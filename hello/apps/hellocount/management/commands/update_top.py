from django.core.management.base import BaseCommand, CommandError
from hellocount.models import Player
import time

class Command(BaseCommand):

    def handle(self, *args, **options):
        for p in Player.objects.order_by('-rps')[0:150]:
            p.refresh_from_uth()
