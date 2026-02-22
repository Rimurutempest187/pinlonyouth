# -*- coding: utf-8 -*-
from functools import wraps
from telegram import Update
from telegram.ext import CallbackContext
import config
import db

def is_admin(user_id):
    return user_id in config.ADMINS

def admin_only(func):
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        user = update.effective_user
        if not user:
            return
        if not is_admin(user.id):
            update.message.reply_text("ဤ command ကို အသုံးပြုခွင့်မရှိပါ။")
            return
        return func(update, context, *args, **kwargs)
    return wrapped

def register_user(update: Update):
    user = update.effective_user
    if not user:
        return
    db.execute(
        "INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, is_admin) VALUES (?, ?, ?, ?, ?)",
        (user.id, user.username or "", user.first_name or "", user.last_name or "", 1 if is_admin(user.id) else 0)
    )

def register_group(chat):
    if chat.type in ("group", "supergroup"):
        db.execute(
            "INSERT OR REPLACE INTO groups (chat_id, title) VALUES (?, ?)",
            (chat.id, chat.title or "")
        )

def format_list_with_footer(items):
    text = "\n".join(items) if items else "မရှိပါ။"
    return f"{text}{config.FOOTER}"
