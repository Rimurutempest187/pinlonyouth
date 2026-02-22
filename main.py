import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from handlers import *
from db import init_db
from config import BOT_TOKEN, LOG_FILE, TIMEZONE, MORNING_VERSE_HOUR, NIGHT_VERSE_HOUR
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

# logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename=LOG_FILE
)
logger = logging.getLogger(__name__)

def send_daily_verse(context):
    # send to all groups
    from utils import get_random_verse
    c = _conn.cursor()
    c.execute("SELECT chat_id FROM groups")
    groups = [r["chat_id"] for r in c.fetchall()]
    verse = get_random_verse()
    if not verse:
        return
    for gid in groups:
        try:
            context.bot.send_message(chat_id=gid, text=verse + CREATE_BY)
        except Exception:
            continue

def main():
    init_db()
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("edit", edit_cmd))
    dp.add_handler(CommandHandler("about", about))
    dp.add_handler(CommandHandler("edabout", edabout))
    dp.add_handler(CommandHandler("contact", contact))
    dp.add_handler(CommandHandler("edcontact", edcontact))
    dp.add_handler(CommandHandler("verse", verse))
    dp.add_handler(CommandHandler("edverse", edverse))
    dp.add_handler(CommandHandler("events", events))
    dp.add_handler(CommandHandler("edevents", edevents))
    dp.add_handler(CommandHandler("birthday", birthday))
    dp.add_handler(CommandHandler("edbirthday", edbirthday))
    dp.add_handler(CommandHandler("pray", pray))
    dp.add_handler(CommandHandler("praylist", praylist))
    dp.add_handler(CommandHandler("set", set_cmd))
    dp.add_handler(CommandHandler("quiz", lambda u,c: u.message.reply_text("Quiz will be auto triggered by message count." + CREATE_BY)))
    dp.add_handler(CommandHandler("edquiz", edquiz))
    dp.add_handler(CommandHandler("tops", tops))
    dp.add_handler(CommandHandler("broadcast", broadcast))
    dp.add_handler(CommandHandler("stats", stats_cmd))
    dp.add_handler(CommandHandler("report", report))
    dp.add_handler(CommandHandler("backup", backup_cmd))
    dp.add_handler(CommandHandler("restore", restore_cmd))
    dp.add_handler(CommandHandler("allclear", allclear))

    # Callback queries
    dp.add_handler(CallbackQueryHandler(callback_query_handler))

    # Message handler for counting in groups
    dp.add_handler(MessageHandler(Filters.text & (Filters.group | Filters.supergroup), message_counter))

    # Start scheduler for daily verses
    scheduler = BackgroundScheduler(timezone=pytz.timezone(TIMEZONE))
    # morning
    scheduler.add_job(lambda: send_daily_verse(updater.bot), CronTrigger(hour=MORNING_VERSE_HOUR, minute=0))
    # night
    scheduler.add_job(lambda: send_daily_verse(updater.bot), CronTrigger(hour=NIGHT_VERSE_HOUR, minute=0))
    scheduler.start()

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
