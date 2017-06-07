from apscheduler.schedulers.blocking import BlockingScheduler
from main import main

sched = BlockingScheduler()
sched.add_job(main, 'cron', day_of_week='mon-fri', hour=9, minute=30, timezone='Asia/Kolkata')
sched.start()