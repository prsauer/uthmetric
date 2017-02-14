from django.shortcuts import render
from hellocount.models import Player,Keep,DFalls,MasterEncoder
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.template import Template, Context
from django.template.loader import get_template
from django.utils import timezone

from datetime import datetime
import json, logging, boto3

logger = logging.getLogger('django')

MID_CLASSES = ['Berserker', 'Bonedancer', 'Healer', 'Shadowblade', 'Spiritmaster', 'Shaman', 'Warrior', 'Skald', 'Hunter', 'Savage', 'Thane', 'Runemaster']
HIB_CLASSES = ['Blademaster', 'Ranger', 'Valewalker', 'Eldritch', 'Champion', 'Animist', 'Enchanter', 'Mentalist', 'Bard', 'Warden', 'Hero', 'Nightshade', 'Druid']
ALB_CLASSES = ['Cleric', 'Mercenary', 'Paladin', 'Wizard', 'Infiltrator', 'Necromancer', 'Armsman', 'Scout', 'Sorcerer', 'Theurgist', 'Cabalist', 'Reaver', 'Minstrel', 'Friar']

def most_recent():
	return Player.objects.order_by('-lastupdated').first().lastupdated

def render_to_s3(template):
	enc = MasterEncoder()
	template.render()
	output = template.content

	client = boto3.client('s3')
	client.put_object(
		ACL='public-read',
		Body=output,
		Bucket='uthgard.riftmetric.com',
		Key=template.template_name,
		CacheControl='max-age= 60',
		ContentType='text/html',
	)

	jout = enc.encode(template.context_data)
	client = boto3.client('s3')
	client.put_object(
		ACL='public-read',
		Body=jout,
		Bucket='uthgard.riftmetric.com',
		Key=template.template_name+".json",
		CacheControl='max-age= 60',
		ContentType='text/html',
	)

@csrf_exempt
def update_keep(request):
	jdata = json.loads(request.body)
	try:
		keep = Keep.objects.get_or_create(name=jdata['name'])[0]
		keep.lastupdated = timezone.now()
		keep.owner = jdata.get('owner','Failed')
		keep.leadername = jdata.get('leadername','Failed')
		keep.save()
		render_keeps(request)
	except Exception as e:
		return HttpResponse("%s %s"%(e,e.message))
	return HttpResponse("Good")

@csrf_exempt
def update_df(request):
	jdata = json.loads(request.body)
	try:
		df = DFalls.objects.first()
		df.owner = jdata['owner']
		df.lastupdated = timezone.now()
		df.save()
		render_keeps(request)
	except Exception as e:
		return HttpResponse("%s %s"%(e,e.message))
	return HttpResponse("Good")

def realmwar(request):
	realm_keeps = []
	realm_keeps.append({'realm': 'Albion', 'keeps': Keep.objects.filter(location="Albion").order_by('name')})
	realm_keeps.append({'realm': 'Midgard', 'keeps': Keep.objects.filter(location="Midgard").order_by('name')})
	realm_keeps.append({'realm': 'Hibernia', 'keeps': Keep.objects.filter(location="Hibernia").order_by('name')})
	return TemplateResponse(request, 'realmwar.html', {'realm': 'realmwar',
													   'all_keeps': Keep.objects.all(),
													   'realm_keeps': realm_keeps,
													   'timestamp': most_recent(),
													   'df': DFalls.objects.first()})

