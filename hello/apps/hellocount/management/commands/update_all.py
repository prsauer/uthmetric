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
            if p.refresh_from_uth():
                refreshed += 1
            count += 1
            if count%100 == 0:
                print 100.0*count/total
        print "refreshed",refreshed,100.0*refreshed/total
