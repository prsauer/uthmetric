from django.core.management.base import BaseCommand, CommandError
from hellocount.models import Player
import time,requests,json

class Command(BaseCommand):

    def handle(self, *args, **options):
        alldata = requests.get('https://www2.uthgard.net/herald/api/dump')
        jdata = json.loads(alldata.content)
        for k in jdata.keys():
            d = jdata[k]
            n = d['Name']
            p = Player.objects.get_or_create(rawname=n)[0]
            p.update_from_json(d)

        all_players = list(Player.objects.filter(rps__gt=0).order_by('-rps'))
        for i in xrange(0,len(all_players)):
            all_players[i].global_rank = i + 1
            all_players[i].save()
