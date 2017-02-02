from django.shortcuts import render
from hellocount.models import Player
from django.views.decorators.csrf import csrf_exempt

import logging
logger = logging.getLogger('django')

@csrf_exempt
def say_hello(request):
	logger.info(request.POST)
	f = open('/srv/output.txt', 'w')
	f.write(str(request.POST))
	f.close()

