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
import httplib, urllib, urllib2, json, subprocess
import base64

# Try importing Python 2 modules using new names
try:
    import ConfigParser as configparser
    import urllib2
    from urllib import urlencode

# On error import Python 3 modules
except ImportError:
    import configparser
    import urllib.request as urllib2
    from urllib.parse import urlencode

# Default values
host = "localhost"
port = "8081"
api_key = ""
ssl = 0
web_root = "/"
app = "SickBeard"

default_url = host + ":" + port + web_root
if ssl:
	default_url = "https://" + default_url
else:
	default_url = "http://" + default_url

# Get values from config_file
config = configparser.RawConfigParser()
config_filename = os.path.join(os.path.dirname(sys.argv[0]), "settings.cfg")

if not os.path.isfile(config_filename):
	print ("ERROR: " + config_filename + " doesn\'t exist")
	print ("copy /rename " + config_filename + ".sample and edit\n")
	sys.exit(1)

else:
	try:
		print ("Loading config from " + config_filename + "\n")

		with open(config_filename, "r") as fp:
			config.readfp(fp)

		# Replace default values with config_file values
		host = config.get("SickBeard", "host")
		port = config.get("SickBeard", "port")
		api_key = config.get("SickBeard", "api_key")
		kodi_host = config.get("Kodi", "host")
		kodi_port = config.get("Kodi", "port")

		if not api_key:
			print ("Sick Beard api key setting is empty, please fill this field in settings.cfg")
			sys.exit(1)

		if not kodi_host or not kodi_port:
			print ("Kodi host or port setting is empty, please fill this field in settings.cfg")
			sys.exit(1)

		try:
			ssl = int(config.get("SickBeard", "ssl"))
			use_pushover = int(config.get("Pushover", "use_pushover"))
			app_token = config.get("Autosub", "app_token")
			user_key = config.get("Pushover", "user_key")
			use_nma = int(config.get("NMA", "use_nma"))
			nma_api = config.get("NMA", "nma_api")
			nma_priority = config.get("NMA", "nma_priority")
			use_pushbullet = int(config.get("Pushbullet", "use_pushbullet"))
			ptoken = config.get("Pushbullet", "ptoken")
			channeltag = config.get("Pushbullet", "channeltag")
			deviceid = config.get("Pushbullet", "deviceid")
			subchanneltag = config.get("Autosub", "channeltag")

		except (configparser.NoOptionError, ValueError):
			pass

		try:
			web_root = config.get("SickBeard", "web_root")
			if not web_root.startswith("/"):
				web_root = "/" + web_root

			if not web_root.endswith("/"):
				web_root = web_root + "/"

		except configparser.NoOptionError:
			pass

	except EnvironmentError:
		e = sys.exc_info()[1]
		print ("Could not read configuration file: " + str(e))
		# There was a config_file, don't use default values but exit
		sys.exit(1)

if ssl:
	protocol = "https://"
else:
	protocol = "http://"

url = protocol + host + ":" + port + web_root + "api/" + api_key + "/?"

print ("Opening URL: " + url)

#first, define needed variables
subandpath= sys.argv[1]
vidandpath= sys.argv[2]
show = sys.argv[4]
epis = sys.argv[6]
season = sys.argv[5]
newsubandpath= subandpath+'.utf8'
subandpathnoext = sys.argv[1] [:-7]
outputfileandpath = subandpathnoext+".nl.mkv"
finalfileandpath = subandpathnoext+".mkv"
pathvid = os.path.dirname(vidandpath)

#muxing vid and sub in new file (vid.nl.mkv)
subprocess.call(['mkvmerge', '-o', outputfileandpath, '--language', '-1:eng', vidandpath , '--language', '0:nld', subandpath])

'''
the conversion to prevent 'strange' chars is not neccesary anymore on my system.
# convert sub to utf-8
#subprocess.call(['iconv', '-c', '-f', 'ISO-8859-1', '-t', 'UTF-8', subandpath, '-o', newsubandpath])
#os.remove(subandpath)
#os.rename(newsubandpath, subandpath)
'''
#remove original video (without the subs)
os.remove(vidandpath)
#put the new file where the old file was (else subs keep downloading)
os.rename(outputfileandpath, finalfileandpath)
#change final permissions
os.chmod(finalfileandpath, 0775)
os.chmod(subandpath, 0775)

