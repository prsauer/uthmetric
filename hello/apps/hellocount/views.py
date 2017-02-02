from django.shortcuts import render
from hellocount.models import Player
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.template import Template, Context
from django.template.loader import get_template

import json, logging, boto3

logger = logging.getLogger('django')

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

def charts(request):
	return TemplateResponse(request, 'charts.html', {'data_rows': ["['0-5', 250]","['6-10', 11]"]})

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

	cdict =  {'guilds': gdata[0:25], 'realm': 'by Guild'}
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

	cdict =  {'realm': realm, 'players': players}
	
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
			CacheControl='max-age= 1',
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
		CacheControl='max-age= 1',
		ContentType='text/html',
	)
	return HttpResponse("")

