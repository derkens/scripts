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
import lib.misc as misc
import lib.api as api

if config.use_email:
	text_file = open("Output.txt", "w")

url = config.protocol + config.host + ":" + config.port + config.web_root + "api/" + config.api_key + "/?"

logger.logging.info ("Opening URL: " + url)

params = config.urlencode({'cmd': 'shows', 'sort': 'name', 'paused': '0'})
t = urllib2.urlopen(url + params).read()
t = json.loads(t)
logger.logging.debug(t)
end = filter( lambda x: x['status']=='Ended', t['data'].values() )
logger.logging.debug(end)

if end == []:
	logger.logging.info("Nothing to be done, exiting")

for i in end :
	showname = i['show_name'] ; logger.logging.debug("Showname = " + showname)
	stat = i['status'] ; logger.logging.debug("Show status = " + stat)
	net = i['next_ep_airdate'] ; logger.logging.debug("Next episode date = " + net)
	if net == '':
		params = config.urlencode({'cmd': 'sb.searchtvdb', 'lang': 'nl', 'name': showname})
		r = urllib2.urlopen(url + params).read()
		r = json.loads(r)
		logger.logging.debug(r)
		tvdbid = str(r['data']['results'][0]['tvdbid'])
		logger.logging.debug(tvdbid)
		params = config.urlencode({'cmd': 'show.pause', 'tvdbid': tvdbid, 'pause': 1})
		s = urllib2.urlopen(url + params).read()
		logger.logging.debug(s)
		pushtitle = config.sbca_push_title
		pushmsg = config.sbca_push_msg
		season = ""
		epnum = ""
		epname = ""
		pushtitle, pushmsg = misc.replace(pushtitle,pushmsg,showname,season,epnum,epname)
		if config.use_pushover:
			push_info = (config.user_key, config.app_token, config.push_device, pushtitle, pushmsg)
			api.pushover(push_info)
		if config.use_nma:
			logger.logging.info ("Sending NMA notification...")
			from lib.pynma import pynma
			p = pynma.PyNMA(config.nma_api)
			res = p.push(config.app, pushtitle, pushmsg, 0, 1, config.nma_priority )
			if res[config.nma_api][u'code'] == u'200':
				logger.logging.info ("NMA Notification succesfully send")
			else:
				error = res[config.nma_api]['message'].encode('ascii')
				logger.logging.error ("NMA Notification failed: " + error)
		if config.use_pushbullet:
			push_info = pushtitle, pushmsg, config.deviceid, config.channeltag
			api.pushbullet(push_info)
		if config.use_email:
			text_file.write(show + " is possibly cancelled\n")


if config.use_email:
	text_file.close()
	logger.logging.info ("Sending Email notification...")
	emailer.SendEmail(show)
	os.remove("Output.txt")

misc.access_log_for_all()
