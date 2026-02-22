# -*- coding: utf-8 -*-
import random
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
import db, utils, config
from datetime import datetime
import io

# /start
def start(update: Update, context: CallbackContext):
    utils.register_user(update)
    chat = update.effective_chat
    if chat:
        utils.register_group(chat)
    text = (
        "ကျေးဇူးတင်ပါတယ်။ Church Community Bot သို့ ကြိုဆိုပါသည်။\n\n"
        "အသုံးပြုနိုင်သော command များ -\n"
        "/about - အသင်းအကြောင်း\n"
        "/verse - ယနေ့ဖတ်ရန် ကျမ်းချက်\n"
        "/events - လာမည့်အစီအစဉ်များ\n"
        "/birthday - ယခုလ မွေးနေ့များ\n"
        "/pray - ဆုတောင်းပေးရန် (ဥပမာ: /pray ကျန်းမာရေးအတွက်)\n"
        "/praylist - ဆုတောင်းစာရင်း\n"
        "/quiz - နေ့စဉ် Quiz\n"
        "/report - အကြောင်းအရာ တင်ပြရန်\n\n"
        f"{config.FOOTER}"
    )
    update.message.reply_text(text)

# /edit - admin only (lists admin commands)
from utils import admin_only
@admin_only
def edit(update: Update, context: CallbackContext):
    text = (
        "Admin commands -\n"
        "/edabout - သမိုင်းနှင့် ရည်ရွယ်ချက်ရေးရန်\n"
        "/edcontact - တာဝန်ခံများ ဖုန်းနံပါတ် ထည့်ရန်\n"
        "/edverse - verse ထည့်ရန်\n"
        "/edevents - events ထည့်ရန်\n"
        "/edbirthday - birthday ထည့်ရန်\n"
        "/edquiz - quiz ထည့်ရန်\n"
        "/broadcast - သတင်းပို့ရန်\n"
        "/stats - စာရင်းအခြေအနေ\n"
        "/backup - data backup\n"
        "/restore - data restore (send DB file)\n"
        "/allclear - အချက်အလက်အားလုံး ဖျက်ရန်\n"
    )
    update.message.reply_text(text)

# /edabout (admin)
@admin_only
def edabout(update: Update, context: CallbackContext):
    text = " ".join(context.args) if context.args else ""
    if not text:
        update.message.reply_text("သမိုင်းနှင့် ရည်ရွယ်ချက်ကို အတိအကျ ရိုက်ထည့်ပါ။")
        return
    db.execute("DELETE FROM reports WHERE id<0")  # noop to ensure DB exists
    # store as a special 'report' with tag 'about' (simple approach)
    db.execute("INSERT INTO reports (user_id, username, text) VALUES (?, ?, ?)",
               (update.effective_user.id, update.effective_user.username or "", f"ABOUT:{text}"))
    update.message.reply_text("သမိုင်းနှင့် ရည်ရွယ်ချက်ကို သိမ်းဆည်းပြီးပါပြီ။")

# /about (users)
def about(update: Update, context: CallbackContext):
    rows = db.execute("SELECT text FROM reports WHERE text LIKE 'ABOUT:%' ORDER BY id DESC LIMIT 1", fetch=True)
    if rows:
        text = rows[0][0].replace("ABOUT:", "")
    else:
        text = "သမိုင်းနှင့် ရည်ရွယ်ချက် မရှိသေးပါ။"
    update.message.reply_text(text + config.FOOTER)

# /contact and /edcontact
@admin_only
def edcontact(update: Update, context: CallbackContext):
    text = " ".join(context.args) if context.args else ""
    if not text:
        update.message.reply_text("အမည်-ဖုန်းနံပါတ်များကို ရိုက်ထည့်ပါ။ (ဥပမာ: John-09xxxx)")
        return
    db.execute("INSERT INTO reports (user_id, username, text) VALUES (?, ?, ?)",
               (update.effective_user.id, update.effective_user.username or "", f"CONTACT:{text}"))
    update.message.reply_text("တာဝန်ခံ ဖုန်းနံပါတ်များ သိမ်းဆည်းပြီးပါပြီ။")

def contact(update: Update, context: CallbackContext):
    rows = db.execute("SELECT text FROM reports WHERE text LIKE 'CONTACT:%' ORDER BY id DESC", fetch=True)
    items = [r[0].replace("CONTACT:", "") for r in rows]
    update.message.reply_text(utils.format_list_with_footer(items))

# /verse and /edverse
@admin_only
def edverse(update: Update, context: CallbackContext):
    text = " ".join(context.args) if context.args else ""
    if not text:
        update.message.reply_text("Verse ကို ရိုက်ထည့်ပါ။")
        return
    db.execute("INSERT INTO verses (text) VALUES (?)", (text,))
    update.message.reply_text("Verse ထည့်ပြီးပါပြီ။")

