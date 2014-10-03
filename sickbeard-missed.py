#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#<derkens@gmail.com>
#Notifies you if there are any 'missed' episodes
#
#todo: nma support

import requests, httplib, urllib

sickbeardip = "only sickbeard ip here"
sickbeardapikey =  "sickbeard api key here"
use_pushover = 0
pushovertoken = "your app token here"
pushoveruser = "your user key here"
use_nma = 0
nma_api = ""
nma_priority = 0
app = "SickBeard"

if use_nma == 1:
    import pynma

payload = {'cmd': 'future', 'type': 'missed' }
t = requests.get("http://"+sickbeardip+"/sickbeard//api/"+sickbeardapikey+"/?", params=payload)
t = t.json()
mis= list(t['data']['missed'])
if mis == "[]" :
    exit()


else:
    for index, string in enumerate(down):
        show = str(mis[index]['show_name'])
        seas = str(mis[index]['season'])
        epis = str(mis[index]['episode'])
        epname = str(mis[index]['ep_name'])
        pushtitle = 'Sick Beard - gemist'
        pushmsg = '!'+show+' '+seas+'x'+epis+' '+epname
        print pushmsg
		if use_pushover == 1
			conn = httplib.HTTPSConnection("api.pushover.net:443")
			conn.request("POST", "/1/messages.json",
				urllib.urlencode({
					"token": pushovertoken,
					"user": pushoveruser,
					"message": pushmsg,
					"title" : pushtitle,
				}), { "Content-type": "application/x-www-form-urlencoded" })
        			conn.getresponse()
		if use_nma == 1
			p = pynma.PyNMA(nma_api)
            		p.push(app, pushtitle, pushmsg, 0, 1, nma_priority )

