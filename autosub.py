#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#<derkens@gmail.com>
#post processing script for autosub (https://code.google.com/p/autosub-bootstrapbill/)
#wat it does: When a subtitle is downloaded, sub is muxed into a new mkv. This is so Kodi can use the subtile information in metadat for the skin (shows you an icon with sub language depending on your skin)
#it will update the xbmc database accordingly
#Todo: put language in a variable
# shamelessly incorporated stuff from Sick Beard AutoProcessTV
# Author: Nic Wolfe <nic@wolfeden.ca>
# URL: http://code.google.com/p/sickbeard/

import os
import sys
import httplib, urllib, urllib2, json, subprocess, re
import lib.logger.logger as logger
import lib.config as config
import lib.emailer as emailer
import base64

if config.ssl:
	protocol = 'https://'
else:
	protocol = 'http://'

#first, define needed variables
subandpath= sys.argv[1]
vidandpath= sys.argv[2]
show = sys.argv[4]
epis = sys.argv[6]
season = sys.argv[5]
newsubandpath= subandpath+'.utf8'
subandpathnoext = sys.argv[1] [:-7]
outputfileandpath = subandpathnoext+'.nl.mkv'
finalfileandpath = subandpathnoext+'.mkv'
pathvid = os.path.dirname(vidandpath)

getname = re.compile('.eries/(.*?)/Season')
m = getname.search(subandpath)
if m:
   findshow = m.group(1)

logger.logging.info ("Found showname: " + findshow)

