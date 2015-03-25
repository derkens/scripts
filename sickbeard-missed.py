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
import lib.emailer as emailer
import base64

if config.ssl:
	protocol = "https://"
else:
	protocol = "http://"

if config.use_email == 1:
	text_file = open("Output.txt", "w")

url = protocol + config.host + ":" + config.port + config.web_root + "api/" + config.api_key + "/?"

logger.logging.info ("Opening URL: " + url)

params = config.urlencode({ 'cmd': 'future', 'type': 'missed' })
t = urllib2.urlopen(url, params).read()
t = json.loads(t)
logger.logging.debug(t)
mis= list(t['data']['missed'])
logger.logging.debug(mis)
if str(mis) == "[]" :
	logger.logging.info("Nothing to be done, exiting")
	exit()


else:
	for index, string in enumerate(mis):
		show = str(mis[index]['show_name']) ; logger.logging.debug("show = " + show)
		seas = str(mis[index]['season']) ; logger.logging.debug("season = " + seas)
		epis = str(mis[index]['episode']) ; logger.logging.debug("episode = " + epis)
		epname = str(mis[index]['ep_name']) ; logger.logging.debug("episode name = " + epname)
		pushtitle = '! '+show
		pushmsg = seas+'x'+epis+' '+epname
		logger.logging.debug("Dumping pushmsg for debug " + pushmsg)
		if config.use_pushover == 1:
			logger.logging.debug ("Sending Pushover notification...")
			conn = httplib.HTTPSConnection("api.pushover.net:443")
			conn.request("POST", "/1/messages.json",
				urllib.urlencode({
					"token": config.app_token,
					"user": config.user_key,
					"message": pushmsg,
					"title" : pushtitle,
					"device" : config.push_device,
				}), { "Content-type": "application/x-www-form-urlencoded" })
			r = conn.getresponse()
			r = json.loads(r.read())
			if r["status"] == 1 :
				logger.logging.info("Pushover notification sent succesfully")
			else:
				logger.logging.error("Pushover failed with following error" + str(r["errors"]))
		if config.use_nma == 1:
			logger.logging.info ("Sending NMA notification...")
			from lib.pynma import pynma
			p = pynma.PyNMA(config.nma_api)
			res = p.push(config.app, pushtitle, pushmsg, 0, 1, config.nma_priority )
			if res[config.nma_api][u'code'] == u'200':
				logger.logging.info ("NMA Notification succesfully send")
			else:
				error = res[config.nma_api]['message'].encode('ascii')
				logger.logging.error ("NMA Notification failed: " + error)
		if config.use_pushbullet == 1:
			data = urllib.urlencode({
				'type': 'note',
				'title': pushtitle,
				'body': pushmsg,
				'device_id': config.deviceid,
				'channel_tag': config.channeltag
				})
			auth = base64.encodestring('%s:' % config.ptoken).replace('\n', '')
			req = urllib2.Request('https://api.pushbullet.com/v2/pushes', data)
			req.add_header('Authorization', 'Basic %s' % auth)
			response = urllib2.urlopen(req)
			res = json.load(response)
			if 'error' in res:
				logger.logging.info ("Pushbullet notification failed")
			else:
				logger.logging.error ("Pushbullet notification sent succesfully")
		if config.use_email == 1:
			text_file.write(pushmsg + "\n")

	else:
		if config.use_email == 1:
			text_file.close()
			logger.logging.info ("Sending Email notification...")
			emailer.SendEmail(pushtitle)
			os.remove("Output.txt")
