# Generated by Django 3.0.6 on 2020-06-13 19:16

from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='report',
            managers=[
                ('object', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterField(
            model_name='report',
            name='date',
            field=models.CharField(default=0, max_length=100),
        ),
    ]
