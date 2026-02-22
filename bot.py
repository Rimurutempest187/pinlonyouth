#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import random
import os
import asyncio
from datetime import datetime, time
from functools import wraps

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Load environment variables or set token here
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

DATA_FILE = "data/data.json"
LOG_FILE = "logs/bot.log"

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename=LOG_FILE
)
logger = logging.getLogger(__name__)

# Ensure data folder
os.makedirs("data", exist_ok=True)

# Utility functions for data persistence
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "admins": [],
                "groups": [],
                "contacts": [],
                "about": "",
                "verses": [],
                "events": [],
                "birthdays": [],
                "prayers": [],
                "quizzes": [],
                "quiz_scores": {},
                "settings": {},
                "message_counters": {},
                "reports": []
            }, f, ensure_ascii=False, indent=2)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# Admin check decorator
def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in data.get("admins", []):
            await update.message.reply_text("ဤ command ကို အသုံးပြုခွင့်မရှိပါ။\nCreate by : PINLON-YOUTH")
            return
        return await func(update, context)
    return wrapper

# Helper to append signature
def with_signature(text: str) -> str:
    return f"{text}\n\nCreate by : PINLON-YOUTH"

# Register group when bot added or message in group
async def register_group(chat_id: int):
    if chat_id not in data["groups"]:
        data["groups"].append(chat_id)
        save_data(data)

# Command handlers

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await register_group(update.effective_chat.id)
    text = (
        f"မင်္ဂလာပါ {user.first_name}!\n\n"
        "Church Community Bot သို့ ကြိုဆိုပါတယ်။\n\n"
        "အသုံးပြုနိုင်သော command များ -\n"
        "/about - အသင်းအကြောင်း\n"
        "/contact - တာဝန်ခံများဖုန်းနံပါတ်\n"
        "/verse - ယနေ့ဖတ်ရန်ကျမ်းချက်\n"
        "/events - လာမည့်အစီအစဉ်များ\n"
        "/birthday - ယခုလ မွေးနေ့များ\n"
        "/pray - ဆုတောင်းပေးရန် (/pray <text>)\n"
        "/praylist - ဆုတောင်းစာရင်း\n"
        "/quiz - Quiz စတင်ရန် (auto)\n"
        "/report - အကြောင်းအရာ တင်ပြရန်\n\n"
        "Admin များအတွက် /edit ကို အသုံးပြုပါ။"
    )
    await update.message.reply_text(with_signature(text))

async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in data.get("admins", []):
        await update.message.reply_text("ဤ command ကို admin များသာ အသုံးပြုနိုင်ပါသည်။\nCreate by : PINLON-YOUTH")
        return
    text = (
        "Admin Commands -\n"
        "/edabout - သမိုင်းကြောင်းနှင့် ရည်ရွယ်ချက် ပြင်ရန်\n"
        "/edcontact - တာဝန်ခံများထည့်ရန်\n"
        "/edverse - verse ထည့်ရန်\n"
        "/edevents - events ထည့်ရန်\n"
        "/edbirthday - birthday ထည့်ရန်\n"
        "/edquiz - quiz ထည့်ရန်\n"
        "/broadcast - group များသို့ ပို့ရန်\n"
        "/stats - bot အခြေအနေ\n"
        "/backup - data backup\n"
        "/restore - data restore (send file)\n"
        "/allclear - အချက်အလက်အားလုံး ဖျက်ရန်\n    "
    )
    await update.message.reply_text(with_signature(text))

# About
@admin_only
async def edabout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("အသင်းအကြောင်းကို ရေးပါ။\nUsage: /edabout <text>")
        return
    data["about"] = text
    save_data(data)
    await update.message.reply_text(with_signature("About updated."))

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = data.get("about") or "အသင်းအကြောင်း မရှိသေးပါ။"
    await update.message.reply_text(with_signature(text))

# Contacts
@admin_only
async def edcontact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("Contact list ထည့်ပါ။\nUsage: /edcontact Name-Phone;Name2-Phone2")
        return
    # Expect semicolon separated Name-Phone
    entries = [e.strip() for e in text.split(";") if e.strip()]
    for e in entries:
        if "-" in e:
            name, phone = e.split("-", 1)
            data["contacts"].append({"name": name.strip(), "phone": phone.strip()})
    save_data(data)
    await update.message.reply_text(with_signature("Contacts updated."))

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not data["contacts"]:
        await update.message.reply_text(with_signature("Contact မရှိသေးပါ။"))
        return
    lines = [f"{c['name']} - {c['phone']}" for c in data["contacts"]]
    await update.message.reply_text(with_signature("\n".join(lines)))

