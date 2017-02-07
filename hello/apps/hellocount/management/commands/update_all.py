from django.core.management.base import BaseCommand, CommandError
from hellocount.models import Player
import time

class Command(BaseCommand):

    def handle(self, *args, **options):
        total = Player.objects.all().count()
        print "Updating",total,"characters"
        count = 0
        refreshed = 0
        for p in Player.objects.order_by('-rps'):
            count += 1
            if count%100 == 0:
                print 100.0*count/total
            if p.age() < 6:
                continue
            if p.level < 20 and p.age() < 24:
                continue
            if p.level < 40 and p.age() < 12:
                continue
            if p.refresh_from_uth():
                refreshed += 1
        print "refreshed",refreshed,100.0*refreshed/total
