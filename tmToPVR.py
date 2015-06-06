#!/usr/bin/env python2
import sys
import os
import time
import ConfigParser
import logging

configFilename = "/volume1/scripts/autoProcessTV/autoProcessTV.cfg"

import os.path
import sys
import os
import time
import lib.logger.logger as logger
import lib.config as config
import lib.emailer as emailer
import lib.misc as misc
import lib.api as api
from lib import requests

def transmission():
	
	dirName = os.getenv('TR_TORRENT_DIR')
	nzbName = os.getenv('TR_TORRENT_NAME')
	
	return (dirName, nzbName)
	
def main():
	logger.logging.info('Starting external PostProcess script ' + __file__)
		
	if not config.tv_dir:
		logger.logging.error('Fill in [SickbBeard] tv_download_dir in settings.cfg to use this Script. Aborting!')
		print 'Fill in [SickbBeard] tv_download_dir in settings.cfg to use this Script. Aborting!'
		time.sleep(3)
		sys.exit()

	if dirName is None:
		logger.logging.error('tmToPVR script need a dir to be run. Aborting!')
		print 'MediaToSickbeard script need a dir to be run. Aborting!'
		time.sleep(3)
		sys.exit()

	if "movies" in dirName:
		logger.logging.error('Found movies in dirName. Aborting!')
		print 'Found movies in dirName. Aborting!'
		time.sleep(3)
		sys.exit()

	if not os.path.isdir(dirName):
		logger.logging.error('Folder ' + dirName + ' does not exist. Aborting AutoPostProcess.')
		print 'Folder ' + dirName + ' does not exist. Aborting AutoPostProcess.'
		time.sleep(3)
		sys.exit()

	if nzbName and os.path.isdir(os.path.join(dirName, nzbName)):
		dirName = os.path.join(dirName, nzbName)
		
	params = {}
		
	params['quiet'] = 1
	
	params['dir'] = dirName
	if nzbName != None:
		params['nzbName'] = nzbName
	
	url = config.protocol + config.host + ":" + config.port + config.web_root + "/home/postprocess/processEpisode"
	login_url = config.protocol + config.host + ":" + config.port + config.web_root + "/login"
	
	logger.logging.debug("Opening URL: " + url + ' with params=' + str(params))   
	print "Opening URL: " + url + ' with params=' + str(params)
	
	try:
		sess = requests.Session()
		sess.post(login_url, data={'username': username, 'password': password}, stream=True, verify=False)
		response = sess.get(url, auth=(username, password), params=params, verify=False,  allow_redirects=False)
	except Exception, e:
		logger.logging.error(': Unknown exception raised when opening url: ' + str(e))
		time.sleep(3)
		sys.exit()
	
	if response.status_code == 302:
		logger.logging.error('Invalid Sickbeard Username or Password, check your config')
		print 'Invalid Sickbeard Username or Password, check your config'
		time.sleep(3)
		sys.exit()
	
	if response.status_code == 200:
		logger.logging.info('Script ' + __file__ + ' Succesfull')
		print 'Script ' + __file__ + ' Succesfull'
		time.sleep(3)
		sys.exit()
		
if __name__ == '__main__':
	main()
