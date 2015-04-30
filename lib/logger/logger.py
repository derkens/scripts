#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#<derkens@gmail.com>
#show cancelled? this script notifies you and put the show in 'pause' (after the last ep oc.)
#
# shamelessly incorporated stuff from Sick Beard AutoProcessTV
# Author: Nic Wolfe <nic@wolfeden.ca>
# URL: http://code.google.com/p/sickbeard/

import os, sys
import logging, logging.config
logconfpath = os.path.join(os.path.dirname(sys.argv[0]), "lib/logger/logging.conf")
logging.config.fileConfig(logconfpath)

import ConfigParser as configparser

config = configparser.RawConfigParser()
config_filename = os.path.join(os.path.dirname(sys.argv[0]), "settings.cfg")

with open(config_filename, "r") as fp:
	config.readfp(fp)

lvl = config.get("General", "loglevel")

logger1 = logging.getLogger("logger1")
logger2 = logging.getLogger("logger2")

if lvl == "DEBUG":
	logging = logger2
else:
	logging = logger1
