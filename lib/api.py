#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  api.py
#
import xml.etree.cElementTree as etree
import logging, stat, pwd, grp, os, httplib, urllib, json, urllib2, base64, sys
import lib.logger.logger as logger
import lib.config as config


def tvdb_call(params):
	url = 'http://thetvdb.com/api/GetSeries.php?seriesname='
	res = urllib.urlopen(url + params).read()
	root = etree.fromstring(res)
	tvdbid = root[0][0].text
	serienaam = root[0][2].text
	return tvdbid, serienaam


def kodi_call(params, method):
	data = {
		'jsonrpc': "2.0",
		'method': method,
		'params': params,
		"id": 1
	}
	req = urllib2.Request('http://' + config.kodi_host + ':' + config.kodi_port + '/jsonrpc')
	req.add_header('Content-Type', 'application/json')
	logger.logging.debug("Kodi call: " + str(method) + " " + str(params))
	res = urllib2.urlopen(req, json.dumps(data))
	res = json.loads(res.read())
	logger.logging.debug("Kodi results: " + json.dumps(res, indent=4))
	return res


def sick_call_initial():
	logger.logging.debug("Checking version of Sickbeard or Sickrage")
	url = config.protocol + config.host + ":" + config.port + config.web_root + "api/" + config.api_key + "/?"
	params = config.urlencode({'cmd': 'sb'})
	res = urllib2.urlopen(url + params).read()
	res = json.loads(res)
	if str(res['data']['sr_version']):
		logger.logging.debug("We are connecting to SickRage, version: " + str(res['data']['sr_version']))
		indexer = 'indexerid'
		fork = "SickRage"
	else:
		logger.logging.debug("We are connecting to SickBeard, version: " + str(res['data']['sb_version']))
		indexer = 'tvdbid'
		fork = "SickBeard"
	return indexer, fork


def sick_call(params):
	logger.logging.debug("sick_call parameters: " + str(params))
	url = config.protocol + config.host + ":" + config.port + config.web_root + "api/" + config.api_key + "/?"
	params = config.urlencode(params)
	res = urllib2.urlopen(url + params).read()
	res = json.loads(res)
	if 'shows' not in params:
		logger.logging.debug("sick_call results: " + json.dumps(res, indent=4))
	else:
		logger.logging.debug("sick_call output suppressed, long showlist")
	return res


def pushover(push_info):
	try:
		user_key, app_token, push_device, pushtitle, pushmsg = push_info
		url, urltitle = "", ""
	except ValueError:
		user_key, app_token, push_device, pushtitle, pushmsg, url, urltitle = push_info

	logger.logging.debug("Sending Pushover notification...")
	conn = httplib.HTTPSConnection("api.pushover.net:443")
	conn.request("POST", "/1/messages.json",
	urllib.urlencode({
		"token": app_token,
		"user": user_key,
		"message": pushmsg,
		"title": pushtitle,
		"device": push_device,
		"url": url,
		"url_title": urltitle,
		"html": "1"
	}), {"Content-type": "application/x-www-form-urlencoded"})
	res = conn.getresponse()
	res = json.loads(res.read())
	if res["status"] == 1:
		logger.logging.info("Pushover notification sent succesfully")
	else:
		logger.logging.error("Pushover failed with following error" + str(res["errors"]))


def pushbullet(push_info):
	pushtitle, pushmsg, config.deviceid, config.channeltag = push_info
	data = urllib.urlencode({
		'type': "note",
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
		logger.logging.error("Pushbullet notification failed")
	else:
		logger.logging.info("Pushbullet notification sucesfully sent")
