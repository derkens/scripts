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
import base64, string
sys.excepthook = misc.log_uncaught_exceptions

indexer, fork = api.sick_call_initial()

path = "/transmission/rpc/"
# in case of torrent, remove processed torrent from transmission list
origpath = sys.argv[2]
if config.deltorrent:
	if config.tordir in origpath:
		torname = os.path.split(os.path.dirname(origpath))[1]
		if torname in config.tordir:
			torname = os.path.basename(origpath)
		logger.logging.debug("found name of torrent: " + torname)

		logger.logging.info("Opening connection to Transmission")
		auth = base64.encodestring('%s:%s' % (config.tm_user, config.tm_pass)).replace('\n', '')
		conn = httplib.HTTPConnection(config.tm_host, config.tm_port)
		headers = {"Authorization": "Basic %s" % auth}
		conn.request("GET", path, None, headers)
		response = conn.getresponse()
		response_data = response.read()
		response.close()
		conn.close()
		session_id = str(response_data).split("X-Transmission-Session-Id: ")[-1].split("</code></p>")[0]
		headers = {'x-transmission-session-id': str(session_id), "Authorization": "Basic %s" % auth}
		logger.logging.debug("Retreived session id: " + session_id)

		fields = ['name', 'id']
		query = json.dumps({'method': 'torrent-get', 'arguments': {'fields': fields}}).encode('utf-8')
		logger.logging.debug("Transmission parameters: " + json.dumps(query, indent=4))
		conn = httplib.HTTPConnection(config.tm_host, config.tm_port)
		conn.request("POST", path, query, headers)
		response = conn.getresponse()
		response_raw = response.read()
		response.close()
		conn.close()
		response = json.loads(response_raw.decode("utf-8"))
		logger.logging.debug("Transmission results: " + json.dumps(response, indent=4))
		for index, string in enumerate(response['arguments']['torrents']):
			if str(response['arguments']['torrents'][index]['name']) == torname:
				torid = str(response['arguments']['torrents'][index]['id'])
				torid = int(torid)
				logger.logging.debug("Transmission torrent id found: " + str(torid))

		query = json.dumps({'method': 'torrent-remove', 'arguments': {'ids': torid}}).encode('utf-8')
		logger.logging.debug("Transmission parameters: " + json.dumps(query, indent=4))
		conn = httplib.HTTPConnection(config.tm_host, config.tm_port)
		conn.request("POST", path, query, headers)
		response = conn.getresponse()
		response_raw = response.read()
		response.close()
		conn.close()
		response = json.loads(response_raw.decode("utf-8"))
		logger.logging.debug("Transmission results: " + json.dumps(response, indent=4))
		logger.logging.info("Removing torrent from Transmisson list with id: " + str(torid))

if config.use_email:
	text_file = open("Output.txt", "w")
logger.logging.info("Opening connection to " + fork)
params = {'cmd': 'history', 'limit': 1, 'type': 'downloaded'}
res = api.sick_call(params)
showname = res['data'][0]['show_name'].encode('utf-8')
sickid = res['data'][0][indexer]
season = res['data'][0]['season']
epnum = res['data'][0]['episode']
qlty = res['data'][0]['quality'].encode('utf-8')
lang = ""
params = {'cmd': 'episode', indexer: sickid, 'season': season, 'episode': epnum}
res = api.sick_call(params)
epname = res['data']['name'].encode('utf-8')
print res['data']['release_name']
if "PROPER" in str(res['data']['release_name']) or "REPACK" in str(res['data']['release_name']):
	proper = " (proper)"
else:
	proper = ""
args = {'showname': showname, 'season': int(season), 'epnum': int(epnum), 'epname': epname, 'lang': lang, 'qlty': qlty}
pushtitle, pushmsg = misc.replace(config.srpp_push_title, config.srpp_push_msg, **args)

if config.use_pushover:
	push_info = {'potitle': pushtitle, 'pomsg': pushmsg + proper, 'sound': config.srpp_push_sound}
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