def verse(update: Update, context: CallbackContext):
    rows = db.execute("SELECT text FROM verses", fetch=True)
    if not rows:
        update.message.reply_text("Verse မရှိသေးပါ။")
        return
    # pick random verse
    text = random.choice(rows)[0]
    update.message.reply_text(text + config.FOOTER)

# /events and /edevents
@admin_only
def edevents(update: Update, context: CallbackContext):
    args = context.args
    if len(args) < 2:
        update.message.reply_text("အသုံး: /edevents <date> <title> (date format: YYYY-MM-DD)")
        return
    date = args[0]
    title = " ".join(args[1:])
    db.execute("INSERT INTO events (title, date) VALUES (?, ?)", (title, date))
    update.message.reply_text("Event ထည့်ပြီးပါပြီ။")

def events(update: Update, context: CallbackContext):
    rows = db.execute("SELECT date, title FROM events ORDER BY date", fetch=True)
    items = [f"{r[0]} - {r[1]}" for r in rows]
    update.message.reply_text(utils.format_list_with_footer(items))

# /birthday and /edbirthday
@admin_only
def edbirthday(update: Update, context: CallbackContext):
    args = context.args
    if len(args) < 2:
        update.message.reply_text("အသုံး: /edbirthday <DD-MM> <name>")
        return
    dm = args[0]
    try:
        day, month = map(int, dm.split("-"))
    except:
        update.message.reply_text("DD-MM အဖြစ် ရိုက်ထည့်ပါ။")
        return
    name = " ".join(args[1:])
    db.execute("INSERT INTO birthdays (name, day, month) VALUES (?, ?, ?)", (name, day, month))
    update.message.reply_text("Birthday ထည့်ပြီးပါပြီ။")

def birthday(update: Update, context: CallbackContext):
    now = datetime.now()
    rows = db.execute("SELECT name, day, month FROM birthdays WHERE month = ?", (now.month,), fetch=True)
    items = [f"{r[0]} - {r[1]}/{r[2]}" for r in rows]
    update.message.reply_text(utils.format_list_with_footer(items))

# /pray and /praylist
def pray(update: Update, context: CallbackContext):
    text = " ".join(context.args) if context.args else ""
    if not text:
        update.message.reply_text("ဆုတောင်းလိုသည့် အချက်ကို ရိုက်ထည့်ပါ။ (ဥပမာ: /pray ကျန်းမာရေးအတွက်)")
        return
    user = update.effective_user
    db.execute("INSERT INTO prayers (user_id, username, text) VALUES (?, ?, ?)",
               (user.id, user.username or "", text))
    update.message.reply_text("သင့်ဆုတောင်းကို သိမ်းဆည်းပြီးပါပြီ။")

def praylist(update: Update, context: CallbackContext):
    rows = db.execute("SELECT username, text, created_at FROM prayers ORDER BY created_at DESC", fetch=True)
    items = [f"{r[0]}: {r[1]}" for r in rows]
    update.message.reply_text(utils.format_list_with_footer(items))

# /quiz and /edquiz and scoring
@admin_only
def edquiz(update: Update, context: CallbackContext):
    # expected format: /edquiz Question | A | B | C | D | ANSWER
    raw = " ".join(context.args)
    parts = [p.strip() for p in raw.split("|")]
    if len(parts) != 6:
        update.message.reply_text("Format: /edquiz Question | A | B | C | D | ANSWER(eg A)")
        return
    question, a, b, c, d, ans = parts
    db.execute("INSERT INTO quizzes (question, choice_a, choice_b, choice_c, choice_d, answer) VALUES (?, ?, ?, ?, ?, ?)",
               (question, a, b, c, d, ans.strip().upper()))
    update.message.reply_text("Quiz ထည့်ပြီးပါပြီ။")

def quiz(update: Update, context: CallbackContext):
    rows = db.execute("SELECT id, question, choice_a, choice_b, choice_c, choice_d FROM quizzes", fetch=True)
    if not rows:
        update.message.reply_text("Quiz မရှိသေးပါ။")
        return
    q = random.choice(rows)
    qid = q[0]
    text = f"Quiz #{qid}\n\n{q[1]}\nA. {q[2]}\nB. {q[3]}\nC. {q[4]}\nD. {q[5]}\n\nReply with /answer {qid} <A/B/C/D>"
    update.message.reply_text(text)

