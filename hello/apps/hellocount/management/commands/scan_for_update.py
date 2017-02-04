from django.core.management.base import BaseCommand, CommandError
from hellocount.models import Player
import time

class Command(BaseCommand):

    def handle(self, *args, **options):
        blizz = Player.objects.get(rawname="Blizz")
        while(True):
            if blizz.refresh_from_uth():
                print "NEW DATA FOUND !!!!"
                print "NEW DATA FOUND !!!!"
                break
            else:
                print "old"
            time.sleep(5)
