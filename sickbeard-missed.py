#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#<derkens@gmail.com>
#Notifies you if there are any 'missed' episodes
#
# shamelessly incorporated stuff from Sick Beard AutoProcessTV
# Author: Nic Wolfe <nic@wolfeden.ca>
# URL: http://code.google.com/p/sickbeard/

import os.path
import sys
import httplib, urllib, urllib2, json
import lib.logger.logger as logger
import lib.config as config

if ssl:
	protocol = "https://"
else:
	protocol = "http://"

url = protocol + host + ":" + port + web_root + "api/" + api_key + "/?"

logger.logging.info ("Opening URL: " + url)

params = urlencode({ 'cmd': 'future', 'type': 'missed' })
t = urllib2.urlopen(url, params).read()
t = json.loads(t)
logger.logging.debug(t)
mis= list(t['data']['missed'])
logger.logging.debug(mis)
if mis == "[]" :
	logger.logging.info("Nothing to be done, exiting")
	exit()


else:
	for index, string in enumerate(mis):
		show = str(mis[index]['show_name']) ; logger.logging.debug("show = " + show)
		seas = str(mis[index]['season']) ; logger.logging.debug("season = " + seas)
		epis = str(mis[index]['episode']) ; logger.logging.debug("episode = " + epis)
		epname = str(mis[index]['ep_name']) ; logger.logging.debug("episode name = " + epname)
		pushtitle = 'Sick Beard - gemist'
		pushmsg = '!'+show+' '+seas+'x'+epis+' '+epname
		logger.logging.debug("Dumping pushmsg for debug " + pushmsg)
		if config.use_pushover == 1:
			logger.logging.info ("Sending Pushover notification...")
			conn = httplib.HTTPSConnection("api.pushover.net:443")
			conn.request("POST", "/1/messages.json",
				urllib.urlencode({
					"token": app_token,
					"user": user_key,
					"message": pushmsg,
					"title" : pushtitle,
				}), { "Content-type": "application/x-www-form-urlencoded" })
			conn.getresponse()
		if config.use_nma == 1:
			logger.logging.info ("Sending NMA notification...")
			from lib.pynma import pynma
			p = pynma.PyNMA(nma_api)
			p.push(app, pushtitle, pushmsg, 0, 1, nma_priority )
