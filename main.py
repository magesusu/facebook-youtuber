from __future__ import unicode_literals

import youtube_dl
import youtube_upload.main as yup

import pytz
from datetime import datetime, timezone
import requests
import json
import csv
import configparser
import optparse

CONFIG_LOCATION = "/home/ssr990/.config/facebook-youtuber/"
UPLOADED_LIST_LOCATION = CONFIG_LOCATION + "UploadedVideoId.csv"
LOCAL_VIDEO_LOCATION = "/home/ssr990/videos"

config = configparser.ConfigParser()
config.read(CONFIG_LOCATION + 'config.ini', 'UTF-8')
ACCESS_TOKEN = config['facebook_app']['ACCESS_TOKEN']
USER_ID = config['facebook_app']['USER_ID']

API_VIDEO_LIST_URL = "https://graph.facebook.com/v2.12/" + USER_ID + "/videos?limit=99999999999999&access_token=" + ACCESS_TOKEN

cue = []
# Get video URLs from Facebook
headers = {"content-type": "application/json"}
videos = requests.get(API_VIDEO_LIST_URL, headers=headers).json()

# Get re-uploaded video ids
with open(UPLOADED_LIST_LOCATION) as f:
    exsistedIds = f.read().split('\n')

    for video in videos['data']:
        isExsist = False
        id = video['id']
        for exsistedId in exsistedIds:
            if exsistedId == id:
                isExsist = True
                break
        if isExsist == False:
            cue.append(id)
            print("[cue]" + id)


with open(UPLOADED_LIST_LOCATION,'a') as f:
    for id in cue:
        # Download the video
        title = ""
        savepath = LOCAL_VIDEO_LOCATION + "/" + id + ".mp4"
        dl = 'https://www.facebook.com/' + USER_ID + '/videos/' + id
        ydl_opts = {'outtmpl': savepath,}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(dl)

        # Upload the video
        yup_opts = ['--title', meta['title'], '--recording-date', datetime.fromtimestamp(meta['timestamp'], timezone.utc).isoformat(timespec='microseconds'), '--description', 'This video is a reproduction of our Facebook video.\nOriginal URL: ' + dl, savepath]
        url = yup.main(yup_opts)
        f.write(id + "\n")
        print("Uploaded: ["+ id +"]" + meta['title'])
