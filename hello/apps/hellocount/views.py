from django.shortcuts import render
from hellocount.models import Player
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

import logging
logger = logging.getLogger('django')

@csrf_exempt
def say_hello(request):
	logger.info(request.POST)
	return HttpResponse("")
