#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  misc.py
#
import logging
import lib.logger.logger as logger
import lib.config as config
import stat
import os

def find_logfile():
	log_file = None
	logger = logging.getLogger('logger')
	for h in logger.__dict__['handlers']:
		if h.__class__.__name__ == 'FileHandler':
			log_file = h.baseFilename
			break
		elif h.__class__.__name__ == 'RotatingFileHandler':
			log_file = h.baseFilename
			break

	return log_file

def access_log_for_all():
	log_file = find_logfile()
	if not oct(stat.S_IMODE(os.stat(find_logfile()).st_mode)) == "0777":
		logger.logging.debug ("Changing logfile permissions")
		os.chmod(log_file, 0777)

def replace(*args):
	lang = ""
	if len(args) == 4:
		showname,season,epnum,epname = args
	if len(args) == 5:
		showname,season,epnum,epname,lang = args
	pushtitle = config.push_title
	pushtitle = pushtitle.replace("{SHOW}", showname)
	pushtitle = pushtitle.replace("{SEASON}", str(season))
	pushtitle = pushtitle.replace("{EPIS}", str(epnum))
	pushtitle = pushtitle.replace("{EPNAME}", epname)
	pushtitle = pushtitle.replace("{LANG}", lang)

	pushmsg = config.push_msg
	pushmsg = pushmsg.replace("{SHOW}", showname)
	pushmsg = pushmsg.replace("{SEASON}", str(season))
	pushmsg = pushmsg.replace("{EPIS}", str(epnum))
	pushmsg = pushmsg.replace("{EPNAME}", epname)
	pushmsg = pushmsg.replace("{LANG}", lang)
	return pushtitle, pushmsg
