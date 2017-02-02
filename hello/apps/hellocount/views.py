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

def leaders(request, realm=None):
	if realm is not None and realm not in ["Albion","Midgard","Hibernia"]:
		return HttpResponse("404")
	if not realm:
		players = Player.objects.all().order_by('-rps')[0:10].values()
	else:
		players = Player.objects.all().order_by('-rps').filter(realmname=realm)[0:10].values()

	cdict =  {'realm': realm, 'players': players}

	t = get_template('leaders.html')
	c = Context(cdict)

	client = boto3.client('s3')
	client.put_object(
		ACL='public-read',
		Body=t.render(c),
		Bucket='uthgard.riftmetric.com',
		Key='leaders_test.html',
		CacheControl='max-age= 60',
		ContentType='text/html',
	)
	return TemplateResponse(request, 'leaders.html', cdict)

@csrf_exempt
def get_by_name(request, rawname):
	try:
		p = Player.objects.get(rawname=rawname)
		return JsonResponse(json.loads(p.raw_data))
	except Player.DoesNotExist:
		return HttpResponse("Failed %s"%rawname)
