#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#<derkens@gmail.com>
#When a download failes in Sabnzbd (or Nzbget for that matter) the episode status remaines 'snatched' indefinitly.
#This script will put the status back to 'wanted'
#Put this in your cron to run daily (or systemd timer) and forget
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
topic = "changed status to wanted"

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
			app_token = config.get("Pushover", "app_token")
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

#url = "http://"+sickbeardip+":8081/api/"+sickbeardapikey+"/?"
params = urlencode({ 'cmd': 'history', 'type': 'downloaded', 'limit': 20 })
t = urllib2.urlopen(url, params).read()
t = json.loads(t)
down = list(t['data'])

params = urlencode({ 'cmd': 'history', 'type': 'snatched', 'limit': 20 })
u = urllib2.urlopen(url, params).read()
u = json.loads(u)
snat = list(u['data'])

y = []
z = []

for index, string in enumerate(down):
	down2 = str(down[index]['show_name'])+'_'+str(down[index]['season'])+'_'+str(down[index]['episode'])+'_'+str(down[index]['tvdbid'])
	y.append(down2)

for index, string in enumerate(snat):
	snat2 = str(snat[index]['show_name'])+'_'+str(snat[index]['season'])+'_'+str(snat[index]['episode'])+'_'+str(snat[index]['tvdbid'])
	z.append(snat2)

onlysnat = list(set(z) - set(y))

for index, string in enumerate(onlysnat):
	temp1 = str(onlysnat[index])
	temp2 = temp1.rsplit('_')
	showname = str(temp2[0])
	season = str(temp2[1])
	epis = str(temp2[2])
	tvdbid = str(temp2[3])
	params = urllib.urlencode({'cmd': 'episode', 'tvdbid': tvdbid, 'season': season, 'episode': epis, })
	w = urllib2.urlopen(url, params).read()
	w = json.loads(w)
	epstatus = str(w['data']['status'])
	epname = str(w['data']['name'])
	if epstatus == "Downloaded":
		pass
	else:
		params = urllib.urlencode({'cmd': 'episode.setstatus', 'tvdbid': tvdbid, 'season': season, 'episode': epis, 'status': 'wanted' })
		q = urllib2.urlopen(url, params).read()
		q = json.loads(q)
		message = showname+' '+season+'x'+epis+' '+epname+' is op wanted gezet, Check Sabnzbd...'
		print message
		if use_pushover == 1:
			print ("Sending Pushover notification...")
			conn = httplib.HTTPSConnection("api.pushover.net:443")
			conn.request("POST", "/1/messages.json",
				urllib.urlencode({
					"token": app_token,
					"user": user_key,
					"message": message,
					"title" : 'Sick Beard - wanted',
				}), { "Content-type": "application/x-www-form-urlencoded" })
			conn.getresponse()
		if use_nma == 1:
			print ("Sending NMA notification...")
			from lib.pynma import pynma
			p = pynma.PyNMA(nma_api)
			p.push(app, topic, message, 0, 1, nma_priority )
		else:
			pass
else:
	print ("Nothing to be done, exiting")
