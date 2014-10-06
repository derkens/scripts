#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#<derkens@gmail.com>
#show cancelled? this script notifies you and put the show in 'pause' (after the last ep oc.)
#
# shamelessly incorporated stuff from Sick Beard AutoProcessTV
# Author: Nic Wolfe <nic@wolfeden.ca>
# URL: http://code.google.com/p/sickbeard/

import os.path
import sys
import httplib, urllib, urllib2, json

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

		if not api_key:
			print ("Sick Beard api key setting is empty, please fill this field in settings.cfg")
			sys.exit(1)

		try:
			ssl = int(config.get("SickBeard", "ssl"))
			use_pushover = int(config.get("Pushover", "use_pushover"))
			app_token = config.get("SickBeard", "app_token")
			user_key = config.get("Pushover", "user_key")
			use_nma = int(config.get("NMA", "use_nma"))
			nma_api = config.get("NMA", "nma_api")
			nma_priority = config.get("NMA", "nma_priority")

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

params = urlencode({'cmd': 'shows', 'sort': 'name', 'paused': '0'})
t = urllib2.urlopen(url, params).read()
t = json.loads(t)
end = filter( lambda x: x['status']=='Ended', t['data'].values() )
if end == []:
	print("Nothing to be done, exiting")
	exit()
for i in end :
	show = i['show_name']
	stat = i['status']
	net = i['next_ep_airdate']
	if net == '':
		params = urlencode({'cmd': 'sb.searchtvdb', 'lang': 'nl', 'name': show})
		r = urllib2.urlopen(url, params).read()
		r = json.loads(r)
		tvdbid = str(r['data']['results'][0]['tvdbid'])
		params = urlencode({'cmd': 'show.pause', 'tvdbid': tvdbid, 'pause': 1})
		s = urllib2.urlopen(url, params).read()
		if use_pushover == 1:
			conn = httplib.HTTPSConnection("api.pushover.net:443")
			conn.request("POST", "/1/messages.json",
				urllib.urlencode({
					"token": app_token,
					"user": user_key,
					"message": show+msgsuffix,
					"title" : 'Sick Beard',
				}), { "Content-type": "application/x-www-form-urlencoded" })
			conn.getresponse()
		if use_nma == 1:
			print ("Sending NMA notification...")
			from lib.pynma import pynma
			p = pynma.PyNMA(nma_api)
			p.push(app, show+msgsuffix, show+msgsuffix, 0, 1, nma_priority )


