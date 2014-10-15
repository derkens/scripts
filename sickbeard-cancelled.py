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
pushtitle = "SickBeard - Cancelled"
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
		logger.logging.debug(s)
		if config.use_pushover == 1:
			logger.logging.debug ("Sending Pushover notification...")
			conn = httplib.HTTPSConnection("api.pushover.net:443")
			conn.request("POST", "/1/messages.json",
				urllib.urlencode({
					"token": config.app_token,
					"user": config.user_key,
					"message": show+" is possibly cancelled",
					"title" : 'Sick Beard',
					"device" : config.push_device,
				}), { "Content-type": "application/x-www-form-urlencoded" })
			r = conn.getresponse()
			r = json.loads(r.read())
			if r["status"] == 1 :
				logger.logging.info("Pushover notification sent succesfully")
			else:
				logger.logging.error("Pushover failed with following error" + str(r["errors"]))
		if config.use_nma == 1:
			pushtitle = "SickBeard"
			logger.logging.info ("Sending NMA notification...")
			from lib.pynma import pynma
			p = pynma.PyNMA(config.nma_api)
			res = p.push(config.app, pushtitle, pushmsg, 0, 1, config.nma_priority )
			if res[config.nma_api][u'code'] == u'200':
				logger.logging.info ("NMA Notification succesfully send")
			else:
				error = res[config.nma_api]['message'].encode('ascii')
				logger.logging.error ("NMA Notification failed: " + error)
		if config.use_email == 1:
			text_file.write(show + " is possibly cancelled\n")
			text_file.close()
			logger.logging.info ("Sending Email notification...")
			emailer.SendEmail(pushtitle)
			os.remove("Output.txt")