#muxing vid and sub in new file (vid.nl.mkv)
p = subprocess.Popen(['mkvmerge', '-o', outputfileandpath, '--language', '-1:eng', vidandpath , '--language', '0:nld', subandpath],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = p.communicate()
if stdout:
    logger.logging.debug(stdout)
if stderr:
    logger.logging.error(stderr)

#the conversion to prevent 'strange' chars is not neccesary anymore on my system.
# convert sub to utf-8
#subprocess.call(['iconv', '-c', '-f', 'ISO-8859-1', '-t', 'UTF-8', subandpath, '-o', newsubandpath])
#os.remove(subandpath)
#os.rename(newsubandpath, subandpath)

os.remove(vidandpath)
os.rename(outputfileandpath, finalfileandpath)
os.chmod(finalfileandpath, 0775)
os.chmod(subandpath, 0775)

#aquire tvdbid from sickbeard
url = protocol + config.host + ':' + config.port + config.web_root + 'api/' + config.api_key + '/?'
logger.logging.info ("Opening connection to Sickbeard / Sickrage")

try:
	params = urllib.urlencode({'cmd': 'sb.searchtvdb', 'lang': 'nl', 'name': findshow})
	r = urllib2.urlopen(url + params).read()
	logger.logging.debug ("Opening URL: " + url + params)
	r = json.loads(r)
	tvdbid = str(r['data']['results'][0]['tvdbid'])
except IndexError:
	findshow = findshow.replace(" ",": ", 1)
	params = urllib.urlencode({'cmd': 'sb.searchtvdb', 'lang': 'nl', 'name': findshow})
	r = urllib2.urlopen(url + params).read()
	logger.logging.debug ("Opening URL: " + url + params)
	r = json.loads(r)
	tvdbid = str(r['data']['results'][0]['tvdbid'])

#aquire episode name from sickbeard
params = urllib.urlencode({'cmd': 'episode', 'tvdbid': tvdbid, 'season': season, 'episode': epis})
t = urllib2.urlopen(url + params).read()
logger.logging.debug ("Opening URL: " + url + params)
t = json.loads(t)
epname= t['data']['name'].encode('utf-8')
logger.logging.debug ("Episode name is: " + epname)

# remove and update episode in xbmc (filename did not change so automatic update does not work)
try:
	if vidandpath.endswith('.mkv') :
		data = {
			'jsonrpc':"2.0",
			'method':"VideoLibrary.GetEpisodes",
			'params':{"sort": {'order': "ascending", 'method': "title"}, "filter": {'operator': "contains", 'field': "title", 'value': epname}, 'properties': ["file"]},
			"id" : 1
		}
		req = urllib2.Request('http://' + config.kodi_host + ':' + config.kodi_port + '/jsonrpc')
		req.add_header('Content-Type', 'application/json')
		r2 = urllib2.urlopen(req, json.dumps(data))
		r2 = r2.read()
		r2 = json.loads(r2)
		xbmcepid = r2['result']['episodes'][0]['episodeid']
		logger.logging.debug ("Episode id in Kodi is: " + str(xbmcepid))

		data = {
			'jsonrpc':"2.0",
			'method':"VideoLibrary.RemoveEpisode",
			'params':{'episodeid' : xbmcepid },
			'id' : 1
		}
		req = urllib2.Request('http://' + config.kodi_host + ':' + config.kodi_port + '/jsonrpc')
		req.add_header('Content-Type', 'application/json')
		r3 = urllib2.urlopen(req, json.dumps(data))
		r3 = r3.read()
		r3 = json.loads(r3)
		logger.logging.info ("Removing episode from kodi library: " + r3['result'])

	else :
		logger.logging.debug ("Episode was not an .mkv")
		pass
except:
	logger.logging.debug ("Episode removal from Kodi failed")
	pass
#update xbmc (only the path)
try:
	data = {
		'jsonrpc':"2.0",
		'method':"VideoLibrary.Scan",
		'params':{'directory':pathvid},
		'id' : 1
	}
	req = urllib2.Request('http://' + config.kodi_host + ':' + config.kodi_port + '/jsonrpc')
	req.add_header('Content-Type', 'application/json')
	response = urllib2.urlopen(req, json.dumps(data))
	status = ""
	logger.logging.debug ("Scanning episode to kodi library: " + r3['result'])

except:
	logger.logging.debug ("Can't reach Kodi")
	status = "!"

finally:
	if config.use_pushover == 1:
		logger.logging.debug ("Sending Pushover notification...")
		pushurl= 'http://thetvdb.com/?tab=series&id=' + tvdbid + '&lid=13'
		pushmsg= "<i><b>"+epname+"</b> ("+season+"x"+epis+") </i>"+status

		conn = httplib.HTTPSConnection('api.pushover.net:443')
		conn.request('POST', '/1/messages.json',
		urllib.urlencode({
			'token': config.asapp_token,
			'user': config.user_key,
			'message': pushmsg,
			'title': findshow,
			'url': pushurl,
			'url_title': show,
			'html': "1",
			'sound': "Piano Bar",
		}), { 'Content-type': 'application/x-www-form-urlencoded' })
		r = conn.getresponse()
		r = json.loads(r.read())
		if r['status'] == 1 :
			logger.logging.info("Pushover notification sent succesfully")
		else:
			logger.logging.error("Pushover failed with following error" + str(r['errors']))
	if config.use_pushbullet == 1:
		data = urllib.urlencode({
			'type': "note",
			'title': findshow,
			'body': epname+" ("+season+"x"+epis+")",
			'device_id': config.deviceid,
			'channel_tag': config.aschanneltag
			})
		auth = base64.encodestring('%s:' % ptoken).replace('\n', '')
		req = urllib2.Request('https://api.pushbullet.com/v2/pushes', data)
		req.add_header('Authorization', 'Basic %s' % auth)
		response = urllib2.urlopen(req)
		res = json.load(response)
		if 'error' in res:
			logger.logging.error ("Pushbullet notification failed")
		else:
			logger.logging.info ("Pushbullet notification sucesfully sent")
	if config.use_nma == 1:
		logger.logging.info ("Sending NMA notification...")
		from lib.pynma import pynma
		p = pynma.PyNMA(nma_api)
		p.push(app, show, pushmsg, 0, 1, nma_priority )