#aquire tvdbid from sickbeard
params = urlencode({'cmd': 'sb.searchtvdb', 'lang': 'nl', 'name': show})
r = urllib2.urlopen(url, params).read()
r = json.loads(r)
tvdbid = str(r['data']['results'][0]['tvdbid'])


#aquire episode name from sickbeard
params = urlencode({'cmd': 'episode', 'tvdbid': tvdbid, 'season': season, 'episode': epis})
t = urllib2.urlopen(url, params).read()
t = json.loads(t)
epname= str(t['data']['name'])

# remove and update episode in xbmc (filename did not change so automatic update does not work)
if vidandpath.endswith('.mkv') :
    data = {
        "jsonrpc":"2.0",
        "method":"VideoLibrary.GetEpisodes",
        "params":{"sort": {"order": "ascending", "method": "title"}, "filter": {"operator": "contains", "field": "title", "value": epname}, "properties": ["file"]},
        "id" : 1
    }
    req = urllib2.Request('http://'+kodi_host+':'+kodi_port+'/jsonrpc')
    req.add_header('Content-Type', 'application/json')
    r2 = urllib2.urlopen(req, json.dumps(data))
    r2 = r2.read()
    r2 = json.loads(r2)
    xbmcepid = r2['result']['episodes'][0]['episodeid']

    data = {
        "jsonrpc":"2.0",
        "method":"VideoLibrary.RemoveEpisode",
        "params":{"episodeid" : xbmcepid },
        "id" : 1
    }
    req = urllib2.Request('http://'+kodi_host+':'+kodi_port+'/jsonrpc')
    req.add_header('Content-Type', 'application/json')
    r3 = urllib2.urlopen(req, json.dumps(data))
    r3 = r3.read()
    r3 = json.loads(r3)

else :
    pass

#update xbmc (only the path)
try:
    data = {
        "jsonrpc":"2.0",
        "method":"VideoLibrary.Scan",
        "params":{"directory":pathvid},
        "id" : 1
    }
    req = urllib2.Request('http://'+kodi_host+':'+kodi_port+'/jsonrpc')
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req, json.dumps(data))
    status = ""

except:
    print ("Can't reach Kodi")
    status = "!"

finally:

	if use_pushover == 1:
		print ("Sending Pushover notification...")
		pushurl= "http://thetvdb.com/?tab=series&id="+tvdbid+"&lid=13"
		pushmsg= show+' '+season+'x'+epis+' '+epname+' '+status

		conn = httplib.HTTPSConnection("api.pushover.net:443")
		conn.request("POST", "/1/messages.json",
		urllib.urlencode({
			"token": app_token,
			"user": user_key,
			"message": pushmsg,
			"url": pushurl,
			"url_title": show,
			"sound": "Piano Bar",
		}), { "Content-type": "application/x-www-form-urlencoded" })
		conn.getresponse()
	if use_pushbullet == 1:
		data = urllib.urlencode({
			'type': 'note',
			'title': show,
			'body': epname+" ("+season+"x"+epis")",
			'device_id': deviceid,
			'channel_tag': subchanneltag
			})
		auth = base64.encodestring('%s:' % ptoken).replace('\n', '')
		req = urllib2.Request('https://api.pushbullet.com/v2/pushes', data)
		req.add_header('Authorization', 'Basic %s' % auth)
		response = urllib2.urlopen(req)
		res = json.load(response)
		if 'error' in res:
			print ("Pushbullet notification failed")
		else:
			print ("Pushbullet notification sucesfully sent")
	if use_nma == 1:
		print ("Sending NMA notification...")
		from lib.pynma import pynma
		p = pynma.PyNMA(nma_api)
		p.push(app, show, pushmsg, 0, 1, nma_priority )
