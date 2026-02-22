from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils.storage import load_data
from config import DATA_FILE, VERSES_SCHEDULE, QUIZ_SCHEDULE

scheduler = AsyncIOScheduler()

async def send_daily_verses(application):
    data = load_data(DATA_FILE)
    verses = data.get("verses", [])
    if not verses:
        return
    import random
    v = random.choice(verses)
    # send to all users (or groups) — choose groups for community
    groups = data.get("groups", [])
    for gid in groups:
        try:
            await application.bot.send_message(chat_id=gid, text=f"Daily Verse:\n{v}")
        except Exception:
            continue

async def send_daily_quiz(application):
    data = load_data(DATA_FILE)
    quizzes = data.get("quizzes", [])
    if not quizzes:
        return
    import random
    q = random.choice(quizzes)
    groups = data.get("groups", [])
    text = f"Daily Quiz:\n{q.get('question')}\n"
    labels = ["A","B","C","D"]
    for i, c in enumerate(q.get("choices", [])):
        text += f"{labels[i]}. {c}\n"
    for gid in groups:
        try:
            await application.bot.send_message(chat_id=gid, text=text)
        except Exception:
            continue

def start_scheduler(application):
    # schedule morning and night verses
    scheduler.add_job(lambda: application.create_task(send_daily_verses(application)),
                      trigger='cron',
                      hour=VERSES_SCHEDULE["morning"]["hour"],
                      minute=VERSES_SCHEDULE["morning"]["minute"],
                      id="verse_morning")
    scheduler.add_job(lambda: application.create_task(send_daily_verses(application)),
                      trigger='cron',
                      hour=VERSES_SCHEDULE["night"]["hour"],
                      minute=VERSES_SCHEDULE["night"]["minute"],
                      id="verse_night")
    # schedule daily quiz
    scheduler.add_job(lambda: application.create_task(send_daily_quiz(application)),
                      trigger='cron',
                      hour=QUIZ_SCHEDULE["hour"],
                      minute=QUIZ_SCHEDULE["minute"],
                      id="daily_quiz")
    scheduler.start()
