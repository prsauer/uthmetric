import requests,json,logging
from django.db import models
from simple_history.models import HistoricalRecords

logger = logging.getLogger('django')

realms = ["","Albion","Midgard","Hibernia"]

class Player(models.Model):
    self.rank = 0

    history = HistoricalRecords()

    fullname = models.CharField(max_length=128)
    rawname = models.CharField(max_length=128, unique=True)
    classname = models.CharField(max_length=128)
    racename = models.CharField(max_length=128)
    realmrank = models.CharField(max_length=128)
    guildname = models.CharField(max_length=128)
    realmname = models.CharField(max_length=16,null=True)
    raw_data = models.CharField(max_length=512)
    rps = models.BigIntegerField(null=True)
    xp = models.BigIntegerField(null=True)

    def redigest(self):
        try:
            self.update_from_json(json.loads(self.raw_data))
        except Exception as e:
            print "Exception on item %s",self.id
            print self.raw_data
            print e,e.message

    def update_from_json(self, jdata):
        try:
            self.fullname = jdata['FullName']
            self.rawname = jdata['Raw'].get('Name')
            self.classname = jdata['ClassName']
            self.racename = jdata['RaceName']
            self.realmrank = jdata['RealmRank']
            self.guildname = jdata['Raw'].get('GuildName')
            self.realmname = realms[jdata['Raw'].get('Realm',0)]
            self.rps = jdata['Raw'].get('RP',0)
            self.xp = jdata['Raw'].get('XP',0)
            self.raw_data = json.dumps(jdata)
        except:
            logger.info("Couldnt decode %s"%(jdata))
        else:
            self.save()
            logger.info("Saved %s"%(jdata))

    def refresh_from_uth(self):
        req = requests.get('https://uthgard.org/herald/api/player/%s'%self.rawname)
        self.update_from_json(json.loads(req.content))

