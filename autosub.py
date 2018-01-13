#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# <derkens@gmail.com>
# post processing script for autosub (https://github.com/Donny87/autosub-bootstrapbill)
# wat it does: When a subtitle is downloaded, sub is muxed into a new mkv. This is so Kodi can use the subtitle information in metadata for the skin (shows you an icon with sub language depending on your skin)
# it will update the xbmc database accordingly
# Todo: put language in a variable
# shamelessly incorporated stuff from Sick Beard AutoProcessTV
# Author: Nic Wolfe <nic@wolfeden.ca>
# URL: http://code.google.com/p/sickbeard/

import os, sys, subprocess, re
import lib.logger.logger as logger
import lib.config as config
import lib.emailer as emailer
import lib.api as api
import lib.misc as misc
sys.excepthook = misc.log_uncaught_exceptions

indexer, fork = api.sick_call_initial()

# first, define needed variables
subandpath = sys.argv[1]
vidandpath = sys.argv[2]
lang = sys.argv[3]
show = sys.argv[4]
epnum = int(sys.argv[6])
season = int(sys.argv[5])
subandpathnoext = sys.argv[1][:-7]
outputfileandpath = subandpathnoext + '.nl.mkv'
finalfileandpath = subandpathnoext + '.mkv'
pathvid = os.path.dirname(vidandpath)
status = ""

logger.logging.info("Opening connection to " + fork)
params = {'cmd': 'sb.getrootdirs'}
u = api.sick_call(params)
for index, string in enumerate(u['data']):
	if u['data'][index]['location'].encode('utf-8') in subandpath:
		rootdir = u['data'][index]['location']
getname = re.compile(rootdir + '/(.*?)/')
m = getname.search(subandpath)
if m:
	findshow = m.group(1)
logger.logging.info("Found showname: " + findshow)

if config.muxing:
	# muxing vid and sub in new file (vid.nl.mkv)
	p = subprocess.Popen(['mkvmerge', '-o', outputfileandpath, '--language', '-1:eng', vidandpath, '--language', '0:nld', subandpath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = p.communicate()
	if stdout:
		logger.logging.debug(stdout)
	if stderr:
		logger.logging.error(stderr)
	if os.path.exists(outputfileandpath):
		os.remove(vidandpath)
		os.rename(outputfileandpath, finalfileandpath)
		os.chmod(finalfileandpath, 0775)
		os.chmod(subandpath, 0775)
	else:
		os.remove(subandpath)
		logger.logging.error("subtitle muxing failed, removing possibly faulty subtitle...")
		status = "Failed to mux "

logger.logging.debug("Opening connection to thetvdb.com")
tvdbid, showname, imglink = api.tvdb_call(findshow)
logger.logging.debug("Showname found on thetvdb.com: " + showname)

try:
	params = {'cmd': 'shows', 'sort': 'name'}
	res = api.sick_call(params)
	res = misc.lower_keys(res)
	sickid = res['data'][showname.lower()][indexer]
except:
	showname = findshow
	params = {'cmd': 'shows', 'sort': 'name'}
	res = api.sick_call(params)
	res = misc.lower_keys(res)
	sickid = res['data'][showname.lower()][indexer]

params = {'cmd': 'episode', indexer: sickid, 'season': season, 'episode': epnum}
res = api.sick_call(params)
epname = res['data']['name'].encode('utf-8')
logger.logging.info("Episode name is: " + epname)

if config.use_symlinks:
	logger.logging.info("making symlinks is on...")
	symloc = os.path.join(config.symdir ,showname, "Season " + str("%02d" % season), '')
	if not os.path.exists(symloc):
		os.makedirs(symloc)
		logger.logging.debug("No directories yet, making them now..")
	if not os.path.exists(symloc + os.path.basename(finalfileandpath)):
		os.symlink(finalfileandpath, symloc + os.path.basename(finalfileandpath))
		logger.logging.debug("Making symlink " + symloc + os.path.basename(finalfileandpath))
	if not os.path.exists(symloc + os.path.basename(subandpath)):
		os.symlink(subandpath, symloc + os.path.basename(subandpath))
		logger.logging.debug("Making symlink " + symloc + os.path.basename(subandpath))
	else:
		logger.logging.debug("Symlinks existed, are you re-downloading a subtitle?")

if config.use_kodi and config.muxing and status is "":
	logger.logging.debug("Kodi integration is on...")
	try:
		if vidandpath.endswith('.mkv'):
			method = "VideoLibrary.GetEpisodes"
			params = {"sort": {'order': "ascending", 'method': "title"}, "filter": {'operator': "contains", 'field': "title", 'value': epname}, 'properties': ["file"]}
			res = api.kodi_call(params, method)
			xbmcepid = res['result']['episodes'][0]['episodeid']
			loc = res['result']['episodes'][0]['file']
			scanloc = os.path.dirname(os.path.dirname(loc))
			logger.logging.debug("Episode id in Kodi is: " + str(xbmcepid))

			method = "VideoLibrary.RemoveEpisode"
			params = {'episodeid': xbmcepid}
			res = api.kodi_call(params, method)
			logger.logging.debug("Removing episode from kodi library: " + res['result'])
		else:
			logger.logging.debug("Episode was not an .mkv")
			pass
	except:
		logger.logging.exception("exception:")
		logger.logging.debug("Episode removal from Kodi failed")
	try:
		method = "VideoLibrary.Scan"
		params = {'directory': scanloc}
		res = api.kodi_call(params, method)
		logger.logging.info("Scanning episode to kodi library: " + res['result'])
	except:
		logger.logging.exception("exception:")
		logger.logging.debug("Can't reach Kodi")

args = {'showname': status + showname, 'season': int(season), 'epnum': int(epnum), 'epname': epname, 'lang': lang}
pushtitle, pushmsg = misc.replace(config.aspush_title, config.aspush_msg, **args)

if config.use_pushover:
	if not config.asapp_token:
		config.asapp_token = config.app_token
		logger.logging.info("No separate app token found for Autosub, using the default. (See Pushover.net how to add your own app token)")
	push_info = {'potitle': pushtitle, 'pomsg': pushmsg, 'sound': config.aspush_sound}
	api.pushover(config.user_key, config.asapp_token, config.push_device, **push_info)
if config.use_pushbullet:
	push_info = pushtitle, pushmsg, config.deviceid, config.aschanneltag
	api.pushbullet(push_info)
if config.use_nma:
	logger.logging.debug("Sending NMA notification...")
	from lib.pynma import pynma
	p = pynma.PyNMA(nma_api)
	p.push(app, show, pushmsg, 0, 1, nma_priority)
	if res[config.nma_api][u'code'] == u'200':
		logger.logging.info("NMA Notification succesfully send")
	else:
		error = res[config.nma_api]['message'].encode('ascii')
		logger.logging.error("NMA Notification failed: " + error)

misc.access_log_for_all()
