#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# <derkens@gmail.com>
# show cancelled? this script notifies you and put the show in 'pause' (after the last ep oc.)
#
# shamelessly incorporated stuff from Sick Beard AutoProcessTV
# Author: Nic Wolfe <nic@wolfeden.ca>
# URL: http://code.google.com/p/sickbeard/

import os.path
import sys, json
import lib.logger.logger as logger
import lib.config as config
import lib.emailer as emailer
import lib.misc as misc
import lib.api as api
sys.excepthook = misc.log_uncaught_exceptions

indexer, fork = api.sick_call_initial()

if config.use_email:
	text_file = open("Output.txt", "w")

logger.logging.info("Opening connection to " + fork)
params = {'cmd': 'shows', 'sort': 'name', 'paused': '0'}
res = api.sick_call(params)

end = filter(lambda x: x['status'] == 'Ended', res['data'].values())
logger.logging.debug(json.dumps(end, indent=4))

if end == []:
	logger.logging.info("Nothing to be done, exiting")

for i, value in enumerate(end):
	showname = end[i]['show_name']; logger.logging.debug("Showname = " + showname)
	sickid = end[i]['indexerid']
	params = {'cmd': 'show.stats', 'indexerid': sickid}
	res = api.sick_call(params)
	total = res['data']['total']
	totaldwl = res['data']['downloaded']['total']
	totalsnt = res['data']['snatched']['total']
	unaired = res['data']['unaired']

	stat = end[i]['status']; logger.logging.debug("Show status = " + stat)
	logger.logging.info(showname + " has status: " + stat)
	if unaired > 0:
		logger.logging.info(showname + " has status Ended, but not all episodes have aired.")
	if unaired == 0 and (total - totaldwl > 0):
		logger.logging.info(showname + " has status Ended, but not all episodes are downloaded")
	if unaired == 0 and (total - totaldwl == 0) and totalsnt == 0:
		logger.logging.debug(showname + " has " + indexer + " " + str(sickid))
		sbcancelled = misc.openpick('sb-cancelled')
		if sbcancelled == "novalue":
			sbcancelled = []
		if str(sickid) not in sbcancelled:
			sbcancelled.append(str(sickid))
			misc.dumppick('sb-cancelled', sbcancelled)

			args = {'showname': showname.encode("utf-8")}
			pushtitle, pushmsg = misc.replace(config.sbca_push_title, config.sbca_push_msg, **args)

			if config.use_pushover:
				push_info = {'potitle': pushtitle, 'pomsg': pushmsg, 'sound': config.sbca_push_sound}
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
				text_file.write(show + " is possibly cancelled\n")
		else:
			logger.logging.debug(str(sickid) + " is already in pickle, skipping")
			logger.logging.info("Nothing to be done, exiting")

if config.use_email:
	text_file.close()
	logger.logging.info("Sending Email notification...")
	emailer.SendEmail(show)
	os.remove("Output.txt")

misc.access_log_for_all()
