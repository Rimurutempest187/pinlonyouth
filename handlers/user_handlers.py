from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes
from utils.storage import load_data, save_data
from config import DATA_FILE

WELCOME_TEXT = (
    "မင်္ဂလာပါ 👋\n\n"
    "Church Community Bot သို့ ကြိုဆိုပါသည်။\n\n"
    "Available commands:\n"
    "/about - အသင်းတော် သမိုင်းနှင့် ရည်ရွယ်ချက်\n"
    "/contact - တာဝန်ခံ လူငယ်ခေါင်းဆောင်များ ဖုန်းနံပါတ်များ\n"
    "/verse - ယနေ့ဖတ်ရန် ကျမ်းချက်များ\n"
    "/events - လာမည့် အစီအစဉ်များ\n"
    "/birthday - ယခုလ မွေးနေ့များ\n"
    "/pray <text> - ဆုတောင်းပေးစေလိုသည့် အချက်\n"
    "/praylist - ဆုတောင်းစာရင်း\n"
    "/quiz - နေ့စဉ် Quiz\n"
    "/report <text> - အကြောင်းအရာ တင်ပြရန်\n\n"
    "Create by : PINLON-YOUTH"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data(DATA_FILE)
    uid = str(user.id)
    if "users" not in data:
        data["users"] = {}
    data["users"].setdefault(uid, {"id": user.id, "username": user.username or "", "first_name": user.first_name or ""})
    save_data(DATA_FILE, data)
    await update.message.reply_text(WELCOME_TEXT)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data(DATA_FILE)
    about_text = data.get("about", "အသင်းတော် သမိုင်းနှင့် ရည်ရွယ်ချက် မရှိသေးပါ။")
    await update.message.reply_text(about_text)

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data(DATA_FILE)
    contacts = data.get("contacts", [])
    if not contacts:
        await update.message.reply_text("တာဝန်ခံ ဖုန်းနံပါတ် မရှိသေးပါ။")
        return
    text = "တာဝန်ခံ လူငယ်ခေါင်းဆောင်များ\n"
    for c in contacts:
        text += f"- {c.get('name')} : {c.get('phone')}\n"
    await update.message.reply_text(text)

async def verse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data(DATA_FILE)
    verses = data.get("verses", [])
    if not verses:
        await update.message.reply_text("Verse မရှိသေးပါ။")
        return
    import random
    v = random.choice(verses)
    await update.message.reply_text(v)

async def events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data(DATA_FILE)
    events = data.get("events", [])
    if not events:
        await update.message.reply_text("လာမည့် အစီအစဉ် မရှိသေးပါ။")
        return
    text = "လာမည့် အစီအစဉ်များ\n"
    for e in events:
        text += f"- {e}\n"
    await update.message.reply_text(text)

async def birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data(DATA_FILE)
    bdays = data.get("birthdays", [])
    if not bdays:
        await update.message.reply_text("ယခုလ မွေးနေ့ မရှိသေးပါ။")
        return
    text = "ယခုလ မွေးနေ့များ\n"
    for b in bdays:
        text += f"- {b}\n"
    await update.message.reply_text(text)

async def pray(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("ဆုတောင်းပေးစေလိုသည့် အချက်ကို ရိုက်ထည့်ပါ။\nဥပမာ: /pray ကျန်းမာရေးအတွက် ဆုတောင်းပါ")
        return
    data = load_data(DATA_FILE)
    data.setdefault("prayers", []).append({"user": user.username or user.first_name, "text": text})
    data.setdefault("praylist", []).append({"user": user.username or user.first_name, "text": text})
    save_data(DATA_FILE, data)
    await update.message.reply_text("သင်၏ ဆုတောင်းကို မှတ်တမ်းတင်ပြီးပါပြီ။")

async def praylist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data(DATA_FILE)
    plist = data.get("praylist", [])
    if not plist:
        await update.message.reply_text("ဆုတောင်းစာရင်း မရှိသေးပါ။")
        return
    text = "ဆုတောင်းစာရင်း\n"
    for p in plist:
        text += f"- {p.get('user')}: {p.get('text')}\n"
    await update.message.reply_text(text)

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data(DATA_FILE)
    quizzes = data.get("quizzes", [])
    if not quizzes:
        await update.message.reply_text("Quiz မရှိသေးပါ။")
        return
    import random
    q = random.choice(quizzes)
    # q expected format: {"question":"...","choices":["A...","B...","C...","D..."],"answer":"A"}
    text = f"Quiz:\n{q.get('question')}\n"
    choices = q.get("choices", [])
    labels = ["A","B","C","D"]
    for i, c in enumerate(choices):
        text += f"{labels[i]}. {c}\n"
    text += "\nReply with the letter (A/B/C/D)."
    # store last quiz for user to check answer later (simple approach)
    uid = str(update.effective_user.id)
    data.setdefault("users", {}).setdefault(uid, {})["last_quiz"] = q
    save_data(DATA_FILE, data)
    await update.message.reply_text(text)

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("တင်ပြလိုသည့် အကြောင်းအရာကို ရိုက်ထည့်ပါ။")
        return
    data = load_data(DATA_FILE)
    data.setdefault("reports", []).append({"user": user.username or user.first_name, "text": text})
    save_data(DATA_FILE, data)
    await update.message.reply_text("သင်၏ အကြောင်းအရာကို လက်ခံရရှိပါသည်။")
