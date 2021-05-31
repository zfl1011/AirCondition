from inspector.models import Hotel, WaitQueue, ServerUnit
from user.models import RoomState
import time


def hotelOn():
    hotel = Hotel.objects.filter(endTime=0)
    if len(hotel) == 0:
        return False
    elif len(hotel) > 1:
        for h in hotel:
            print(h.startTime)
            h.endTime = time.time()
            h.save()
        return False
    else:
        return True


def helpLog():
    wq = WaitQueue.objects.all()
    data = open("wqlog.txt", 'a')
    print(time.asctime(time.localtime(time.time())), file=data)
    for w in wq:
        print(w.roomID, w.order, file=data)
    data.close()

    rs = RoomState.objects.all()
    data = open("rslog.txt", 'a')
    print(time.asctime(time.localtime(time.time())), file=data)
    for r in rs:
        print(r.roomID, r.state, r.temp, r.fee, r.plus, file=data)
    data.close()

    su = ServerUnit.objects.all()
    data = open("sulog.txt", 'a')
    print(time.asctime(time.localtime(time.time())), file=data)
    for u in su:
        print(u.name, u.state, file=data)
    data.close()
