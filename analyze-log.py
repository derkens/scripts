#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  analyse-log.py
#


import os.path, httplib, urllib, urllib2, logging
import sys
import json
import lib.logger.logger as logger
import lib.config as config
import lib.api as api
import lib.misc as misc
import pickle

sys.excepthook = misc.log_uncaught_exceptions
logfile = misc.find_logfile()
error = 0
time = misc.openpick('analyzelog')
for i, line in enumerate(reversed(open(logfile, "r").readlines())):
	if time in line:
		break
	else:
		if "CRITICAL" in line:
			times = line[:19]
			error = 1
			break
if 'times' in locals():
	misc.dumppick('analyzelog', times)
if error:
	pushtitle = "ScriptSuite checker"
	pushmsg =  "Found an ERROR in the logfile @: " + time + ", one of the scripts failed."
	logger.logging.debug(pushmsg)
	push_info = {'potitle': pushtitle.encode('utf-8'), 'pomsg': pushmsg.encode('utf-8'), 'sound': config.github_push_sound}
	api.pushover(config.user_key, config.analyzeapptoken, config.push_device, **push_info)
else:
	logger.logging.debug("No errors found...")
misc.access_log_for_all()

