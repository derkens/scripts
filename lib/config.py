import os.path
import sys
import stat
import grp, pwd, os
import httplib, urllib, urllib2, json
import lib.logger.logger as logger


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

# Default values Sickbeard
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
	logger.logging.error(config_filename + " doesn\'t exist")
	logger.logging.error("copy /rename " + config_filename + ".sample and edit")
	sys.exit(1)


else:
	try:
		with open(config_filename, "r") as fp:
			config.readfp(fp)

		# Replace default values with config_file values
		host = config.get("SickBeard", "host")
		port = config.get("SickBeard", "port")
		api_key = config.get("SickBeard", "api_key")
		lvl = config.get("General", "loglevel")
		logger.logging.setLevel(lvl)
		githublogging = int(config.get("Github", "logging"))
		use_sickbeard = int(config.get("General", "use_sickbeard"))
		if 'github' in sys.argv[0] and not githublogging:
			logger.logging.setLevel("CRITICAL")
		logger.logging.debug("Loading config from " + config_filename)
		if use_sickbeard and not api_key:
			logger.logging.error("Sick Beard api key setting is empty, please fill this field in settings.cfg")
			sys.exit(1)

		try:
			ssl = int(config.get("SickBeard", "ssl"))
			use_pushover = int(config.get("Pushover", "use_pushover"))
			push_device = config.get("Pushover", "push_device")
			app_token = config.get("SickBeard", "app_token")
			user_key = config.get("Pushover", "user_key")
			use_nma = int(config.get("NMA", "use_nma"))
			nma_api = config.get("NMA", "nma_api")
			nma_priority = config.get("NMA", "nma_priority")
			use_kodi = int(config.get("Kodi", "use_kodi"))
			kodi_host = config.get("Kodi", "host")
			kodi_port = config.get("Kodi", "port")
			use_email = int(config.get("Email", "use_email"))
			from_address = str(config.get("Email", "from_address"))
			to_address = str(config.get("Email", "to_address"))
			smtp_ssl = int(config.get("Email", "ssl"))
			smtp_server = config.get("Email", "smtp_server")
			smtp_user = str(config.get("Email", "smtp_user"))
			smtp_pass = str(config.get("Email", "smtp_pass"))
			smtp_port = config.get("Email", "smtp_port")
			starttls = int(config.get("Email", "starttls"))
			use_pushbullet = int(config.get("Pushbullet", "use_pushbullet"))
			ptoken = config.get("Pushbullet", "ptoken")
			channeltag = config.get("Pushbullet", "channeltag")
			deviceid = config.get("Pushbullet", "deviceid")
			asapp_token = config.get("Autosub", "app_token")
			aschanneltag = config.get("Autosub", "channeltag")
			muxing = int(config.get("Autosub", "muxing"))
			aspush_title = str(config.get("Autosub", "push_title"))
			aspush_msg = str(config.get("Autosub", "push_msg"))
			aspush_sound = str(config.get("Autosub", "push_sound"))
			use_image_push = int(config.get("Autosub", "use_image_push"))
			temp_image = str(config.get("Autosub", "temp_image"))
			tm_host = config.get("Transmission", "host")
			tm_port = config.get("Transmission", "port")
			tm_user = config.get("Transmission", "username")
			tm_pass = config.get("Transmission", "password")
			tordir = str(config.get("Transmission", "tordir"))
			deltorrent = int(config.get("Transmission", "deletetorrents"))
			srpp_push_title = str(config.get("Sickrage-pp", "push_title"))
			srpp_push_msg = str(config.get("Sickrage-pp", "push_msg"))
			srpp_push_sound = str(config.get("Sickrage-pp", "push_sound"))
			sbca_push_title = str(config.get("Sickbeard-cancelled", "push_title"))
			sbca_push_msg = str(config.get("Sickbeard-cancelled", "push_msg"))
			sbca_push_sound = str(config.get("Sickbeard-cancelled", "push_sound"))
			sbs2w_push_title = str(config.get("Sickbeard-s2w", "push_title"))
			sbs2w_push_msg = str(config.get("Sickbeard-s2w", "push_msg"))
			sbs2w_push_sound = str(config.get("Sickbeard-s2w", "push_sound"))
			sbmis_push_title = str(config.get("Sickbeard-missed", "push_title"))
			sbmis_push_msg = str(config.get("Sickbeard-missed", "push_msg"))
			sbmis_push_sound = str(config.get("Sickbeard-missed", "push_sound"))
			tv_dir = str(config.get("SickBeard", "tv_download_dir"))
			username = str(config.get("SickBeard", "web_username"))
			password = str(config.get("SickBeard", "web_password"))
			githubuser = str(config.get("Github", "user"))
			githubapp_token = str(config.get("Github", "app_token"))
			github_push_sound = str(config.get("Github", "push_sound"))
			analyzeapptoken = config.get("Analyze-log", "apptoken")
			use_symlinks = int(config.get("Symlinks", "use_symlinks"))
			symdir = str(config.get("Symlinks", "symdir"))
			tvdbapi = str(config.get("Tvdb","tvdbapi"))


		except (configparser.NoOptionError, ValueError):
			logger.logging.exception("exception:")
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
		logger.logging.error("Could not read configuration file: " + str(e))
		# There was a config_file, don't use default values but exit
		sys.exit(1)

if ssl:
	protocol = "https://"
else:
	protocol = "http://"
