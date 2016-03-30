#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  github_notifier.py
#
# github notifications

import os.path, httplib, urllib, urllib2, logging
import sys
import json
import lib.logger.logger as logger
import lib.config as config
import lib.api as api
import lib.misc as misc
sys.excepthook = misc.log_uncaught_exceptions

if not config.githublogging:
	logger.logging.setLevel(logging.CRITICAL)

url = 'https://api.github.com/users/' + config.githubuser + '/received_events'

logger.logging.info("Opening URL: " + url)
stopid = misc.openpick('github_notifier')
if stopid == "novalue":
	logger.logging.debug("Didn't find 'lastid' is this a first run?")
else:
	logger.logging.debug("Found lastid = " + stopid)

firstid = None
try:
	req = urllib2.Request(url)
	req.add_header('Content-Type', 'application/json')
except urllib2.URLError, e:
    logger.logging.error('URLError = ' + str(e.reason))
	sys.exit()
r2 = urllib2.urlopen(req)
r2 = json.loads(r2.read())
print r2
for index, value in enumerate(r2):
	if r2[index]['type'] == 'PushEvent' or 'GollumEvent':
		if r2[index]['id'] == stopid:
			logger.logging.info("No new pushes found, exiting")
			sys.exit()
		else:
			if firstid is None:
				firstid = r2[index]['id']
				misc.dumppick('github_notifier', firstid)
			if r2[index]['type'] == 'PushEvent':
				for index2, value2 in enumerate(r2[index]['payload']['commits']):
					pushtitle = value2['author']['name'] + " pushed to " + r2[index]['repo']['name']
					pushmsg = value2['message']
					url = value2['url']
					url = url.replace("//api.", "//")
					url = url.replace("commits", "commit")
					url = url.replace("/repos/", "/")
					urltitle = "View commit on Github"
				if not config.githubapp_token:
					config.githubapp_token = config.app_token
				push_info = {'potitle': pushtitle.encode('utf-8'), 'pomsg': pushmsg.encode('utf-8'), 'pourl': url, 'pourltitle': urltitle, 'sound': config.github_push_sound}
				api.pushover(config.user_key, config.githubapp_token, config.push_device, **push_info)
			if r2[index]['type'] == 'GollumEvent':
				for index3, value3 in enumerate(r2[index]['payload']['pages']):
					pushtitle = r2[index]['actor']['login'] + " " + value3['action'] + " " + r2[index]['repo']['name'].split("/", 1)[1] + " wiki."
					pushmsg = "Page: '" + value3['title'] + "' was " + value3['action']
					url = value3['html_url']
					urltitle = "View wiki page on Github"
				if not config.githubapp_token:
					config.githubapp_token = config.app_token
				push_info = {'potitle': pushtitle, 'pomsg': pushmsg, 'pourl': url, 'pourltitle': urltitle, 'sound': config.github_push_sound}
				api.pushover(config.user_key, config.githubapp_token, config.push_device, **push_info)

misc.access_log_for_all()
