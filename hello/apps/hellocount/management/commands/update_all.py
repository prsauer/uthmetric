from django.core.management.base import BaseCommand, CommandError
from hellocount.models import Player
import time,requests,json

class Command(BaseCommand):

    def handle(self, *args, **options):
        alldata = requests.get('https://uthgard.org/herald/api/dump')
        jdata = json.loads(alldata.content)
        f = open('output.txt','w')
        f.write(str(jdata))
        f.close()
        for d in jdata:
            print d
            n = d['Name']
            p = Player.objects.get_or_create(rawname=n)
            p.update_from_json(d)
