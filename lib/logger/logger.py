#!/usr/bin/env python2
# -*- coding: utf-8 -*-


import os, sys
import logging, logging.config
logconfpath = os.path.join(os.path.dirname(sys.argv[0]), "lib/logger/logging.conf")
logging.config.fileConfig(logconfpath)

logging = logging.getLogger("logger")
