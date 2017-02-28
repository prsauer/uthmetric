import requests,json,logging
from django.db import models
from simple_history.models import HistoricalRecords
from datetime import datetime
from datetime import timedelta
from django.utils import timezone
import pytz

logger = logging.getLogger('django')

realms = {"ALBION": "Albion", "MIDGARD": "Midgard", "HIBERNIA": "Hibernia"}

class CustomQuerySetManager(models.Manager):
    """A re-usable Manager to access a custom QuerySet"""
    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            # don't delegate internal methods to the queryset
            if attr.startswith('__') and attr.endswith('__'):
                raise
            return getattr(self.get_query_set(), attr, *args)

    def get_query_set(self):
        return self.model.QuerySet(self.model, using=self._db)

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
    objects = CustomQuerySetManager()
    history = HistoricalRecords()
    name = models.CharField(max_length=128)
    leadername = models.CharField(max_length=128)
    owner = models.CharField(max_length=128)
    lastupdated = models.DateTimeField(null=True)
    location = models.CharField(max_length=128)
    def to_json(self):
        return {'name': self.name,
                'leadername': self.leadername,
                'owner': self.owner,
                'lastupdated': self.lastupdated,
                'location': self.location,
                }

class Player(models.Model):

    history = HistoricalRecords()

    fullname = models.CharField(max_length=128)
    rawname = models.CharField(max_length=128, unique=True)
    classname = models.CharField(max_length=128,db_index=True)
    racename = models.CharField(max_length=128,db_index=True)
    realmrank = models.CharField(max_length=128)
    guildname = models.CharField(max_length=128,null=True,db_index=True)
    realmname = models.CharField(max_length=16,null=True,db_index=True)
    raw_data = models.CharField(max_length=512)
    rps = models.BigIntegerField(null=True,db_index=True)
    xp = models.BigIntegerField(null=True)
    level = models.IntegerField(null=True,db_index=True)
    lastupdated = models.DateTimeField(null=True)

    rps_last7 = models.BigIntegerField(null=True,db_index=True)

    def to_json(self):
        return {'fullname': self.fullname,
                'rawname': self.rawname,
                'classname': self.classname,
                'racename': self.racename,
                'realmrank': "%sL%s"%(self.realmrank[0:len(self.realmrank)-1],self.realmrank[len(self.realmrank)-1]),
                'guildname': self.guildname,
                'realmname': self.realmname,
                'rps': self.rps,
                'xp': self.xp,
                'level': self.level,
                'lastupdated': self.lastupdated,
                'rps_last7': self.rps_last7,
                }

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
            self.fullname = jdata['Name']
            self.rawname = jdata['Name']
            self.classname = jdata['Class']
            self.racename = jdata['Race']
            self.realmrank = jdata['RealmRank']
            self.level = jdata['Level']
            self.guildname = jdata['Guild']
            self.realmname = realms[jdata['Realm']]
            self.rps = jdata['Rp']
            self.xp = jdata['Xp']
            self.lastupdated = pytz.UTC.localize(datetime.fromtimestamp(int(jdata['LastUpdated'])))
            self.raw_data = json.dumps(jdata)

            try:
                seven_ago = timezone.now() - timedelta(days=7)
                self.rps_last7 = self.rps - self.history.as_of(seven_ago).rps
            except:
                logger.info("History decode failed %s"%(jdata))
        except:
            logger.info("Couldnt decode %s"%(jdata))
        else:
            self.save()
            logger.info("Saved %s"%(jdata))
        return True

    def refresh_from_uth(self):
        req = requests.get('https://www2.uthgard.net/herald/api/player/%s'%self.rawname)
        try:
            return self.update_from_json(json.loads(req.content))
        except ValueError:
            logger.info("Error: %s,%s"%(self.rawname,req.content))
        return False

class MasterEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj,datetime):
            return str(obj)
        if hasattr(obj, 'to_json'):
            return obj.to_json()
        if obj.__class__.__name__ == 'QuerySet':
            return [i.to_json() for i in obj]
        return json.JSONEncoder.default(self, obj)
