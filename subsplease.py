import os
import feedparser
from sql import db
from time import sleep, time
from pyrogram.errors import FloodWait
from pyrogram import Client, filters, idle
from apscheduler.schedulers.background import BackgroundScheduler
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from decouple import config


logging.info("Starting...")
api_id = os.environ.get("APP_ID")
api_hash = os.environ.get("API_HASH")
url = list(set(i for i in os.environ.get("URL", "https://subsplease.org/rss/?r=sd").split("|")))
session = os.environ.get("SESSION")
log_group = int(os.environ.get("LOG_GROUP", None))
log_channel = int(os.environ.get("LOG_CHANNEL", None))
check_interval = int(os.environ.get("INTERVAL", 5))
max_instances = int(os.environ.get("MAX_INSTANCES", 5))

k = Client(
    session_name=session,
    api_id=api_id,
    api_hash=api_hash
)


for kk in url:
    if db.get(kk) == None:
        db.update(kk, "*")

def create_feed_checker(kk):
    def check_feed():
        FEED = feedparser.parse(kk)
        if len(FEED.entries) == 0:
            return
        entry = FEED.entries[0]
        if entry.id != db.get(kk).link:
            message = f"/magnet {entry.link}"
            try:
                app.send_message(log_channel, message)
                db.update(kk, entry.id)
            except FloodWait as e:
                print(f"FloodWait: {e.x} Seconds")
                sleep(e.x)
            except Exception as e:
                print(e)
        else:
            print(f"Checked: {entry.id}")
    return check_feed



@k.on_message((filters.video) & filters.chat(log_group) & filters.incoming & ~filters.forwarded)
async def n(client, message):
  media = message.video
  name = f"{message.caption}"
  if "[SubsPlease]" in name:
     kk_name = name.replace("[SubsPlease]", "")
  else:
     kk_name = name
  if "(" in kk_name:
     filename = kk_name.rsplit("(", 1)[0]
  else:
     file_name = kk_name
  title = f"{file_name}"
  await message.copy(log_channel, caption=title)



scheduler = BackgroundScheduler()
for kk in url:
    feed_checker = create_feed_checker(kk)
    scheduler.add_job(feed_checker, "interval", seconds=check_interval, max_instances=max_instances)
scheduler.start()
k.start()
n.start()
idle()
k.start()
n.stop()





  













   

