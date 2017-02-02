from django.shortcuts import render
#from hellocount.models import Visit
from hellocount.models import Player

import logging
logger = logging.getLogger('django')

def say_hello(request):
	logger.info(request.POST)