def realmwar2(request):
	alb = ["alb"]*7
	mid = ["mid"]*7
	hib = ["hib"]*7

	alb[0] = Keep.objects.get(name="Caer Renaris").owner[0:3].lower()
	alb[1] = Keep.objects.get(name="Caer Berkstead").owner[0:3].lower()
	alb[2] = Keep.objects.get(name="Caer Sursbrooke").owner[0:3].lower()
	alb[3] = Keep.objects.get(name="Caer Boldiam").owner[0:3].lower()
	alb[4] = Keep.objects.get(name="Caer Erasleigh").owner[0:3].lower()
	alb[5] = Keep.objects.get(name="Caer Benowyc").owner[0:3].lower()
	alb[6] = Keep.objects.get(name="Caer Hurbury").owner[0:3].lower()

	mid[0] = Keep.objects.get(name="Arvakr Faste").owner[0:3].lower()
	mid[1] = Keep.objects.get(name="Hlidskialf Faste").owner[0:3].lower()
	mid[2] = Keep.objects.get(name="Glenlock Faste").owner[0:3].lower()
	mid[3] = Keep.objects.get(name="Blendrake Faste").owner[0:3].lower()
	mid[4] = Keep.objects.get(name="Nottmoor Faste").owner[0:3].lower()
	mid[5] = Keep.objects.get(name="Bledmeer Faste").owner[0:3].lower()
	mid[6] = Keep.objects.get(name="Fensalir Faste").owner[0:3].lower()

	hib[0] = Keep.objects.get(name="Dun Scathaig").owner[0:3].lower()
	hib[1] = Keep.objects.get(name="Dun da Behnn").owner[0:3].lower()
	hib[2] = Keep.objects.get(name="Dun na nGed").owner[0:3].lower()
	hib[3] = Keep.objects.get(name="Dun Crimthainn").owner[0:3].lower()
	hib[4] = Keep.objects.get(name="Dun Bolg").owner[0:3].lower()
	hib[5] = Keep.objects.get(name="Dun Crauchon").owner[0:3].lower()
	hib[6] = Keep.objects.get(name="Dun Ailinne").owner[0:3].lower()

	return TemplateResponse(request,'realmwar3.html', {'realm': 'realmwar', 'alb':alb,'hib':hib,'mid':mid})

def render_keeps(request):
	render_to_s3(realmwar2(request))
	render_to_s3(realmwar(request))
	return HttpResponse("Good")

@csrf_exempt
def post_data(request):
	logger.info(request.body)
	jdata = json.loads(request.body)
	jdata = jdata['Item']
	try:
		p = Player.objects.get(rawname=jdata['Raw'].get('Name'))
	except Player.DoesNotExist:
		p = Player()
	p.update_from_json(jdata)
	return HttpResponse("")

@csrf_exempt
def push_name(request, rawname):
	try:
		p = Player.objects.get(rawname=rawname)
		return HttpResponse("Already observed")
	except Player.DoesNotExist:
		try:
			p = Player()
			p.rawname = rawname
			p.refresh_from_uth()
			return HttpResponse("Observing new player... %s"%p.raw_data)
		except Exception as e:
			pass
	return HttpResponse("Error adding player -- Check Uthgard api for name first!")

def by_class(request):
	realms = [[ALB_CLASSES,"Albion"],[HIB_CLASSES,"Hibernia"],[MID_CLASSES,"Midgard"]]
	charts = []
	for r in realms:
		a_data = []
		a_title = "%s Class Distribution (Level 45+, RR 1L6+)"%r[1]
		for a_cls in r[0]:
			a_data.append([a_cls[0:5], Player.objects.filter(classname=a_cls,level__gt=45, rps__gte=1375).count()])
		a_data.sort(key=lambda x: x[1])
		a_data.reverse()
		charts.append({'data': a_data, 'title': a_title, 'element_id': '%s_data'%(r[1].lower())})

	return TemplateResponse(request, 'by_class.html', {'realm': 'classes', 'charts': charts, 'timestamp': most_recent()})

def contrib(request):
	return TemplateResponse(request, 'contrib.html', {'timestamp': most_recent()})

def charts(request):
	context = {'realm': 'Distribution', 'charts': []}
	chart = {
		'data': [], 
		'title': "Albion Distribution by Level",
		"element_id": "albion_data",
	}
	for idx in xrange(1,51,5):
		min_l = idx
		max_l = idx+4
		count = Player.objects.filter(
			realmname='Albion',
			level__gte=min_l,
			level__lte=max_l,
		).count()
		row = "['%s-%s', %s]"%(min_l,max_l,count)
		chart['data'].append(row)
	context['charts'].append(chart)
	
	chart = {
		'data': [], 
		'title': "Hibernia Distribution by Level",
		"element_id": "hibernia_data",
	}
	for idx in xrange(1,51,5):
		min_l = idx
		max_l = idx+4
		count = Player.objects.filter(
			realmname='Hibernia',
			level__gte=min_l,
			level__lte=max_l,
		).count()
		row = "['%s-%s', %s]"%(min_l,max_l,count)
		chart['data'].append(row)
	context['charts'].append(chart)
	
	chart = {
		'data': [], 
		'title': "Midgard Distribution by Level",
		"element_id": "midgard_data",
	}
	for idx in xrange(1,51,5):
		min_l = idx
		max_l = idx+4
		count = Player.objects.filter(
			realmname='Midgard',
			level__gte=min_l,
			level__lte=max_l,
		).count()
		row = "['%s-%s', %s]"%(min_l,max_l,count)
		chart['data'].append(row)
	context['charts'].append(chart)
	context['timestamp'] = most_recent()
	return TemplateResponse(request, 'charts.html', context)

