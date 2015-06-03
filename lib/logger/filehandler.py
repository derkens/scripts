#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  filehandler.py
#
import logging
import random
import os, sys
#import lib.config as config
import ConfigParser as configparser
config = configparser.RawConfigParser()
config_filename = os.path.join(os.path.dirname(sys.argv[0]), "settings.cfg")
with open(config_filename, "r") as fp:
	config.readfp(fp)
logpath = config.get("General", "logpath")
if logpath == "":
	logpath = os.path.join(os.path.dirname(sys.argv[0]))
logfile = config.get("General", "logfile")
class myFileHandler(logging.handlers.RotatingFileHandler):
	def __init__(self,path,fileName,mode,size,rest):
		path = logpath
		super(myFileHandler,self).__init__(os.path.join(path, logfile),mode,size,rest)
