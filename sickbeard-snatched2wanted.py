#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#<derkens@gmail.com>
#When a download failes in Sabnzbd (or Nzbget for that matter) the episode status remaines 'snatched' indefinitly.
#This script will put the status back to 'wanted'
#Put this in your cron to run daily (or systemd timer) and forget
#
#todo:

import httplib, urllib, urllib2, json

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

url = "http://"+sickbeardip+"/sickbeard//api/"+sickbeardapikey+"/?"
params = urllib.urlencode({ 'cmd': 'history', 'type': 'downloaded', 'limit': 20 })
t = urllib2.urlopen(url, params).read()
t = json.loads(t)
down = list(t['data'])

params = urllib.urlencode({ 'cmd': 'history', 'type': 'snatched', 'limit': 20 })
u = urllib2.urlopen(url, params).read()
u = json.loads(u)
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
    params = urllib.urlencode({'cmd': 'episode', 'tvdbid': tvdbid, 'season': season, 'episode': epis, })
    w = urllib2.urlopen(url, params).read()
    w = json.loads(w)
    epstatus = str(w['data']['status'])
    epname = str(w['data']['name'])
    if epstatus == "Downloaded":
        pass
    else:
        params = urllib.urlencode({'cmd': 'episode.setstatus', 'tvdbid': tvdbid, 'season': season, 'episode': epis, 'status': 'wanted' })
        q = urllib2.urlopen(url, params).read()
        q = json.loads(q)
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
