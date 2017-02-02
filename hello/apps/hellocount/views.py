from django.shortcuts import render
from hellocount.models import Player
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json

import logging
logger = logging.getLogger('django')

@csrf_exempt
def say_hello(request):
	logger.info(request.body)
	jdata = json.loads(request.body)
	jdata = jdata['Item']
	try:
		p = Player.objects.get(rawname=jdata['Raw'].get('Name'))
	except Player.DoesNotExist:
		p = Player()
	p.update_from_json(request.body)
	return HttpResponse("")
