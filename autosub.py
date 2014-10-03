#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#<derkens@gmail.com>
#post processing script for autosub (https://code.google.com/p/autosub-bootstrapbill/)
#wat it does: When a subtitle is downloaded, sub is muxed into a new mkv. This is so Kodi can use the subtile information in metadat for the skin (shows you an icon with sub language depending on your skin)
#it will update the xbmc database accordingly
#Todo: put language in a variable


import sys, os, subprocess, json, urllib2, requests
import httplib, urllib

#owninfo:
sickbeardip = "only sickbeard ip here"
sickbeardapikey = "sickbeard api key here"
xbmcip = "only xbmc ip"
xbmcport = "only xbmc port"
pushovertoken ="pushover app token here"
pushoveruser = "pushover user key here"
localstorage = "where are the series?"

#first, define needed variables
subandpath= sys.argv[1]
vidandpath= sys.argv[2]
show = sys.argv[4]
epis = sys.argv[6]
season = sys.argv[5]
newsubandpath= subandpath+'.utf8'
subandpathnoext = sys.argv[1] [:-7]
outputfileandpath = subandpathnoext+".nl.mkv"
finalfileandpath = subandpathnoext+".mkv"
pathvid = os.path.dirname(vidandpath)

#muxing vid and sub in new file (vid.nl.mkv)
subprocess.call(['mkvmerge', '-o', outputfileandpath, '--language', '-1:eng', vidandpath , '--language', '0:nld', subandpath])

''' the conversion to prevent 'strange' chars is not neccesary anymore on my system.
# convert sub to utf-8
#subprocess.call(['iconv', '-c', '-f', 'ISO-8859-1', '-t', 'UTF-8', subandpath, '-o', newsubandpath])
#os.remove(subandpath)
#os.rename(newsubandpath, subandpath)
'''
#remove original video (without the subs)
os.remove(vidandpath)
#put the new file where the old file was (else subs keep downloading)
os.rename(outputfileandpath, finalfileandpath)
#change final permissions
os.chmod(finalfileandpath, 0775)
os.chmod(subandpath, 0775)

#aquire tvdbid from sickbeard
payload = {'cmd': 'sb.searchtvdb', 'lang': 'nl', 'name': show}
r = requests.get("http://"+sickbeardip+"/sickbeard//api/"+sickbeardapikey+"/?", params=payload)
r = r.json()
tvdbid = str(r['data']['results'][0]['tvdbid'])


#aquire episode name from sickbeard
payload = {'cmd': 'episode', 'tvdbid': tvdbid, 'season': season, 'episode': epis}
t = requests.get("http://"+sickbeardip+"/sickbeard//api/"+sickbeardapikey+"/?", params=payload)
t = t.json()
epname= str(t['data']['name'])

# remove and update episode in xbmc (filename did not change so automatic update does not work)
if vidandpath.endswith('.mkv') :
    data = {
        "jsonrpc":"2.0",
        "method":"VideoLibrary.GetEpisodes",
        "params":{"sort": {"order": "ascending", "method": "title"}, "filter": {"operator": "contains", "field": "title", "value": epname}, "properties": ["file"]},
        "id" : 1
    }
    req = urllib2.Request('http://'+xbmcip+':'+xbmcport+'/jsonrpc')
    req.add_header('Content-Type', 'application/json')
    r2 = urllib2.urlopen(req, json.dumps(data))
    r2 = r2.read()
    r2 = json.loads(r2)
    xbmcepid = r2['result']['episodes'][0]['episodeid']

    data = {
        "jsonrpc":"2.0",
        "method":"VideoLibrary.RemoveEpisode",
        "params":{"episodeid" : xbmcepid },
        "id" : 1
    }
    req = urllib2.Request('http://'+xbmcip+':'+xbmcport+'/jsonrpc')
    req.add_header('Content-Type', 'application/json')
    r3 = urllib2.urlopen(req, json.dumps(data))
    r3 = r3.read()
    r3 = json.loads(r3)

else :
    pass

#update xbmc (only the path)
try:
    data = {
        "jsonrpc":"2.0",
        "method":"VideoLibrary.Scan",
        "params":{"directory":localstorage},
        "id" : 1
    }
    req = urllib2.Request('http://'+xbmcip+':'+xbmcport+'/jsonrpc')
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req, json.dumps(data))
    status = ""

except:
    print "can't reach xbmc"
    status = "!"

finally:

    pushurl= "http://thetvdb.com/?tab=series&id="+tvdbid+"&lid=13"
    pushmsg= show+' '+season+'x'+epis+' '+epname+' '+status

    conn = httplib.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
      urllib.urlencode({
        "token": pushovertoken,
        "user": pushoveruser,
        "message": pushmsg,
        "url": pushurl,
        "url_title": show,
        "sound": "Piano Bar",
      }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()
