import requests,json,logging
from django.db import models
from simple_history.models import HistoricalRecords
from datetime import datetime
from django.utils import timezone
import pytz

logger = logging.getLogger('django')

realms = ["","Albion","Midgard","Hibernia"]

class DFalls(models.Model):
    history = HistoricalRecords()
    owner = models.CharField(max_length=128)
    lastupdated = models.DateTimeField(null=True)
    def to_json(self):
        return {'owner': self.owner, 'lastupdated': self.lastupdated}

class Relic(models.Model):
    history = HistoricalRecords()
    name = models.CharField(max_length=128)
    owner = models.CharField(max_length=128)
    location = models.CharField(max_length=128)
    lastupdated = models.DateTimeField(null=True)
    origin = models.CharField(max_length=128)

class Keep(models.Model):
    history = HistoricalRecords()
    name = models.CharField(max_length=128)
    leadername = models.CharField(max_length=128)
    owner = models.CharField(max_length=128)
    lastupdated = models.DateTimeField(null=True)
    location = models.CharField(max_length=128)

class Player(models.Model):

    history = HistoricalRecords()

    fullname = models.CharField(max_length=128)
    rawname = models.CharField(max_length=128, unique=True)
    classname = models.CharField(max_length=128)
    racename = models.CharField(max_length=128)
    realmrank = models.CharField(max_length=128)
    guildname = models.CharField(max_length=128,null=True)
    realmname = models.CharField(max_length=16,null=True)
    raw_data = models.CharField(max_length=512)
    rps = models.BigIntegerField(null=True)
    xp = models.BigIntegerField(null=True)
    level = models.IntegerField(null=True)
    lastupdated = models.DateTimeField(null=True)

    def age(self):
        return (timezone.now() - self.lastupdated).total_seconds()/60/60

    def redigest(self):
        try:
            self.update_from_json(json.loads(self.raw_data))
        except Exception as e:
            print "Exception on item %s",self.id
            print self.raw_data
            print e,e.message

    def clean_history(self):
        did_work = True
        while(did_work):
            did_work = False
            history_items = list(self.history.order_by('history_date'))
            for i in xrange(1, len(history_items)):
                if history_items[i].raw_data == history_items[i-1].raw_data:
                    history_items[i].delete()
                    did_work = True
                    break

    def update_from_json(self, jdata):
        if json.dumps(jdata) == self.raw_data:
            # Don't save so we dont create duplicate histories
            return False
        try:
            self.fullname = jdata['FullName']
            self.rawname = jdata['Raw'].get('Name')
            self.classname = jdata['ClassName']
            self.racename = jdata['RaceName']
            self.realmrank = jdata['RealmRank']
            self.level = jdata['Level']
            self.guildname = jdata['Raw'].get('GuildName')
            self.realmname = realms[jdata['Raw'].get('Realm',0)]
            self.rps = jdata['Raw'].get('RP',0)
            self.xp = jdata['Raw'].get('XP',0)
            self.lastupdated = pytz.UTC.localize(datetime.fromtimestamp(int(jdata['Raw']['LastUpdated'])))
            self.raw_data = json.dumps(jdata)
        except:
            logger.info("Couldnt decode %s"%(jdata))
        else:
            self.save()
            logger.info("Saved %s"%(jdata))
        return True

    def refresh_from_uth(self):
        req = requests.get('https://uthgard.org/herald/api/player/%s'%self.rawname)
        try:
            return self.update_from_json(json.loads(req.content))
        except ValueError:
            logger.info("Error: %s,%s"%(self.rawname,req.content))
        return False

class MasterEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'to_json'):
            return obj.to_json()
        return json.JSONEncoder.default(self, obj)