def answer(update: Update, context: CallbackContext):
    args = context.args
    if len(args) < 2:
        update.message.reply_text("အသုံး: /answer <quiz_id> <A/B/C/D>")
        return
    qid = args[0]
    ans = args[1].strip().upper()
    row = db.execute("SELECT answer FROM quizzes WHERE id = ?", (qid,), fetch=True)
    if not row:
        update.message.reply_text("Quiz မတွေ့ပါ။")
        return
    correct = row[0][0].strip().upper()
    user = update.effective_user
    if ans == correct:
        # increment score
        existing = db.execute("SELECT id, score FROM quiz_scores WHERE user_id = ?", (user.id,), fetch=True)
        if existing:
            db.execute("UPDATE quiz_scores SET score = score + 1, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?", (user.id,))
        else:
            db.execute("INSERT INTO quiz_scores (user_id, username, score) VALUES (?, ?, ?)", (user.id, user.username or "", 1))
        update.message.reply_text("မှန်ပါတယ်! သင့်အမှတ်တိုးပြီးပါပြီ။")
    else:
        update.message.reply_text(f"မမှန်ပါ။ မှန်သောဖြေ: {correct}")

# /Tops
def tops(update: Update, context: CallbackContext):
    rows = db.execute("SELECT username, score FROM quiz_scores ORDER BY score DESC LIMIT 10", fetch=True)
    items = [f"{i+1}. {r[0]} - {r[1]}" for i, r in enumerate(rows)]
    update.message.reply_text(utils.format_list_with_footer(items))

# /broadcast (admin)
@admin_only
def broadcast(update: Update, context: CallbackContext):
    # usage: /broadcast <text> (optionally reply with photo to include)
    text = " ".join(context.args) if context.args else ""
    if not text and not update.message.reply_to_message:
        update.message.reply_text("ပို့လိုသည့် စာကို ရိုက်ထည့်ပါ။")
        return
    # gather groups
    groups = db.execute("SELECT chat_id FROM groups", fetch=True)
    sent = 0
    failed = 0
    for g in groups:
        chat_id = g[0]
        try:
            if update.message.reply_to_message and update.message.reply_to_message.photo:
                # send photo with caption
                photo = update.message.reply_to_message.photo[-1].file_id
                context.bot.send_photo(chat_id=chat_id, photo=photo, caption=text + config.FOOTER)
            else:
                context.bot.send_message(chat_id=chat_id, text=text + config.FOOTER)
            sent += 1
        except Exception as e:
            failed += 1
    update.message.reply_text(f"Broadcast ပြီးစီးပါပြီ။ Sent: {sent}, Failed: {failed}")

# /stats (admin)
@admin_only
def stats(update: Update, context: CallbackContext):
    users = db.execute("SELECT COUNT(*) FROM users", fetch=True)[0][0]
    groups = db.execute("SELECT COUNT(*) FROM groups", fetch=True)[0][0]
    verses = db.execute("SELECT COUNT(*) FROM verses", fetch=True)[0][0]
    quizzes = db.execute("SELECT COUNT(*) FROM quizzes", fetch=True)[0][0]
    text = f"Users: {users}\nGroups: {groups}\nVerses: {verses}\nQuizzes: {quizzes}"
    update.message.reply_text(text)

# /report
def report(update: Update, context: CallbackContext):
    text = " ".join(context.args) if context.args else ""
    if not text:
        update.message.reply_text("တင်ပြလိုသည့် အကြောင်းအရာကို ရိုက်ထည့်ပါ။")
        return
    user = update.effective_user
    db.execute("INSERT INTO reports (user_id, username, text) VALUES (?, ?, ?)",
               (user.id, user.username or "", text))
    update.message.reply_text("သင့် report ကို သိမ်းဆည်းပြီးပါပြီ။")

# /backup (admin)
@admin_only
def backup(update: Update, context: CallbackContext):
    try:
        with open(db.DB_PATH, "rb") as f:
            update.message.reply_document(document=f, filename="church_community_backup.db")
    except Exception as e:
        update.message.reply_text("Backup မအောင်မြင်ပါ။")

# /restore (admin) - expects admin to send DB file as document with caption /restore
@admin_only
def restore(update: Update, context: CallbackContext):
    # This handler should be used when admin uploads a file and captions /restore
    if not update.message.document:
        update.message.reply_text("DB ဖိုင်ကို upload ပြီး /restore caption ဖြင့် ပို့ပါ။")
        return
    file = update.message.document.get_file()
    file.download(custom_path=db.DB_PATH)
    update.message.reply_text("Restore ပြီးပါပြီ။ Bot ကို restart လုပ်ပါ။")

# /allclear (admin)
@admin_only
def allclear(update: Update, context: CallbackContext):
    # Danger: delete all data
    db.execute("DELETE FROM users")
    db.execute("DELETE FROM groups")
    db.execute("DELETE FROM verses")
    db.execute("DELETE FROM quizzes")
    db.execute("DELETE FROM events")
    db.execute("DELETE FROM birthdays")
    db.execute("DELETE FROM prayers")
    db.execute("DELETE FROM reports")
    db.execute("DELETE FROM quiz_scores")
    update.message.reply_text("Data အားလုံး ဖျက်ပြီးပါပြီ။")
