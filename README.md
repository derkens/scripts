These are some personal scripts I've *cut and pasted* and *trial'd and error'd* together.
Using this as backup and share site.
The script are all SickBeard and SickRage compatible. Let me know if you encounter problems.

*note: The autosub script is very personal and probably won't work for you..'*

####General####

When you want to use the script, clone the repository and leave the file structure intact. The scripts will fail if files or directories are missing.

First you should edit settings.cfg.sample and save to settings.cfg.

####sickbeard-missed####

When this script is run, it will collect the episodes SickBeard missed, as it shows in 'Coming Episodes'.
It will only notify you of shows you missed, it won't take any action.
You can put this script in crontab or systemd timer and run it daily after your normal download timeframe.
Currently the only notifiers to choose are [pushover](http://www.pushover.net), [notify my android](http://www.notifymyandroid.com), [pushbullet](http://www.pushbullet.com) and e-mail

####sickbeard-cancelled####

When this script is run, it will checkout the status of shows in the SickBeard showlist through the API (only not paused shows).
When it encounters shows as ended, it will check if the last episode is aired (eg. no next airdate).
It will then put the show on pause, to prevent it beiing checked again next time the script is executed.
Currently the only notifiers to choose are [pushover](http://www.pushover.net), [notify my android](http://www.notifymyandroid.com), [pushbullet](http://www.pushbullet.com) and e-mail

####sickbeard-snatched2wanted####

This script gets episodes with the status 'snatched' (on failed downloads) and sets the status back to wanted.
what it does, it gets a list from the api out of the history with status *'Downloaded'*, Then it will get a list with status *'snatched'* from the history.
both limited to 20 items for now
It crosschecks both lists and it remove items from the *'snatched'* list whom are also present on the *'downloaded'* list.
The remaining items are checked one at a time for episode status for security (one at a time for this is a SickBeard api limitation)
After that the remaining episode that have status *'snatched'*, are put to wanted. This also triggers a backlog search.
Currently the only notifiers to choose are [pushover](http://www.pushover.net), [notify my android](http://www.notifymyandroid.com), [pushbullet](http://www.pushbullet.com) and e-mail

####sickrage-pp####

This is a post-process script you can add to the post-process of sickrage. This was first a way to get a customized notification when an episode was downloaded. Once I noticed this script is always run when post-processing (automatic or manual) We have implemented some api calls to transmission torrent downloader to clear the torrent list.
Currently the only notifiers to choose are [pushover](http://www.pushover.net), [notify my android](http://www.notifymyandroid.com), [pushbullet](http://www.pushbullet.com) and e-mail

####github_notifier####

Gets the pushes and wiki edits from your personal stream (pushes and wiki edits from repos you follow) and notifies with pushover.

####ToDo####
[ ] check for presence of external tools (mkvmerge)
[ ] obfuscate api keys in logfile (in progress)
[ ] implement sound choice for pushover
[ ] reorganize settings.cfg
[ ] merge movie scripts

* thanks for contributing @Mickroz
