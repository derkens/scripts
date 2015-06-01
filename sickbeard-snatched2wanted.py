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
import lib.logger.logger as logger
import lib.config as config
import lib.emailer as emailer
import lib.misc as misc
import lib.api as api


params = { 'cmd': 'history', 'type': 'downloaded', 'limit': 20 }
res = api.sick_call(params)
down = list(res['data'])
logger.logging.debug (down)
params = { 'cmd': 'history', 'type': 'snatched', 'limit': 20 }
res = api.sick_call(params)
snat = list(res['data'])
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
if config.use_email:
	text_file = open("Output.txt", "w+")
for index, string in enumerate(onlysnat):
	temp1 = str(onlysnat[index])
	temp2 = temp1.rsplit('_')
	showname = str(temp2[0]) ; logger.logging.debug("showname: " + showname)
	season = str(temp2[1]) ; logger.logging.debug("season: " + season)
	epnum = str(temp2[2]) ; logger.logging.debug("episode: " + epnum)
	tvdbid = str(temp2[3]) ; logger.logging.debug("tvdbid: " + tvdbid)
	params = {'cmd': 'episode', 'tvdbid': tvdbid, 'season': season, 'episode': epnum, }
	res = api.sick_call(params)
	epstatus = str(res['data']['status'])
	epname = str(res['data']['name'])
	if epstatus != "Snatched":
		pass
	else:
		params = {'cmd': 'episode.setstatus', 'tvdbid': tvdbid, 'season': season, 'episode': epnum, 'status': 'wanted' }
		res = api.sick_call(params)
		logger.logging.debug(res)
		pushtitle = config.sbs2w_push_title
		pushmsg = config.sbs2w_push_msg
		pushtitle, pushmsg = misc.replace(pushtitle,pushmsg,showname,season,epnum,epname)
		if config.use_pushover:
			push_info = (config.user_key, config.app_token, config.push_device, pushtitle, pushmsg)
			api.pushover(push_info)
		if config.use_nma:
			logger.logging.debug ("Sending NMA notification...")
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
			text_file.write(message + "\n")
		else:
			pass
if not 'pushmsg' in locals():
	logger.logging.info("Nothing to be done, exiting")
else:
	if config.use_email:
		text_file.close()
		logger.logging.info ("Sending Email notification...")
		emailer.SendEmail(pushtitle)
if config.use_email:
	os.remove("Output.txt")

misc.access_log_for_all()