# Verses
@admin_only
async def edverse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("Verse ထည့်ပါ။\nUsage: /edverse <verse text>")
        return
    data["verses"].append(text)
    save_data(data)
    await update.message.reply_text(with_signature("Verse added."))

async def verse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not data["verses"]:
        await update.message.reply_text(with_signature("Verse မရှိသေးပါ။"))
        return
    v = random.choice(data["verses"])
    await update.message.reply_text(with_signature(v))

# Events
@admin_only
async def edevents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("Event ထည့်ပါ။\nUsage: /edevents <date - description>")
        return
    data["events"].append(text)
    save_data(data)
    await update.message.reply_text(with_signature("Event added."))

async def events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not data["events"]:
        await update.message.reply_text(with_signature("Event မရှိသေးပါ။"))
        return
    await update.message.reply_text(with_signature("\n".join(data["events"])))

# Birthdays
@admin_only
async def edbirthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("Birthday list ထည့်ပါ။\nUsage: /edbirthday Name-DD-MM")
        return
    entries = [e.strip() for e in text.split(";") if e.strip()]
    for e in entries:
        if "-" in e:
            name, ddmm = e.split("-", 1)
            data["birthdays"].append({"name": name.strip(), "ddmm": ddmm.strip()})
    save_data(data)
    await update.message.reply_text(with_signature("Birthdays updated."))

async def birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # list birthdays in current month
    now = datetime.now()
    month = now.month
    results = []
    for b in data["birthdays"]:
        try:
            parts = b["ddmm"].split("-")
            d = int(parts[0])
            m = int(parts[1])
            if m == month:
                results.append(f"{b['name']} - {b['ddmm']}")
        except Exception:
            continue
    if not results:
        await update.message.reply_text(with_signature("ယခုလတွင် မွေးနေ့ မရှိသေးပါ။"))
        return
    await update.message.reply_text(with_signature("\n".join(results)))

