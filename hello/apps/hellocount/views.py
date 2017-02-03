from django.shortcuts import render
from hellocount.models import Player
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.template import Template, Context
from django.template.loader import get_template

from datetime import datetime
import json, logging, boto3

logger = logging.getLogger('django')

def most_recent():
	return Player.objects.order_by('-lastupdated').first().lastupdated

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

def contrib(request):
	return TemplateResponse(request, 'contrib.html', {})

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

	# Render per-guild data
	tr = by_guild(request)
	tr.render()
	output = tr.content

	client = boto3.client('s3')
	client.put_object(
		ACL='public-read',
		Body=output,
		Bucket='uthgard.riftmetric.com',
		Key='guilds.html',
		CacheControl='max-age= 60',
		ContentType='text/html',
	)

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

