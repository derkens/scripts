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
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity",
							action="store_true")
args = parser.parse_args()

logger1 = logging.getLogger("logger1")
logger2 = logging.getLogger("logger2")

if args.verbose:
	logging = logger2
else:
	logging = logger1
