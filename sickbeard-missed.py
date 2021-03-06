#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# <derkens@gmail.com>
# Notifies you if there are any 'missed' episodes
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
sys.excepthook = misc.log_uncaught_exceptions

if config.use_email:
	text_file = open("Output.txt", "w")

indexer, fork = api.sick_call_initial()
logger.logging.info("Opening connection to " + fork)

params = {'cmd': 'future', 'type': 'missed'}
res = api.sick_call(params)
mis = list(res['data']['missed'])
if str(mis) == "[]":
	logger.logging.info("Nothing to be done, exiting")

else:
	for index, string in enumerate(mis):
		showname = str(mis[index]['show_name']); logger.logging.debug("show = " + showname)
		season = str(mis[index]['season']); logger.logging.debug("season = " + season)
		epnum = str(mis[index]['episode']); logger.logging.debug("episode = " + epnum)
		epname = mis[index]['ep_name'].encode('utf-8'); logger.logging.debug("episode name = " + epname)

		args = {'showname': showname, 'season': int(season), 'epnum': int(epnum), 'epname': epname}
		pushtitle, pushmsg = misc.replace(config.sbmis_push_title, config.sbmis_push_msg, **args)
		logger.logging.debug("Dumping pushmsg for debug " + pushmsg)

		if config.use_pushover:
			push_info = {'potitle': pushtitle, 'pomsg': pushmsg, 'sound': config.sbmis_push_sound}
			api.pushover(config.user_key, config.app_token, config.push_device, **push_info)
		if config.use_nma:
			logger.logging.debug("Sending NMA notification...")
			from lib.pynma import pynma
			p = pynma.PyNMA(config.nma_api)
			res = p.push(config.app, pushtitle, pushmsg, 0, 1, config.nma_priority)
			if res[config.nma_api][u'code'] == u'200':
				logger.logging.info("NMA Notification succesfully send")
			else:
				error = res[config.nma_api]['message'].encode('ascii')
				logger.logging.error("NMA Notification failed: " + error)
		if config.use_pushbullet:
			push_info = pushtitle, pushmsg, config.deviceid, config.channeltag
			api.pushbullet(push_info)
		if config.use_email:
			text_file.write(pushmsg + "\n")

	else:
		if config.use_email:
			text_file.close()
			logger.logging.info("Sending Email notification...")
			emailer.SendEmail(pushtitle)
			os.remove("Output.txt")

misc.access_log_for_all()
