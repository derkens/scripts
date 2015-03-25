#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#<derkens@gmail.com>
#When a download failes in Sabnzbd (or Nzbget for that matter) the episode status remaines 'snatched' indefinitly.
#This script will put the status back to 'wanted'
#Put this in your cron to run daily (or systemd timer) and forget
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

url = protocol + config.host + ":" + config.port + config.web_root + "api/" + config.api_key + "/?"

logger.logging.info ("Opening URL: " + url)
params = config.urlencode({ 'cmd': 'history', 'type': 'downloaded', 'limit': 20 })
t = urllib2.urlopen(url, params).read()
t = json.loads(t)
down = list(t['data'])
logger.logging.debug (down)
params = config.urlencode({ 'cmd': 'history', 'type': 'snatched', 'limit': 20 })
u = urllib2.urlopen(url, params).read()
u = json.loads(u)
snat = list(u['data'])
logger.logging.debug(snat)

y = []
z = []

for index, string in enumerate(down):
	down2 = str(down[index]['show_name'])+'_'+str(down[index]['season'])+'_'+str(down[index]['episode'])+'_'+str(down[index]['tvdbid'])
	y.append(down2)

for index, string in enumerate(snat):
	snat2 = str(snat[index]['show_name'])+'_'+str(snat[index]['season'])+'_'+str(snat[index]['episode'])+'_'+str(snat[index]['tvdbid'])
	z.append(snat2)

onlysnat = list(set(z) - set(y))
logger.logging.debug("onlysnat: " + str(onlysnat))
if config.use_email == 1:
	text_file = open("Output.txt", "w+")
for index, string in enumerate(onlysnat):
	temp1 = str(onlysnat[index])
	temp2 = temp1.rsplit('_')
	showname = str(temp2[0]) ; logger.logging.debug("showname: " + showname)
	season = str(temp2[1]) ; logger.logging.debug("season: " + season)
	epis = str(temp2[2]) ; logger.logging.debug("episode: " + epis)
	tvdbid = str(temp2[3]) ; logger.logging.debug("tvdbid: " + tvdbid)
	params = urllib.urlencode({'cmd': 'episode', 'tvdbid': tvdbid, 'season': season, 'episode': epis, })
	w = urllib2.urlopen(url, params).read()
	w = json.loads(w)
	epstatus = str(w['data']['status'])
	epname = str(w['data']['name'])
	if epstatus != "Snatched":
		pass
	else:
		params = urllib.urlencode({'cmd': 'episode.setstatus', 'tvdbid': tvdbid, 'season': season, 'episode': epis, 'status': 'wanted' })
		q = urllib2.urlopen(url, params).read()
		q = json.loads(q) ; logger.logging.debug(q)
		message = season+'x'+epis+' '+epname+' is op wanted gezet.'
		logger.logging.info (message)
		pushtitle = show
		if config.use_pushover == 1:
			logger.logging.debug ("Sending Pushover notification...")
			conn = httplib.HTTPSConnection("api.pushover.net:443")
			conn.request("POST", "/1/messages.json",
				urllib.urlencode({
					"token": config.app_token,
					"user": config.user_key,
					"message": message,
					"title" : pushtitle,
					"push_device" : config.push_device,
				}), { "Content-type": "application/x-www-form-urlencoded" })
			r = conn.getresponse()
			r = json.loads(r.read())
			if r["status"] == 1 :
				logger.logging.info("Pushover notification sent succesfully")
			else:
				logger.logging.error("Pushover failed with following error" + str(r["errors"]))
		if config.use_nma == 1:
			logger.logging.debug ("Sending NMA notification...")
			from lib.pynma import pynma
			p = pynma.PyNMA(config.nma_api)
			res = p.push(config.app, pushtitle, message, 0, 1, config.nma_priority )
			if res[config.nma_api][u'code'] == u'200':
				logger.logging.info ("NMA Notification succesfully send")
			else:
				error = res[config.nma_api]['message'].encode('ascii')
				logger.logging.error ("NMA Notification failed: " + error)
		if config.use_pushbullet == 1:
			data = urllib.urlencode({
				'type': 'note',
				'title': pushtitle,
				'body': message,
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
			text_file.write(message + "\n")
		else:
			pass
if not 'message' in locals():
	logger.logging.info("Nothing to be done, exiting")
else:
	if config.use_email == 1:
		text_file.close()
		logger.logging.info ("Sending Email notification...")
		emailer.SendEmail(pushtitle)
if config.use_email == 1:
	os.remove("Output.txt")