def get_by_name(request, rawname):
	try:
		p = Player.objects.get(rawname=rawname)
		return JsonResponse(json.loads(p.raw_data))
	except Player.DoesNotExist:
		return HttpResponse("Failed %s"%rawname)

def by_guild(request):
	guilds = Player.objects.values('guildname').distinct()
	gdata = []
	for g in [g['guildname'] for g in guilds]:
		if g:
			players = Player.objects.filter(guildname=g)
			this_g = {}
			this_g['guildname'] = g
			this_g['rank'] = 0
			this_g['realmname'] = players.first().realmname
			this_g['rps'] = sum(players.values_list('rps',flat=True))
			this_g['size'] = players.count()
			gdata.append(this_g)
	gdata.sort(key=lambda x: x['rps'])
	gdata.reverse()
	gdata = gdata[0:25]

	for i in xrange(0, len(gdata)):
		gdata[i]['rank'] = i+1

	cdict =  {'timestamp': most_recent(), 'guilds': gdata[0:25], 'realm': 'by Guild'}
	return TemplateResponse(request, 'guilds.html', cdict)

def leaders(request, realm=None):
	if realm is not None and realm not in ["Albion","Midgard","Hibernia"]:
		return HttpResponse("404")
	if not realm:
		db_players = list(Player.objects.all().order_by('-rps')[0:25])
	else:
		db_players = list(Player.objects.all().order_by('-rps').filter(realmname=realm)[0:25])

	fields = ['rawname','classname','guildname','realmname','rps', 'realmrank']
	players = []
	for i in xrange(0, len(db_players)):
		players.append({})
		players[i]['rank'] = i+1
		for f in fields:
			players[i][f] = getattr(db_players[i],f)
		his = db_players[i].history.order_by('-history_date')
		lastrps = 0
		if len(his) > 1:
			lastrps = db_players[i].history.order_by('-history_date')[1].rps or 0
		if lastrps > 0:
			players[i]['delta'] = db_players[i].rps - lastrps
		else:
			players[i]['delta'] = '-'

	cdict =  {'timestamp': most_recent(), 'realm': realm, 'players': players}
	
	return TemplateResponse(request, 'leaders.html', cdict)

def render_leaders(request):
	realms = [("",None),("_alb","Albion"),("_mid","Midgard"),("_hib","Hibernia")]
	for r in realms:
		tr = leaders(request,r[1])
		tr.render()
		output = tr.content

		client = boto3.client('s3')
		client.put_object(
			ACL='public-read',
			Body=output,
			Bucket='uthgard.riftmetric.com',
			Key='leaders%s.html'%r[0],
			CacheControl='max-age= 60',
			ContentType='text/html',
		)

	render_to_s3(by_guild(request))
	# # Render per-guild data
	# tr = by_guild(request)
	# tr.render()
	# output = tr.content
	# 
	# client = boto3.client('s3')
	# client.put_object(
	# 	ACL='public-read',
	# 	Body=output,
	# 	Bucket='uthgard.riftmetric.com',
	# 	Key='guilds.html',
	# 	CacheControl='max-age= 60',
	# 	ContentType='text/html',
	# )

	# Render charts page
	tr = charts(request)
	tr.render()
	output = tr.content

	client = boto3.client('s3')
	client.put_object(
		ACL='public-read',
		Body=output,
		Bucket='uthgard.riftmetric.com',
		Key='charts.html',
		CacheControl='max-age= 60',
		ContentType='text/html',
	)

	# Render class charts page
	tr = by_class(request)
	tr.render()
	output = tr.content

	client = boto3.client('s3')
	client.put_object(
		ACL='public-read',
		Body=output,
		Bucket='uthgard.riftmetric.com',
		Key='classes.html',
		CacheControl='max-age= 60',
		ContentType='text/html',
	)

	# Render contrib page
	tr = contrib(request)
	tr.render()
	output = tr.content

	client = boto3.client('s3')
	client.put_object(
		ACL='public-read',
		Body=output,
		Bucket='uthgard.riftmetric.com',
		Key='contrib.html',
		CacheControl='max-age= 60',
		ContentType='text/html',
	)
	return HttpResponse("")

