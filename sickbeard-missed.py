#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#<derkens@gmail.com>
#Notifies you if there are any 'missed' episodes
#
#todo: nma support

import requests, httplib, urllib

sickbeardip = "only sickbeard ip here"
sickbeardapikey =  "sickbeard api key here"
pushovertoken = "your app token here"
pushoveruser = "your user key here"

payload = {'cmd': 'future', 'type': 'missed' }
t = requests.get("http://"+sickbeardip+"/sickbeard//api/"+sickbeardapikey+"/?", params=payload)
t = t.json()
mis2 = list(t['data'])
mis= str(t['data']['missed'])
if mis == "[]" :
    exit()


else:
    for index, string in enumerate(down):
        show = str(mis2['missed'][index]['show_name'])
        seas = str(mis2['missed'][index]['season'])
        epis = str(mis2['missed'][index]['episode'])
        epname = str(mis2['missed'][index]['ep_name'])
        pushtitle = 'Sick Beard - gemist'
        pushmsg = '!'+show+' '+seas+'x'+epis+' '+epname
        print pushmsg
        conn = httplib.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
            urllib.urlencode({
                "token": pushovertoken,
                "user": pushoveruser,
                "message": pushmsg,
                "title" : pushtitle,
            }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()

