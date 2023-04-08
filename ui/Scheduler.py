

from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
import datetime
from ReadLatest import readLatest

import logging
logging.basicConfig(filename='logging.log', 
#                    encoding='utf-8', 
                    level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    )


if __name__ == '__main__':
    
    logging.debug(str(datetime.datetime.now()) + ' main program started')
    print("main program started")

    scheduler = BlockingScheduler(daemon=True, job_defaults={'coalesce': False})
#    scheduler.configure(timezone="utc")

    scheduler.add_job(readLatest, 'cron', day_of_week='mon-sun', hour='0-23', minute='*/30',)
    # job = scheduler.add_job(startRunProgram, 'interval', seconds=20, next_run_time=datetime.datetime.now())
        
    scheduler.start()
    
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))