import os
from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
import datetime

def price_to_github():

    print(datetime.datetime.now())
    os.system('git commit -a -m "commit from windows"')
    
    print("after commmittttinnnnnnnnnnnnng")

    os.system('git push -u origin master')

    print("Success")

price_to_github()


if __name__ == '__main__':
    
    print("Price to Github started")

    scheduler = BlockingScheduler(daemon=True, job_defaults={'coalesce': False})
#    scheduler.configure(timezone="utc")

    scheduler.add_job(price_to_github, 'interval', seconds=7200, next_run_time=datetime.datetime.now())

    # scheduler.add_job(price_to_github, 'cron', day_of_week='mon-sun', hour='0-23', minute='*/00',)
    # job = scheduler.add_job(startRunProgram, 'interval', seconds=20, next_run_time=datetime.datetime.now())
        
    scheduler.start()
    
    # print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))