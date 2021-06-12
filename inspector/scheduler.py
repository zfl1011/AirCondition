import threading
import time

from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor #线程池，进程池

from .models import Hotel, ServerUnit, WaitQueue, SchedulerLog
from user.models import RoomState, RoomRequest

class Scheduler:
    def __init__(self, unitNum, mode):
        self.isReady = 0 #0停止，1工作
        self.unitNum = unitNum
        self.mode = mode #1制冷，2制热
        self.runThreadSchdule = None
        self.runThreadKeepOrder = None
    def schduling(self):
        thread_pool = ThreadPoolExecutor(3)
        hotel = Hotel.objects.filter(endTime=0)
        print("scheduling...")
        feerate = hotel[0].feeRateL
        backtemp = [0,0,0,0,0]
        if hotel[0].Mode == 2:
            rate = [0.05,0.1,0.2]
        else:
            rate = [-0.05,-0.1,-0.2]
        thread_pool = ThreadPoolExecutor(3)
        while len(hotel) > 0 and hotel[0].isSchedulerRunning == 1:
            print("after 9 seconds")
            # 六个任务，按顺序做 0 把order=0但需要服务的120①state=1或2的是否需要变成3？②state=3的回温 0.075，是否要变成1？
            # ③state==2的 计时 order-9  9秒温度变化，0.15 0.075 0.05
            # ④ state==0但还在排队或正被服务(order!=0),order=0把对应的state。puls的unit叫停(state=0)
            # ⑤安排服务 if新请求request.temp==-1
            #             request.temp=0
            #             if 有空len（state=0）> 0 ：服务
            #             elif 满足风速优先级：叫停(unit.state=0，order=120)，state=2，进池子
            #             else 上一步没被调走，进入时间片 查看提交了几秒了 order=120-int(time-request.time)
            #          elif order==1：换order最小的出来(unit.state=0，order=120)，state=2，进池子
            #          else： iforder-=9>0 order-9,else order = 1
            # 睡9秒。
            needAdd = RoomState.objects.filter(state=1)
            # print("0")
            for r in needAdd:
                posi = WaitQueue.objects.filter(roomID=r.roomID)
                req = RoomRequest.objects.filter(roomID=r.roomID).order_by("-pk")
                posi = posi[0]
                if posi.order == 0 :#or (len(req)>1 and req[1].speed == -1)
                    r.plus = req[0].pk
                    r.save()
                    posi.order = 111
                    posi.save()
                    posi = WaitQueue.objects.filter(roomID=r.roomID)
                    # queueLen += 1
                    print("add r", r.roomID, " at", posi[0].order, "改成120倒计时")
            #①
            needJudge = RoomState.objects.filter(state=1)
            # print("1")
            if len(needJudge) > 0:
                for r in needJudge:
                    req = RoomRequest.objects.filter(roomID=r.roomID).order_by("-pk")
                    target = req[0].targetTemp
                    if (self.mode == 1 and target > r.temp) or (self.mode == 2 and target < r.temp):
                        print(r.roomID,"号房间满足目标")
                        r.state = 3
                    r.save()
            needJudge = RoomState.objects.filter(state=2)
            if len(needJudge) > 0:
                for r in needJudge:
                    req = RoomRequest.objects.filter(roomID=r.roomID).order_by("-pk")
                    target = req[0].targetTemp
                    if (self.mode == 1 and target > r.temp) or (self.mode == 2 and target < r.temp):
                        print("满足目标，停止",r.roomID,"房间 释放服务器",r.plus)
                        r.state = 3
                        unit = ServerUnit.objects.get(name=r.plus)
                        unit.state = 0
                        unit.save()
                        wq = WaitQueue.objects.get(roomID=r.roomID)
                        wq.order = 111
                        wq.save()
                        r.plus = req[0].pk
                        r.save()
            #②
            needJudge = RoomState.objects.filter(state=3)
            # print("2")
            if len(needJudge) > 0 :
                for r in needJudge:
                    req = RoomRequest.objects.filter(roomID=r.roomID).order_by("-pk")
                    target = req[0].targetTemp
                    if (self.mode == 1 and target+1 < r.temp) or (self.mode == 2 and target-1 > r.temp ):
                        wq = WaitQueue.objects.get(roomID=r.roomID)
                        print(r.roomID, "号房间回温到",r.temp,"需要服务, waitqueue",wq.order)
                        r.state = 1
                        r.save()
                        continue
                    print(r.roomID,"号房间回温中",backtemp[r.roomID-1],r.temp)
                    if self.mode == 1:
                        backtemp[r.roomID-1] = round(backtemp[r.roomID-1]+0.15,3)
                    else:
                        backtemp[r.roomID - 1] = round(backtemp[r.roomID - 1] - 0.15, 3)
                    if abs(backtemp[r.roomID-1]) == 0.45:
                        if self.mode == 1:
                            r.temp += 0.5
                        else :
                            r.temp -= 0.5
                        backtemp[r.roomID-1] = 0
                    r.save()
            #③
            needJudge = RoomState.objects.filter(state=2)
            # print("3")
            if len(needJudge) > 0:
                for r in needJudge:
                    wq = WaitQueue.objects.get(roomID=r.roomID)
                    wq.order = wq.order - 9
                    req = RoomRequest.objects.filter(roomID=r.roomID).order_by("-pk")
                    speed = req[0].speed
                    wq.save()
                    r.temp = round(r.temp + rate[speed],3)
                    print(r.roomID,"号房间被服务中")
                    r.save()
            # ④
            needJudge = RoomState.objects.filter(state=0) #requestOff
            # print("4")
            if len(needJudge) > 0:
                for r in needJudge:
                    wq = WaitQueue.objects.get(roomID=r.roomID)
                    if wq.order < 0:
                        unitID = r.plus
                        # print("unitID",unitID)
                        unit = ServerUnit.objects.filter(name=unitID)
                        if len(unit) == 0:
                            continue
                        unit = ServerUnit.objects.get(name=unitID)
                        unit.state = 0
                        unit.save()
                    wq.order = 0
                    wq.save()
                    r.save()
            # ⑤安排服务
            # if新请求request.temp == -1
            #             request.temp=0
            #             if 有空len（state=0）> 0 ：服务
            #             elif 满足风速优先级：叫停(unit.state=0，order=120)，state=2，进池子
            #             else 上一步没被调走，进入时间片 查看提交了几秒了 order=120-int(time-request.time)
            #          elif order==1：换order最小的出来(unit.state=0，order=120)，state=2，进池子
            #          else： iforder-=9>0 order-9,else order = 1
            needJudge = RoomState.objects.filter(state=1)
            # print("5")
            if len(needJudge) > 0:
                # print("in1")
                for r in needJudge:
                    # print("in2")
                    req = RoomRequest.objects.filter(roomID=r.roomID).order_by("-pk")
                    req = req[0]
                    if req.temp == -1:
                        # print("in3")
                        req.temp = 0
                        req0speed = req.speed
                        req0time = int(req.time)
                        req.save()
                        unit = ServerUnit.objects.filter(state=0)
                        if len(unit) >0 :
                            u = unit[0]
                            u.state = 1
                            u.save()
                            print("第一次且空let unit", u.name, " serve", r.roomID)
                            rq = r.plus
                            r.state = 2
                            r.plus = u.name
                            r.save()
                            timeslip = int(time.time()) - req0time
                            wq = WaitQueue.objects.get(roomID=r.roomID)
                            wq.order = 0 - timeslip
                            wq.save()
                            thread_pool.submit(serveSimulate, u.name, r.roomID, r.temp, rq, feerate)
                        else:
                            #TODO
                            print("无空，寻找优先级可替换的位置")
                            isServing = RoomState.objects.filter(state=2)
                            posi = [[-1, req0speed, 0, -1]]  # 房间号，风速，服务时长 unitname
                            for ring in isServing:
                                reqing = RoomRequest.objects.filter(roomID=ring.roomID).order_by("-pk")
                                posi.append([ring.roomID, reqing[0].speed, ring.time, ring.plus])
                            bigger = []  # 风速小的
                            lowestcount = []  # 风速最小的
                            basespeed = req0speed
                            for ring in posi:
                                if ring[1] <= req0speed:
                                    continue
                                elif ring[1] > basespeed:
                                    lowestcount = [ring[0]]
                                    basespeed = ring[1]
                                    bigger.append(ring[0])
                                elif  ring[1] == basespeed:
                                    lowestcount.append(ring[0])
                                    bigger.append(ring[0])
                            print("lowestcountl",lowestcount,"bigger",bigger)
                            # 下方if 优先级失效，走时间片 对应2.2、2.3
                            if len(bigger) == 0:
                                print("优先级失效，走时间片 对应2.2、2.3")
                                timeslip = int(time.time()) - req0time
                                wq = WaitQueue.objects.get(roomID=r.roomID)
                                if wq.order == 0:
                                    wq.order = 120 - timeslip
                                    wq.save()
                            # 下方elif对应2.1.1和2.1.3
                            elif len(bigger) == 1 or len(lowestcount) == 1:
                                if len(bigger) == 1:
                                    changer = RoomState.objects.get(roomID=bigger[0])
                                else:
                                    changer = RoomState.objects.get(roomID=lowestcount[0])
                                changer.state = 1
                                unitID = changer.plus
                                changeq = RoomRequest.objects.filter(roomID=changer.roomID).order_by("-pk")
                                changer.plus = changeq[0].pk
                                changer.save()
                                wq = WaitQueue.objects.get(roomID=changer.roomID)
                                wq.order = 111
                                wq.save()
                                changeu = ServerUnit.objects.get(name=unitID)
                                changeu.state = 0
                                changeu.save()
                                print("根据2.1.1或2.1.3：let unit", u.name, " serve", r.roomID)
                                r.state = 2
                                rpk = r.plus
                                r.plus = changeu.name
                                r.save()
                                timeslip = int(time.time()) - req0time
                                wq = WaitQueue.objects.get(roomID=r.roomID)
                                wq.order = -9
                                wq.save()
                                thread_pool.submit(serveSimulate, changeu.name, r.roomID, r.temp, rpk, feerate)
                            # 下方elif对应2.1.2
                            elif len(lowestcount) > 1:
                                basetime = 0
                                changer = -1
                                for ring in lowestcount:
                                    wq = WaitQueue.objects.get(roomID=ring)
                                    print("房间",ring,"已服务",-wq.order)
                                    if wq.order < basetime:
                                        changer = ring
                                        basetime = wq.order
                                if changer == -1:#怎么可能
                                    continue
                                changer = RoomState.objects.get(roomID=changer)
                                changer.state = 1
                                unitID = changer.plus
                                changeq = RoomRequest.objects.filter(roomID=changer.roomID).order_by("-pk")
                                changer.plus = changeq[0].pk
                                changer.save()
                                wq = WaitQueue.objects.get(roomID=changer.roomID)
                                wq.order = 111
                                wq.save()
                                changeu = ServerUnit.objects.get(name=unitID)
                                changeu.state = 0
                                changeu.save()
                                print("根据2.1.2：let unit", u.name, " serve", r.roomID)
                                r.state = 2
                                rpk = r.plus
                                r.plus = changeu.name
                                r.save()
                                timeslip = int(time.time()) - req0time
                                wq = WaitQueue.objects.get(roomID=r.roomID)
                                wq.order = -9
                                wq.save()
                                thread_pool.submit(serveSimulate, changeu.name, r.roomID, r.temp, rpk, feerate)
                                time.sleep(1)
                    else:
                        wq = WaitQueue.objects.get(roomID=r.roomID)
                        unit = ServerUnit.objects.filter(state=0)
                        if len(unit) > 0 and r.state == 1:
                            print("有空服务器")
                            waitwq = WaitQueue.objects.filter(order__gt=0).order_by("order")
                            if (len(waitwq) == 1 and waitwq[0].roomID==r.roomID) or (len(waitwq) > 1 and waitwq[0].roomID==r.roomID):
                                u = unit[0]
                                if u.state == 0:
                                    u.state=1
                                else:
                                    break
                                u.save()
                                wq.order = -9
                                wq.save()
                                r.state = 2
                                rq = RoomRequest.objects.filter(roomID=r.roomID).last().pk
                                r.plus = u.name
                                r.save()
                                print("let unit", u.name, " serve", r.roomID,"rq",rq)
                                thread_pool.submit(serveSimulate, u.name, r.roomID, r.temp, rq, feerate)
                        elif wq.order == 1 :
                            ring = RoomState.objects.filter(state=2)
                            basetime = 0
                            changer = -1
                            for r2 in ring:
                                wq = WaitQueue.objects.get(roomID=r2.roomID)
                                if wq.order < basetime:
                                    changer = r2.roomID
                                    basetime = wq.order
                            if changer == -1:
                                continue
                            changer = RoomState.objects.get(roomID=changer)
                            changer.state = 1
                            unitID = changer.plus
                            changeq = RoomRequest.objects.filter(roomID=changer.roomID).order_by("-pk")
                            changer.plus = changeq[0].pk
                            changer.save()
                            wq = WaitQueue.objects.get(roomID=changer.roomID)
                            wq.order = 111
                            wq.save()
                            changeu = ServerUnit.objects.get(name=unitID)
                            changeu.state = 1
                            changeu.save()
                            print("根据时间片：let unit", u.name, " serve", r.roomID)
                            r.state = 2
                            rpk = r.plus
                            r.plus = changeu.name
                            r.save()
                            thread_pool.submit(serveSimulate, changeu.name, r.roomID, r.temp, rpk, feerate)
                        else :
                            print(r.roomID,"号房间等待倒计时",wq.order)
                            if wq.order > 10:
                                wq.order = wq.order - 9
                            else:
                                wq.order = 1
                            wq.save()
            time.sleep(9)
            hotel = Hotel.objects.filter(endTime=0)


