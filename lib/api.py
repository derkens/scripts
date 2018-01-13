#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  api.py
#
import xml.etree.cElementTree as etree
import logging, stat, pwd, grp, os, httplib, urllib, json, urllib2, base64, sys
import lib.logger.logger as logger
import lib.config as config
import requests


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
	if not 'GetTVShows' in method:
		 logger.logging.debug("Kodi call: " + json.dumps(res, indent=4))
	else:
		logger.logging.debug("kodi_call output suppressed, long showlist")
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


def pushover(user_key, apptoken, pushdevice, **push_info):
	logger.logging.debug("Sending Pushover notification...")
	url = "https://api.pushover.net/1/messages.json"
	try:
		files = {'attachment': open(push_info.get('image',''), 'rb')}
	except:
		files = ''
	payload={
		"token": apptoken,
		"user": user_key,
		"message": push_info['pomsg'],
		"title": push_info['potitle'],
		"device": pushdevice,
		"url": push_info.get('pourl', ''),
		"url_title": push_info.get('pourltitle', ''),
		"sound": push_info.get('sound', ''),
        "html": "1"
	}
	conn = requests.post(url, params=payload, files=files)
	res = json.loads(conn.text)
	if res["status"]:
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
