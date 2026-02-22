# -*- coding: utf-8 -*-
from telegram.ext import JobQueue
import db, random, config
from datetime import time
import pytz

def send_daily_verse(context):
    # pick random verse and send to all groups
    rows = db.execute("SELECT text FROM verses", fetch=True)
    if not rows:
        return
    text = random.choice(rows)[0] + config.FOOTER
    groups = db.execute("SELECT chat_id FROM groups", fetch=True)
    for g in groups:
        try:
            context.bot.send_message(chat_id=g[0], text=text)
        except:
            continue

def send_daily_quiz(context):
    rows = db.execute("SELECT id, question, choice_a, choice_b, choice_c, choice_d FROM quizzes", fetch=True)
    if not rows:
        return
    q = random.choice(rows)
    qid = q[0]
    text = f"Daily Quiz #{qid}\n\n{q[1]}\nA. {q[2]}\nB. {q[3]}\nC. {q[4]}\nD. {q[5]}\n\nReply with /answer {qid} <A/B/C/D>"
    groups = db.execute("SELECT chat_id FROM groups", fetch=True)
    for g in groups:
        try:
            context.bot.send_message(chat_id=g[0], text=text)
        except:
            continue

def schedule_jobs(job_queue: JobQueue):
    tz = pytz.timezone(config.TIMEZONE)
    # Morning verse at 6:00
    job_queue.run_daily(send_daily_verse, time=time(hour=6, minute=0, tzinfo=tz))
    # Night verse at 20:00
    job_queue.run_daily(send_daily_verse, time=time(hour=20, minute=0, tzinfo=tz))
    # Daily quiz at 18:00
    job_queue.run_daily(send_daily_quiz, time=time(hour=18, minute=0, tzinfo=tz))
