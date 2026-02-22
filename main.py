import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN, DATA_FILE, ADMIN_IDS
from utils.storage import load_data, save_data
from handlers.user_handlers import start, about, contact, verse, events, birthday, pray, praylist, quiz, report
from handlers.admin_handlers import (
    edit_cmds, edabout, edcontact, edverse, edevents, edbirthday, edquiz,
    tops, broadcast, stats, backup, restore, allclear
)
from handlers.scheduled_jobs import start_scheduler
from pathlib import Path

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def ensure_data_file():
    p = Path(DATA_FILE)
    if not p.exists():
        save_data(DATA_FILE, {
            "users": {},
            "groups": [],
            "verses": [],
            "quizzes": [],
            "events": [],
            "contacts": [],
            "birthdays": [],
            "prayers": [],
            "praylist": [],
            "reports": [],
            "scores": []
        })

async def track_chats(update, context):
    # When bot is added to group or receives message, store group id
    data = load_data(DATA_FILE)
    chat = update.effective_chat
    if chat and chat.type in ("group", "supergroup"):
        gid = chat.id
        groups = data.setdefault("groups", [])
        if gid not in groups:
            groups.append(gid)
            save_data(DATA_FILE, data)

async def handle_text_answers(update, context):
    # Simple handler to capture quiz answers (A/B/C/D)
    text = update.message.text.strip().upper()
    if text in ("A","B","C","D"):
        uid = str(update.effective_user.id)
        data = load_data(DATA_FILE)
        user = data.get("users", {}).get(uid, {})
        last_q = user.get("last_quiz")
        if not last_q:
            await update.message.reply_text("မည်သည့် Quiz ကို ဖြေဆိုနေသည်ကို မတွေ့ပါ။ /quiz ဖြင့် စတင်ပါ။")
            return
        correct = last_q.get("answer","").upper()
        if text == correct:
            # increment score
            scores = data.setdefault("scores", [])
            name = update.effective_user.username or update.effective_user.first_name
            # find existing
            found = next((s for s in scores if s.get("name")==name), None)
            if found:
                found["score"] = found.get("score",0) + 1
            else:
                scores.append({"name": name, "score": 1})
            save_data(DATA_FILE, data)
            await update.message.reply_text("မှန်ပါတယ် 🎉")
        else:
            await update.message.reply_text(f"မမှန်ပါ။ မှန်ကန်သော ဖြေကြောင်း: {correct}")

def main():
    ensure_data_file()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # user commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CommandHandler("verse", verse))
    app.add_handler(CommandHandler("events", events))
    app.add_handler(CommandHandler("birthday", birthday))
    app.add_handler(CommandHandler("pray", pray))
    app.add_handler(CommandHandler("praylist", praylist))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("report", report))

    # admin commands
    app.add_handler(CommandHandler("edit", edit_cmds))
    app.add_handler(CommandHandler("edabout", edabout))
    app.add_handler(CommandHandler("edcontact", edcontact))
    app.add_handler(CommandHandler("edverse", edverse))
    app.add_handler(CommandHandler("edevents", edevents))
    app.add_handler(CommandHandler("edbirthday", edbirthday))
    app.add_handler(CommandHandler("edquiz", edquiz))
    app.add_handler(CommandHandler("Tops", tops))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("backup", backup))
    app.add_handler(CommandHandler("restore", restore))
    app.add_handler(CommandHandler("allclear", allclear))

    # track groups when messages arrive
    app.add_handler(MessageHandler(filters.ChatType.GROUPS, track_chats))
    # handle simple quiz answers
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text_answers))

    # start scheduler
    start_scheduler(app)

    logger.info("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