def serveSimulate(unitID, roomID, stemp, rpk, feerate):
    st = time.time()
    tmp = ServerUnit.objects.filter(name=unitID)
    unit = tmp[0]
    unit.state=1
    unit.save()
    count = 0
    r = RoomState.objects.get(roomID=roomID)
    rf=r.fee
    rp=r.power
    while unit.state == 1 and r.state == 2:
        time.sleep(1)
        tmp = ServerUnit.objects.filter(name=unitID)
        r = RoomState.objects.get(roomID=roomID)
        rr=RoomRequest.objects.filter(roomID=roomID).last()
        unit = tmp[0]
        count += 1
        if count % 5 == 0:
            print(time.asctime(time.localtime(time.time())), "unit ", unit.name, " is serving room", roomID)
            # TODO 计费
            if rr.speed == 1:
                change = 5 / 60
            elif rr.speed == 2:
                change = (5 / 60) * 1.2
            elif rr.speed == 0:
                change = (5 / 60) * 0.8
            fee = round(change * feerate, 2)
            power=round(change,2)
            r.fee = r.fee + fee
            r.power=r.power+change
            r.save()

    r = RoomState.objects.get(roomID=roomID)
    dur=r.fee-rf
    durp=r.power-rp
    # TODO  scheduleLog
    sl = SchedulerLog.objects.create(serverID=unit.name, roomID=roomID, requestID=rpk, startTime=st, endTime=time.time(), fee=dur,power=durp)
    sl.save()
    print("unit ", unit.name, " serve over",roomID,time.asctime(time.localtime(time.time())))
    if r.state == 2:
        r.state = 1
    r.fee = r.fee + fee
    r.save()
    tmp = ServerUnit.objects.filter(name=unitID)
    unit = tmp[0]
    if unit.state != 0 and r.plus != unitID:
        unit.state = 0
        unit.save()
    # 线程 循环roomState被服务+温度降+计费这个计费在结算后清空、增scheduleLog、