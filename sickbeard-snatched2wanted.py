#!/usr/bin/env python
# -*- coding: utf-8 -*-
#<derkens@gmail.com>
#When a download failes in Sabnzbd (or Nzbget for that matter) the episode status remaines 'snatched' indefinitly.
#This script will put the status back to 'wanted'
#Put this in your cron to run daily (or systemd timer) and forget
#
#todo:

import requests, httplib, urllib

sickbeardip = "only sickbeard ip address"

pushover = "yes" #yes or no
pushovertoken = "your app token here"
pushoveruser = "your user key here"
sickbeardapikey= "sickbeard api key here"

nma = "no" #yes or no
nmakey = "your nma api key here"
app = "SickBeard"
topic = "changed status to wanted"
prio = "2"
if nma == "yes":
    import pynma


payload = {'cmd': 'history', 'type': 'downloaded', 'limit': 20 }
t = requests.get("http://"+sickbeardip+"/sickbeard//api/"+sickbeardapikey+"/?", params=payload)
t = t.json()
down = list(t['data'])

payload2 = {'cmd': 'history', 'type': 'snatched', 'limit': 20 }
u = requests.get("http://"+sickbeardip+"/sickbeard//api/"+sickbeardapikey+"/?", params=payload2)
u = u.json()
snat = list(u['data'])
y = []
z = []

for index, string in enumerate(down):
    down2 = str(down[index]['show_name'])+'_'+str(down[index]['season'])+'_'+str(down[index]['episode'])+'_'+str(down[index]['tvdbid'])
    y.append(down2)

for index, string in enumerate(snat):
    snat2 = str(snat[index]['show_name'])+'_'+str(snat[index]['season'])+'_'+str(snat[index]['episode'])+'_'+str(snat[index]['tvdbid'])
    z.append(snat2)

onlysnat = list(set(z) - set(y))

for index, string in enumerate(onlysnat):
    temp1 = str(onlysnat[index])
    temp2 = temp1.rsplit('_')
    showname = str(temp2[0])
    season = str(temp2[1])
    epis = str(temp2[2])
    tvdbid = str(temp2[3])
    payload3 = {'cmd': 'episode', 'tvdbid': tvdbid, 'season': season, 'episode': epis }
    w = requests.get("http://"+sickbeardip+"/sickbeard//api/"+sickbeardapikey+"/?", params=payload3)
    w = w.json()
    epstatus = str(w['data']['status'])
    epname = str(w['data']['name'])
    if epstatus == "Downloaded":
        pass
    else:
        payload4 = {'cmd': 'episode.setstatus', 'tvdbid': tvdbid, 'season': season, 'episode': epis, 'status': 'wanted' }
        q = requests.get("http://"+sickbeardip+"/sickbeard//api/"+sickbeardapikey+"/?", params=payload4)
        q = q.json()
        message = showname+' '+season+'x'+epis+' '+epname+' is op wanted gezet, Check Sabnzbd...'
        if pushover == "yes":

            conn = httplib.HTTPSConnection("api.pushover.net:443")
            conn.request("POST", "/1/messages.json",
                urllib.urlencode({
                    "token": pushovertoken,
                    "user": pushoveruser,
                    "message": message,
                    "title" : 'Sick Beard - wanted',
                }), { "Content-type": "application/x-www-form-urlencoded" })
            conn.getresponse()
        if nma == "yes":
            p = pynma.PyNMA(nmakey)
            p.push(app, topic, message, 0, 1, prio )
        else:
            pass
