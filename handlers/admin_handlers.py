from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes
from config import ADMIN_IDS, DATA_FILE
from utils.storage import load_data, save_data, backup_data, restore_data
from pathlib import Path
import datetime

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

async def edit_cmds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("ဤ command ကို အသုံးမပြုနိုင်ပါ။ (Admins only)")
        return
    text = (
        "Admin commands:\n"
        "/edabout - အသင်းတော် သမိုင်းနှင့် ရည်ရွယ်ချက် ပြင်ရန်\n"
        "/edcontact - တာဝန်ခံ ဖုန်းနံပါတ်များ ထည့်ရန်\n"
        "/edverse - Verse ထည့်ရန်\n"
        "/edevents - Events ထည့်ရန်\n"
        "/edbirthday - Birthday list ထည့်ရန်\n"
        "/edquiz - Quiz ထည့်ရန်\n"
        "/broadcast - Group များသို့ ပို့ရန်\n"
        "/stats - Bot အချက်အလက် စစ်ဆေးရန်\n"
        "/backup - Data backup\n"
        "/restore - Data restore\n"
        "/allclear - Data အားလုံး ဖျက်ရန်\n"
    )
    await update.message.reply_text(text)

async def edabout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("Admins only")
        return
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("အသင်းတော် သမိုင်းနှင့် ရည်ရွယ်ချက်ကို ရိုက်ထည့်ပါ။")
        return
    data = load_data(DATA_FILE)
    data["about"] = text
    save_data(DATA_FILE, data)
    await update.message.reply_text("About ကို သိမ်းဆည်းပြီးပါပြီ။")

async def edcontact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("Admins only")
        return
    # Expect format: Name - Phone ; Name2 - Phone2 ; ...
    raw = " ".join(context.args)
    if not raw:
        await update.message.reply_text("အမည်-ဖုန်းနံပါတ်များကို ရိုက်ထည့်ပါ။ (ဥပမာ: John-0912345678; Mary-0998765432)")
        return
    contacts = []
    parts = raw.split(";")
    for p in parts:
        if "-" in p:
            name, phone = p.split("-", 1)
            contacts.append({"name": name.strip(), "phone": phone.strip()})
    data = load_data(DATA_FILE)
    data["contacts"] = contacts
    save_data(DATA_FILE, data)
    await update.message.reply_text("Contacts သိမ်းဆည်းပြီးပါပြီ။")

async def edverse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("Admins only")
        return
    raw = " ".join(context.args)
    if not raw:
        await update.message.reply_text("Verse ကို ရိုက်ထည့်ပါ။")
        return
    data = load_data(DATA_FILE)
    data.setdefault("verses", []).append(raw)
    save_data(DATA_FILE, data)
    await update.message.reply_text("Verse ထည့်ပြီးပါပြီ။")

async def edevents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("Admins only")
        return
    raw = " ".join(context.args)
    if not raw:
        await update.message.reply_text("Event ကို ရိုက်ထည့်ပါ။")
        return
    data = load_data(DATA_FILE)
    data.setdefault("events", []).append(raw)
    save_data(DATA_FILE, data)
    await update.message.reply_text("Event ထည့်ပြီးပါပြီ။")

async def edbirthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("Admins only")
        return
    raw = " ".join(context.args)
    if not raw:
        await update.message.reply_text("Birthday list ကို ရိုက်ထည့်ပါ။ (ဥပမာ: Name - DD-MM)")
        return
    parts = [p.strip() for p in raw.split(";") if p.strip()]
    data = load_data(DATA_FILE)
    data["birthdays"] = parts
    save_data(DATA_FILE, data)
    await update.message.reply_text("Birthdays သိမ်းဆည်းပြီးပါပြီ။")

async def edquiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("Admins only")
        return
    # Expect format: question | A | B | C | D | answer_letter
    raw = " ".join(context.args)
    if not raw or "|" not in raw:
        await update.message.reply_text("Format: question | A | B | C | D | answer_letter")
        return
    parts = [p.strip() for p in raw.split("|")]
    if len(parts) < 6:
        await update.message.reply_text("Format မမှန်ပါ။")
        return
    q = {"question": parts[0], "choices": parts[1:5], "answer": parts[5].upper()}
    data = load_data(DATA_FILE)
    data.setdefault("quizzes", []).append(q)
    save_data(DATA_FILE, data)
    await update.message.reply_text("Quiz ထည့်ပြီးပါပြီ။")

async def tops(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("Admins only")
        return
    data = load_data(DATA_FILE)
    # For simplicity, assume we store scores in data["scores"] as list of {"name":..., "score":...}
    scores = data.get("scores", [])
    if not scores:
        await update.message.reply_text("Scores မရှိသေးပါ။")
        return
    scores_sorted = sorted(scores, key=lambda x: x.get("score", 0), reverse=True)[:10]
    text = "Top Quiz Scores\n"
    for s in scores_sorted:
        text += f"- {s.get('name')}: {s.get('score')}\n"
    await update.message.reply_text(text)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("Admins only")
        return
    # Usage: /broadcast text here
    text = " ".join(context.args)
    if not text and not update.message.photo:
        await update.message.reply_text("ပို့လိုသည့် စာသား သို့မဟုတ် ပုံ တစ်ခုခု ထည့်ပါ။")
        return
    data = load_data(DATA_FILE)
    groups = data.get("groups", [])
    if not groups:
        await update.message.reply_text("Group များ မရှိသေးပါ။")
        return
    sent = 0
    for gid in groups:
        try:
            if update.message.photo:
                # forward photo with caption
                photo = update.message.photo[-1]
                await context.bot.send_photo(chat_id=gid, photo=photo.file_id, caption=text or "")
            else:
                await context.bot.send_message(chat_id=gid, text=text)
            sent += 1
        except Exception:
            continue
    await update.message.reply_text(f"Broadcast ပို့ပြီးပါပြီ။ ({sent}/{len(groups)})")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("Admins only")
        return
    data = load_data(DATA_FILE)
    users = len(data.get("users", {}))
    groups = len(data.get("groups", []))
    verses = len(data.get("verses", []))
    quizzes = len(data.get("quizzes", []))
    await update.message.reply_text(f"Users: {users}\nGroups: {groups}\nVerses: {verses}\nQuizzes: {quizzes}")

async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("Admins only")
        return
    src = DATA_FILE
    backup_path = f"{DATA_FILE}.backup.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    try:
        backup_data(src, backup_path)
        await update.message.reply_text(f"Backup created: {backup_path}")
    except Exception as e:
        await update.message.reply_text(f"Backup failed: {e}")

async def restore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("Admins only")
        return
    # Usage: /restore backup_filename
    if not context.args:
        await update.message.reply_text("Restore ဖိုင်နာမည် ရိုက်ထည့်ပါ။")
        return
    backup_path = context.args[0]
    try:
        restore_data(backup_path, DATA_FILE)
        await update.message.reply_text("Restore ပြီးစီးပါပြီ။")
    except Exception as e:
        await update.message.reply_text(f"Restore မအောင်မြင်ပါ: {e}")

async def allclear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("Admins only")
        return
    # Danger: clear all data
    data = {
        "users": {},
        "groups": [],
        "verses": [],
        "quizzes": [],
        "events": [],
        "contacts": [],
        "birthdays": [],
        "prayers": [],
        "praylist": [],
        "reports": []
    }
    save_data(DATA_FILE, data)
    await update.message.reply_text("Data အားလုံး ဖျက်ပြီးပါပြီ။")
