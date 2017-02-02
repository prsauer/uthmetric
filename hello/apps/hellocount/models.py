import requests,json,logging
from django.db import models
from simple_history.models import HistoricalRecords

logger = logging.getLogger('django')

realms = ["","Albion","Midgard","Hibernia"]

class Player(models.Model):
    history = HistoricalRecords()

    fullname = models.CharField(max_length=128)
    rawname = models.CharField(max_length=128)
    classname = models.CharField(max_length=128)
    racename = models.CharField(max_length=128)
    realmrank = models.CharField(max_length=128)
    guildname = models.CharField(max_length=128)
    realmname = models.CharField(max_length=16,null=True)
    raw_data = models.CharField(max_length=512)

    def update_from_json(self, res):
        try:
            jdata = json.loads(res)
            self.fullname = jdata['FullName']
            self.rawname = jdata['Raw'].get('Name')
            self.classname = jdata['ClassName']
            self.racename = jdata['RaceName']
            self.realmrank = jdata['RealmRank']
            self.guildname = jdata['Raw'].get('GuildName')
            self.realmname = realms[jdata['Raw'].get('Realm',0)]
            self.raw_data = res
        except:
            logger.error("Couldnt decode %s"%(res))
        else:
            self.save()

    def refresh_from_uth(self):
        req = requests.get('https://uthgard.org/herald/api/player/%s'%self.rawname)
        self.update_from_json(req.content)

