from django.shortcuts import render
from hellocount.models import Player
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse

import json, logging

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
		players = Player.objects.all()[0:10].values()
	else:
		players = Player.objects.filter(realmname=realm)[0:10].values()
	return TemplateResponse(request, 'leaders.html', {'players': players})

@csrf_exempt
def get_by_name(request, rawname):
	try:
		p = Player.objects.get(rawname=rawname)
		return JsonResponse(json.loads(p.raw_data))
	except Player.DoesNotExist:
		return HttpResponse("Failed %s"%rawname)
