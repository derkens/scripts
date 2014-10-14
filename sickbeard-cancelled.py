#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#<derkens@gmail.com>
#show cancelled? this script notifies you and put the show in 'pause' (after the last ep oc.)
#
# shamelessly incorporated stuff from Sick Beard AutoProcessTV
# Author: Nic Wolfe <nic@wolfeden.ca>
# URL: http://code.google.com/p/sickbeard/

import os.path
import sys
import httplib, urllib, urllib2, json
import lib.logger.logger as logger
import lib.config as config
import lib.emailer as emailer

if config.ssl:
	protocol = "https://"
else:
	protocol = "http://"

if config.use_email == 1:
	text_file = open("Output.txt", "w")

url = protocol + config.host + ":" + config.port + config.web_root + "api/" + config.api_key + "/?"

logger.logging.info ("Opening URL: " + url)

params = config.urlencode({'cmd': 'shows', 'sort': 'name', 'paused': '0'})
t = urllib2.urlopen(url, params).read()
t = json.loads(t)
logger.logging.debug(t)
end = filter( lambda x: x['status']=='Ended', t['data'].values() )
logger.logging.debug(end)
if end == []:
	logger.logging.info("Nothing to be done, exiting")
	exit()
for i in end :
	show = i['show_name'] ; logger.logging.debug("Showname = " + show)
	stat = i['status'] ; logger.logging.debug("Show status = " + stat)
	net = i['next_ep_airdate'] ; logger.logging.debug("Next episode date = " + net)
	if net == '':
		params = config.urlencode({'cmd': 'sb.searchtvdb', 'lang': 'nl', 'name': show})
		r = urllib2.urlopen(url, params).read()
		r = json.loads(r)
		logger.logging.debug(r)
		tvdbid = str(r['data']['results'][0]['tvdbid'])
		logger.logging.debug(tvdbid)
		params = config.urlencode({'cmd': 'show.pause', 'tvdbid': tvdbid, 'pause': 1})
		s = urllib2.urlopen(url, params).read()
		logging.debug(s)
		if config.use_pushover == 1:
			logger.logging.info ("Sending Pushover notification...")
			conn = httplib.HTTPSConnection("api.pushover.net:443")
			conn.request("POST", "/1/messages.json",
				urllib.urlencode({
					"token": config.app_token,
					"user": config.user_key,
					"message": show+msgsuffix,
					"title" : 'Sick Beard',
				}), { "Content-type": "application/x-www-form-urlencoded" })
			conn.getresponse()
		if use_nma == 1:
			logger.logging.info ("Sending NMA notification...")
			from lib.pynma import pynma
			p = pynma.PyNMA(config.nma_api)
			p.push(config.app, show+msgsuffix, show+msgsuffix, 0, 1, config.nma_priority )


