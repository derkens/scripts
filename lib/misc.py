#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  misc.py
#
import logging
import lib.logger.logger as logger
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
