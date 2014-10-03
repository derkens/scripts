#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#<derkens@gmail.com>
#show cancelled? this script notifies you and put the show in 'pause' (after the last ep oc.)
#
#Todo: nma support

import requests, json, urllib, httplib


sickbeardip = "only sickbeard ip here"
sickbeardapikey =  "sickbeard api key here"
use_pushover = 0
pushovertoken = "your app token here"
pushoveruser = "your user key here"
msgsuffix = " is cancelled"
use_nma = 0
nma_api = ""
nma_priority = 0
app = "SickBeard"

if use_nma == 1:
    import pynma
	
payload = {'cmd': 'shows', 'sort': 'name', 'paused': '0'}
t = requests.get("http://"+sickbeardip+"/sickbeard//api/"+sickbeardapikey+"/?", params=payload)
t = t.json()
end = filter( lambda x: x['status']=='Ended', t['data'].values() )
for i in end :
    show = i['show_name']
    stat = i['status']
    net = i['next_ep_airdate']
    if net == '':
        payload = {'cmd': 'sb.searchtvdb', 'lang': 'nl', 'name': show}
        r = requests.get("http://"+sickbeardip+"/sickbeard//api/"+sickbeardapikey+"/?", params=payload)
        r = r.json()
        tvdbid = str(r['data']['results'][0]['tvdbid'])
        payload = {'cmd': 'show.pause', 'tvdbid': tvdbid, 'pause': 1}
        s = requests.get("http://"+sickbeardip+"/sickbeard//api/"+sickbeardapikey+"/?", params=payload)
		if use_pushover == 1
        conn = httplib.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
            urllib.urlencode({
                "token": pushovertoken,
                "user": pushoveruser,
                "message": show+msgsuffix,
                "title" : 'Sick Beard',
            }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()
		if use_nma == 1
			p = pynma.PyNMA(nma_api)
            p.push(app, show+msgsuffix, show+msgsuffix, 0, 1, nma_priority )
    else:
        exit()

