#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#<derkens@gmail.com>
#Notifies you if there are any 'missed' episodes
#
# shamelessly incorporated stuff from Sick Beard AutoProcessTV
# Author: Nic Wolfe <nic@wolfeden.ca>
# URL: http://code.google.com/p/sickbeard/

import os.path
import sys
import httplib, urllib, urllib2, json, logging
import logging.config

logging.config.fileConfig("lib/logger/logging.conf")
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
	logger.error (config_filename + " doesn\'t exist")
	logger.error ("copy /rename " + config_filename + ".sample and edit\n")
	sys.exit(1)

else:
	try:
		logging.info ("\n Loading config from " + config_filename + "\n")

		with open(config_filename, "r") as fp:
			config.readfp(fp)

		# Replace default values with config_file values
		host = config.get("SickBeard", "host")
		port = config.get("SickBeard", "port")
		api_key = config.get("SickBeard", "api_key")

		if not api_key:
			logging.error ("Sick Beard api key setting is empty, please fill this field in settings.cfg")
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
		logging.error ("Could not read configuration file: " + str(e))
		# There was a config_file, don't use default values but exit
		sys.exit(1)

if ssl:
	protocol = "https://"
else:
	protocol = "http://"

url = protocol + host + ":" + port + web_root + "api/" + api_key + "/?"

logging.info ("Opening URL: " + url + "\n")

params = urlencode({ 'cmd': 'future', 'type': 'missed' })
t = urllib2.urlopen(url, params).read()
t = json.loads(t)
logging.debug(t)
mis= list(t['data']['missed'])
logging.debug(mis)
if mis == "[]" :
	logging.info("Nothing to be done, exiting")
	exit()


else:
	for index, string in enumerate(mis):
		show = str(mis[index]['show_name']) ; logging.debug("show = " + show)
		seas = str(mis[index]['season']) ; logging.debug("season = " + seas)
		epis = str(mis[index]['episode']) ; logging.debug("episode = " + epis)
		epname = str(mis[index]['ep_name']) ; logging.debug("episode name = " + epname)
		pushtitle = 'Sick Beard - gemist'
		pushmsg = '!'+show+' '+seas+'x'+epis+' '+epname
		logging.debug(pushmsg)
		if use_pushover == 1:
			logging.info ("Sending Pushover notification...")
			conn = httplib.HTTPSConnection("api.pushover.net:443")
			conn.request("POST", "/1/messages.json",
				urllib.urlencode({
					"token": app_token,
					"user": user_key,
					"message": pushmsg,
					"title" : pushtitle,
				}), { "Content-type": "application/x-www-form-urlencoded" })
			conn.getresponse()
		if use_nma == 1:
			logging.info ("Sending NMA notification...")
			from lib.pynma import pynma
			p = pynma.PyNMA(nma_api)
			p.push(app, pushtitle, pushmsg, 0, 1, nma_priority )