# Prayers
async def pray(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("ဆုတောင်းပေးလိုသည့် အချက်ကို ရေးပါ။\nUsage: /pray <text>")
        return
    entry = {
        "user": update.effective_user.username or update.effective_user.full_name,
        "text": text,
        "time": datetime.now().isoformat()
    }
    data["prayers"].append(entry)
    save_data(data)
    await update.message.reply_text(with_signature("သင့်ဆုတောင်းကို မှတ်တမ်းတင်ပြီးပါပြီ။"))

async def praylist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not data["prayers"]:
        await update.message.reply_text(with_signature("ဆုတောင်းစာရင်း မရှိသေးပါ။"))
        return
    lines = [f"{p['user']}: {p['text']}" for p in data["prayers"]]
    await update.message.reply_text(with_signature("\n".join(lines)))

# Quiz system
@admin_only
async def edquiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Expect format: Question | A | B | C | D | answer_letter
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("Quiz ထည့်ပါ။\nUsage: /edquiz Question | A | B | C | D | A")
        return
    parts = [p.strip() for p in text.split("|")]
    if len(parts) != 6:
        await update.message.reply_text("Format မှားနေပါသည်။\nUsage: /edquiz Question | A | B | C | D | A")
        return
    q = {
        "question": parts[0],
        "choices": [parts[1], parts[2], parts[3], parts[4]],
        "answer": parts[5].upper()
    }
    data["quizzes"].append(q)
    save_data(data)
    await update.message.reply_text(with_signature("Quiz added."))

async def send_quiz_to_chat(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    if not data["quizzes"]:
        return
    q = random.choice(data["quizzes"])
    text = f"Quiz Time!\n\n{q['question']}\nA. {q['choices'][0]}\nB. {q['choices'][1]}\nC. {q['choices'][2]}\nD. {q['choices'][3]}\n\nReply with A/B/C/D to answer."
    await context.bot.send_message(chat_id=chat_id, text=with_signature(text))

# Message counter and quiz trigger
async def message_counter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    # register group
    await register_group(chat_id)
    # increment counter
    counters = data.get("message_counters", {})
    settings = data.get("settings", {})
    threshold = settings.get(str(chat_id), {}).get("threshold", 0)
    counters[str(chat_id)] = counters.get(str(chat_id), 0) + 1
    data["message_counters"] = counters
    save_data(data)
    # check threshold
    if threshold and counters[str(chat_id)] >= threshold:
        # send quiz
        await send_quiz_to_chat(chat_id, context)
        counters[str(chat_id)] = 0
        data["message_counters"] = counters
        save_data(data)

# Handle quiz answers (simple)
async def handle_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip().upper()
    if text not in ("A", "B", "C", "D"):
        return
    # We cannot track which quiz was last sent per chat in this simple version.
    # We'll check last quiz in list as the one asked.
    if not data["quizzes"]:
        return
    q = data["quizzes"][-1]
    correct = q["answer"].upper()
    user_id = str(update.effective_user.id)
    if text == correct:
        # increment score
        scores = data.get("quiz_scores", {})
        scores[user_id] = scores.get(user_id, 0) + 1
        data["quiz_scores"] = scores
        save_data(data)
        await update.message.reply_text(with_signature("မှန်ပါသည်! +1 point"))
    else:
        await update.message.reply_text(with_signature(f"မမှန်ပါ။ မှန်ကန်သောဖြေ: {correct}"))

async def tops(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scores = data.get("quiz_scores", {})
    if not scores:
        await update.message.reply_text(with_signature("မည်သူ့မှ Quiz score မရှိသေးပါ။"))
        return
    # convert to list of (name, score)
    items = []
    for uid, sc in scores.items():
        try:
            user = await context.bot.get_chat(int(uid))
            name = user.full_name
        except Exception:
            name = uid
        items.append((name, sc))
    items.sort(key=lambda x: x[1], reverse=True)
    lines = [f"{i+1}. {n} - {s}" for i, (n, s) in enumerate(items[:10])]
    await update.message.reply_text(with_signature("\n".join(lines)))

# Set threshold
@admin_only
async def set_threshold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if not context.args:
        await update.message.reply_text("Usage: /set <number>")
        return
    try:
        n = int(context.args[0])
        if n < 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("ကျေးဇူးပြု၍ အမှန်တကယ်သော နံပါတ်တစ်ခု ရိုက်ထည့်ပါ။")
        return
    settings = data.get("settings", {})
    settings[chat_id] = settings.get(chat_id, {})
    settings[chat_id]["threshold"] = n
    data["settings"] = settings
    save_data(data)
    await update.message.reply_text(with_signature(f"Message threshold set to {n}"))

# Broadcast to groups (admin)
@admin_only
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Usage: /broadcast <text>  and optionally attach photo
    text = " ".join(context.args) if context.args else ""
    if not text and not update.message.photo:
        await update.message.reply_text("Usage: /broadcast <text> (or attach photo with caption)")
        return
    sent = 0
    failed = 0
    for gid in data.get("groups", []):
        try:
            if update.message.photo:
                # send photo with caption
                photo = update.message.photo[-1]
                await context.bot.send_photo(chat_id=gid, photo=photo.file_id, caption=with_signature(text))
            else:
                await context.bot.send_message(chat_id=gid, text=with_signature(text))
            sent += 1
        except Exception as e:
            logger.exception("Broadcast failed to %s", gid)
            failed += 1
    await update.message.reply_text(with_signature(f"Broadcast finished. Sent: {sent}, Failed: {failed}"))

# Stats
@admin_only
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    groups = len(data.get("groups", []))
    users = "N/A"  # bot cannot easily count unique users without tracking
    quizzes = len(data.get("quizzes", []))
    verses = len(data.get("verses", []))
    await update.message.reply_text(with_signature(f"Groups: {groups}\nQuizzes: {quizzes}\nVerses: {verses}"))

# Reports
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("Report အကြောင်းအရာ ရေးပါ။\nUsage: /report <text>")
        return
    entry = {
        "user": update.effective_user.username or update.effective_user.full_name,
        "text": text,
        "time": datetime.now().isoformat()
    }
    data["reports"].append(entry)
    save_data(data)
    await update.message.reply_text(with_signature("Report ကို လက်ခံရရှိပါသည်။"))

# Backup and restore
@admin_only
async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # send data file to admin
    try:
        await update.message.reply_document(document=InputFile(DATA_FILE), filename="backup_data.json")
    except Exception as e:
        logger.exception("Backup failed")
        await update.message.reply_text(with_signature("Backup မအောင်မြင်ပါ။"))

@admin_only
async def restore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Admin should send a file with /restore command and attach the file
    if not update.message.document:
        await update.message.reply_text("Restore ဖိုင်ကို attach လုပ်ပြီး /restore command ထပ်မံပို့ပါ။")
        return
    doc = update.message.document
    file = await doc.get_file()
    path = "data/restore_temp.json"
    await file.download_to_drive(path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            newdata = json.load(f)
        # Overwrite data
        global data
        data = newdata
        save_data(data)
        await update.message.reply_text(with_signature("Restore အောင်မြင်ပါသည်။"))
    except Exception as e:
        logger.exception("Restore failed")
        await update.message.reply_text(with_signature("Restore မအောင်မြင်ပါ။ ဖိုင်ကို စစ်ဆေးပါ။"))

# All clear
@admin_only
async def allclear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Clear all data except admins
    admins = data.get("admins", [])
    new = {
        "admins": admins,
        "groups": [],
        "contacts": [],
        "about": "",
        "verses": [],
        "events": [],
        "birthdays": [],
        "prayers": [],
        "quizzes": [],
        "quiz_scores": {},
        "settings": {},
        "message_counters": {},
        "reports": []
    }
    global data
    data = new
    save_data(data)
    await update.message.reply_text(with_signature("All data cleared."))

# Add admin command (for convenience)
@admin_only
async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /addadmin <user_id>")
        return
    try:
        uid = int(context.args[0])
        if uid not in data["admins"]:
            data["admins"].append(uid)
            save_data(data)
        await update.message.reply_text(with_signature("Admin added."))
    except Exception:
        await update.message.reply_text("Invalid user id.")

# Scheduler for daily verses (morning and night)
scheduler = AsyncIOScheduler()

async def scheduled_send_verse(context: ContextTypes.DEFAULT_TYPE, when: str):
    # when: "morning" or "night"
    if not data["verses"]:
        return
    verse_text = random.choice(data["verses"])
    text = f"{when.title()} Verse\n\n{verse_text}"
    for gid in data.get("groups", []):
        try:
            await context.bot.send_message(chat_id=gid, text=with_signature(text))
        except Exception:
            continue

def schedule_jobs(app):
    # Morning at 06:00 and Night at 20:00 (local time)
    scheduler.add_job(lambda: asyncio.create_task(scheduled_send_verse(app, "morning")),
                      CronTrigger(hour=6, minute=0))
    scheduler.add_job(lambda: asyncio.create_task(scheduled_send_verse(app, "night")),
                      CronTrigger(hour=20, minute=0))
    scheduler.start()

# Backup on shutdown
async def on_shutdown(app):
    save_data(data)
    logger.info("Bot shutting down, data saved.")

# Entry point
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("edit", edit))
    app.add_handler(CommandHandler("edabout", edabout))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("edcontact", edcontact))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CommandHandler("edverse", edverse))
    app.add_handler(CommandHandler("verse", verse))
    app.add_handler(CommandHandler("edevents", edevents))
    app.add_handler(CommandHandler("events", events))
    app.add_handler(CommandHandler("edbirthday", edbirthday))
    app.add_handler(CommandHandler("birthday", birthday))
    app.add_handler(CommandHandler("pray", pray))
    app.add_handler(CommandHandler("praylist", praylist))
    app.add_handler(CommandHandler("edquiz", edquiz))
    app.add_handler(CommandHandler("quiz", lambda u, c: send_quiz_to_chat(u.effective_chat.id, c)))
    app.add_handler(CommandHandler("Tops", tops))
    app.add_handler(CommandHandler("set", set_threshold))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("backup", backup))
    app.add_handler(CommandHandler("restore", restore))
    app.add_handler(CommandHandler("allclear", allclear))
    app.add_handler(CommandHandler("addadmin", addadmin))

    # Message handlers
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_counter))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_quiz_answer))

    # Start scheduler after app is ready
    async def start_scheduler(_):
        schedule_jobs(app)
    app.post_init = start_scheduler
    app.post_shutdown = on_shutdown

    logger.info("Starting bot")
    app.run_polling()

if __name__ == "__main__":
    main()
