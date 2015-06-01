#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  sickrage-pp.py
#
# torrent removal and notification

import json, httplib, os, sys
import lib.logger.logger as logger
import lib.config as config
import lib.emailer as emailer
import lib.api as api
import lib.misc as misc

path = "/transmission/rpc/"
# in case of torrent, remove processed torrent from transmission list
origpath = sys.argv[2]
if config.deltorrent:
	if config.tordir in origpath:
		torname = os.path.split(os.path.dirname(origpath))[1]
		if torname in config.tordir:
			torname =  os.path.basename(origpath)
			logger.logging.debug("found name of torrent: " + torname)

		conn = httplib.HTTPConnection(config.tm_host, config.tm_port)
		conn.request("GET", path)
		response = conn.getresponse()
		response_data = response.read()
		response.close()
		conn.close()
		session_id = str(response_data).split("X-Transmission-Session-Id: ")[-1].split("</code></p>")[0]
		headers = {'x-transmission-session-id': str(session_id)}
		logger.logging.debug("connection to transmission for session id")

		fields = ['name', 'id']
		query = json.dumps({'method': 'torrent-get', 'arguments': {'fields': fields}}).encode('utf-8')

		conn = httplib.HTTPConnection(config.tm_host, config.tm_port)
		conn.request("POST", path, query, headers)
		response = conn.getresponse()
		response_raw = response.read()
		response.close()
		conn.close()
		response = json.loads(response_raw.decode("utf-8"))
		for index, string in enumerate(response['arguments']['torrents']):
			if str(response['arguments']['torrents'][index]['name']) == torname:
				torid = str(response['arguments']['torrents'][index]['id'])
				torid = int(torid)
				logger.logging.debug("transmission torrent id found: " + str(torid))

		query = json.dumps({'method': 'torrent-remove', 'arguments': {'ids': torid}}).encode('utf-8')
		conn = httplib.HTTPConnection(config.tm_host, config.tm_port)
		conn.request("POST", path, query, headers)
		response = conn.getresponse()
		response_raw = response.read()
		response.close()
		conn.close()
		response = json.loads(response_raw.decode("utf-8"))
		logger.logging.debug("removing torrent from transmisson list with id: " + str(torid))



if config.use_email:
	text_file = open("Output.txt", "w")

url = config.protocol + config.host + ":" + config.port + config.web_root + "api/" + config.api_key + "/?"

logger.logging.info ("Opening URL: " + url)

params = { 'cmd': 'history', 'limit': 1 , 'type': 'downloaded' }
t = api.sick_call(params)
showname= t['data'][0]['show_name'].encode('utf-8')
tvdbid= t['data'][0]['tvdbid']
season= t['data'][0]['season']
epnum= t['data'][0]['episode']

params = { 'cmd': 'episode', 'tvdbid': tvdbid , 'season': season, 'episode': epnum }
t = api.sick_call(params)
epname = t['data']['name'].encode('utf-8')

pushtitle = config.srpp_push_title
pushmsg = config.srpp_push_msg
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
	text_file.write(pushmsg + "\n")

else:
	if config.use_email:
		text_file.close()
		logger.logging.info ("Sending Email notification...")
		emailer.SendEmail(pushtitle)
		os.remove("Output.txt")

misc.access_log_for_all()
