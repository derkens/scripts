#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#<derkens@gmail.com>
#post processing script for autosub (https://github.com/Donny87/autosub-bootstrapbill)
#wat it does: When a subtitle is downloaded, sub is muxed into a new mkv. This is so Kodi can use the subtitle information in metadata for the skin (shows you an icon with sub language depending on your skin)
#it will update the xbmc database accordingly
#Todo: put language in a variable
# shamelessly incorporated stuff from Sick Beard AutoProcessTV
# Author: Nic Wolfe <nic@wolfeden.ca>
# URL: http://code.google.com/p/sickbeard/

import os, sys, subprocess, re
import lib.logger.logger as logger
import lib.config as config
import lib.emailer as emailer
import lib.api as api
import lib.misc as misc

#first, define needed variables
subandpath= sys.argv[1]
vidandpath= sys.argv[2]
lang = sys.argv[3]
show = sys.argv[4]
epnum = sys.argv[6]
season = sys.argv[5]
subandpathnoext = sys.argv[1] [:-7]
outputfileandpath = subandpathnoext+'.nl.mkv'
finalfileandpath = subandpathnoext+'.mkv'
pathvid = os.path.dirname(vidandpath)

getname = re.compile('.eries/(.*?)/Season')
m = getname.search(subandpath)
if m:
   findshow = m.group(1)
logger.logging.info ("Found showname: " + findshow)
if config.muxing:
	#muxing vid and sub in new file (vid.nl.mkv)
	p = subprocess.Popen(['mkvmerge', '-o', outputfileandpath, '--language', '-1:eng', vidandpath , '--language', '0:nld', subandpath],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = p.communicate()
	if stdout:
		logger.logging.debug(stdout)
	if stderr:
		logger.logging.error(stderr)


	os.remove(vidandpath)
	os.rename(outputfileandpath, finalfileandpath)
	os.chmod(finalfileandpath, 0775)
	os.chmod(subandpath, 0775)

logger.logging.debug ("Opening connection to thetvdb.com")
tvdbid, showname = api.tvdb_call(findshow)
logger.logging.info ("Showname found on thetvdb.com: " + showname)

logger.logging.debug ("Opening connection to Sickbeard / Sickrage")
params = { 'cmd': 'shows', 'sort': 'name' }
res = api.sick_call(params)
if 'indexerid'in res['data'][showname]: sickid = res['data'][showname]['indexerid'] ; indexerid = 'indexerid'
else: sickid = tvdbid ; indexerid = 'tvdbid'

params = {'cmd': 'episode', indexerid: sickid, 'season': season, 'episode': epnum}
res = api.sick_call(params)
epname = res['data']['name']
logger.logging.debug ("Episode name is: " + epname)
if config.use_kodi and config.muxing:
	logger.logging.debug("Kodi integration is on...")
	try:
		if vidandpath.endswith('.mkv') :
			method = "VideoLibrary.GetEpisodes"
			params = {"sort": {'order': "ascending", 'method': "title"}, "filter": {'operator': "contains", 'field': "title", 'value': epname}, 'properties': [ "file" ]}
			res = api.kodi_call(params, method)
			xbmcepid = res['result']['episodes'][0]['episodeid']
			logger.logging.debug ("Episode id in Kodi is: " + str(xbmcepid))

			method = "VideoLibrary.RemoveEpisode"
			params = {'episodeid' : xbmcepid }
			res = api.kodi_call(params, method)
			logger.logging.info ("Removing episode from kodi library: " + res['result'])

		else :
			logger.logging.debug ("Episode was not an .mkv")
			pass
	except:
		logger.logging.exception("exception:")
		logger.logging.debug ("Episode removal from Kodi failed")

	try:
		method = "VideoLibrary.Scan"
		params = {'directory' : pathvid }
		res = api.kodi_call(params, method)
		logger.logging.debug ("Scanning episode to kodi library: " + res['result'])
		status = ""
	except:
		logger.logging.exception("exception:")
		logger.logging.debug ("Can't reach Kodi")
		status = "!"

pushtitle = config.aspush_title
pushmsg = config.aspush_msg
pushtitle, pushmsg = misc.replace(pushtitle,pushmsg,showname,season,epnum,epname,lang)

if config.use_pushover:
	if not config.asapp_token:
		config.asapp_token = config.app_token
	push_info = (config.user_key, config.asapp_token, config.push_device, pushtitle, pushmsg)
	api.pushover(push_info)
if config.use_pushbullet:
	push_info = pushtitle, pushmsg, config.deviceid, config.aschanneltag
	api.pushbullet(push_info)
if config.use_nma:
	logger.logging.info ("Sending NMA notification...")
	from lib.pynma import pynma
	p = pynma.PyNMA(nma_api)
	p.push(app, show, pushmsg, 0, 1, nma_priority )

misc.access_log_for_all()
