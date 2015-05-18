#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  sickrage-pp.py
#
# Only used for notification format change...

import urllib, json, httplib
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

params = urllib.urlencode({ 'cmd': 'history', 'limit': 1 , 'type': 'downloaded' })
t = urllib.urlopen(url + params).read()
t = json.loads(t)

showname= t['data'][0]['show_name'].encode('utf-8')
tvdbid= t['data'][0]['tvdbid']
season= t['data'][0]['season']
epnum= t['data'][0]['episode']

params = urllib.urlencode({ 'cmd': 'episode', 'tvdbid': tvdbid , 'season': season, 'episode': epnum })
t = urllib.urlopen(url + params).read()
t = json.loads(t)
epname = t['data']['name'].encode('utf-8')
pushmsg = "<i><b>"+epname+"</b> ("+str(season)+"x"+str(epnum)+") </i>"
pushtitle = showname

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
			"html": "1"
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

print showname
print pushmsg
