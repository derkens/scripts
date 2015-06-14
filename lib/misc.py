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
		elif h.__class__.__name__ == 'myFileHandler':
			log_file = h.baseFilename
			break

	return log_file


def access_log_for_all():
	log_file = find_logfile()
	if not oct(stat.S_IMODE(os.stat(find_logfile()).st_mode)) == "0777":
		logger.logging.debug ("Changing logfile permissions")
		os.chmod(log_file, 0777)


def replace(pushtitle, pushmsg, **args):
	pushtitle = pushtitle.replace("{SHOW}", args['showname'])
	pushtitle = pushtitle.replace("{SEASON}", str("%02d" % args.get('season', 0)))
	pushtitle = pushtitle.replace("{EPIS}", str("%02d" % args.get('epnum', 0)))
	pushtitle = pushtitle.replace("{EPNAME}", args.get('epname', ''))
	pushtitle = pushtitle.replace("{LANG}", args.get('lang', ''))
	pushtitle = pushtitle.replace("{QLTY}", args.get('qlty', ''))

	pushmsg = pushmsg.replace("{SHOW}", args['showname'])
	pushmsg = pushmsg.replace("{SEASON}", str("%02d" % args.get('season', 0)))
	pushmsg = pushmsg.replace("{EPIS}", str("%02d" % args.get('epnum', 0)))
	pushmsg = pushmsg.replace("{EPNAME}", args.get('epname', ''))
	pushmsg = pushmsg.replace("{LANG}", args.get('lang', ''))
	pushmsg = pushmsg.replace("{QLTY}", args.get('qlty', ''))
	return pushtitle, pushmsg
