# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import config, db
from handlers import *
from scheduler import schedule_jobs

def main():
    db.init_db()
    updater = Updater(token=config.BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("edit", edit))
    dp.add_handler(CommandHandler("edabout", edabout))
    dp.add_handler(CommandHandler("about", about))
    dp.add_handler(CommandHandler("edcontact", edcontact))
    dp.add_handler(CommandHandler("contact", contact))
    dp.add_handler(CommandHandler("edverse", edverse))
    dp.add_handler(CommandHandler("verse", verse))
    dp.add_handler(CommandHandler("edevents", edevents))
    dp.add_handler(CommandHandler("events", events))
    dp.add_handler(CommandHandler("edbirthday", edbirthday))
    dp.add_handler(CommandHandler("birthday", birthday))
    dp.add_handler(CommandHandler("pray", pray))
    dp.add_handler(CommandHandler("praylist", praylist))
    dp.add_handler(CommandHandler("edquiz", edquiz))
    dp.add_handler(CommandHandler("quiz", quiz))
    dp.add_handler(CommandHandler("answer", answer))
    dp.add_handler(CommandHandler("Tops", tops))
    dp.add_handler(CommandHandler("broadcast", broadcast))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("report", report))
    dp.add_handler(CommandHandler("backup", backup))
    dp.add_handler(CommandHandler("restore", restore))
    dp.add_handler(CommandHandler("allclear", allclear))

    # For restore: accept document with caption /restore
    dp.add_handler(MessageHandler(Filters.document & Filters.caption_regex(r"^/restore"), restore))

    # Start scheduler jobs
    schedule_jobs(updater.job_queue)

    updater.start_polling()
    print("Bot started...")
    updater.idle()

if __name__ == "__main__":
    main()
