#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  api.py
#
import logging, stat, pwd, grp, os, httplib, urllib, json, urllib2, base64, sys
import lib.logger.logger as logger
import lib.config as config
import lib.misc as misc
import requests, pickle, time


def tvdb_init():
	url= "https://api.thetvdb.com/login"
	headers= {'Content-Type': 'application/json'}
	payload={
		"apikey": config.tvdbapi
		}
	tvdb_token_age = misc.openpick('tvdb_token_age')
	if tvdb_token_age == "novalue":
		misc.dumppick('tvdb_token_age', '1514764800')
		misc.dumppick('tvdbtoken', 'notoken')
	elif (int(time.time()) - int(misc.openpick('tvdb_token_age'))) < 86400:
		logger.logging.debug("Token still valid")
		tvdb_token = misc.openpick('tvdb_token')    
	else:
		logger.logging.debug("Token Invalid, get new token")
		conn = requests.post(url, json=payload, headers=headers)
		res = json.loads(conn.text)
		tvdb_token = res["token"]
		misc.dumppick('tvdb_token', tvdb_token)
		misc.dumppick('tvdb_token_age',int(time.time()) )
	return tvdb_token

def tvdb_call(seriesname):
    tvdb_token = tvdb_init()
    url= "https://api.thetvdb.com/search/series"
    headers= {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + tvdb_token }
    payload={
		"name": seriesname
        }
    conn = requests.get(url, params=payload, headers=headers)
    res = json.loads(conn.text)
    imglink = res['data'][0]['banner']
    serienaam = res['data'][0]['seriesName']
    tvdbid = res['data'][0]['id']
    return tvdbid, serienaam.encode('utf-8'), imglink

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
