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
url = list(
    set(os.environ.get("URL", "https://subsplease.org/rss/?r=sd").split("|"))
)

token = os.environ.get("BOT_TOKEN")
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

n = Client(
    "AutoAnime",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=token,

)

for kk in url:
    if db.get(kk) is None:
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
    kk_name = name.replace("[SubsPlease]", "") if "[SubsPlease]" in name else name
    if "(" in kk_name:
       filename = kk_name.rsplit("(", 1)[0]
    else:
       file_name = kk_name
    title = f"{file_name}"
    await message.copy(log_group, caption=title)


@n.on_message((filters.video) & filters.chat(log_group) & filters.incoming & ~filters.forwarded)
async def n(client, message):
  media = message.video
  title = f"{message.caption}"
  await message.copy(log_channel, caption=title)

prvt_message = '''
Hello there, I am Anime Uploaded Bot for lol I upload latest Animes there. If you liked my work.
Developer : @Madepranav
Language : python
Framework : pyrogram
'''
grp_message = '''
Hello there, I am Anime Uploaded Bot for lmeo
'''

@n.on_message(filters.command(["start"], prefixes=["/", "!"]))
async def start(client, message):
    self = await bot.get_me()
    busername = self.username
    if message.chat.type != "private":
        await message.reply_text(grp_message)
        return
    else:
        buttons = [[InlineKeyboardButton("Dev", url="https://t.me/madepranav"),
                    ]]
        await message.reply_text(prvt_message, reply_markup=InlineKeyboardMarkup(buttons))


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





  













   

