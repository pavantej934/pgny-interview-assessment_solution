from datetime import datetime
import pytz
import logging

class Logger:

    def __init__(self):
        log_path = './storage/logs/app.log'
        logging.getLogger('apscheduler.scheduler').propagate = False
        logging.basicConfig(filename=log_path,
                            filemode='a',
                            format='%(asctime)s, %(levelname)s %(message)s',
                            datefmt='%m/%d/%Y %H:%M:%S',
                            level=logging.INFO)

    def log_to_file(self, msg):
        logging.info(msg)

    def log_to_console(self, msg):
        print (datetime.now(pytz.timezone('US/Eastern')),':', msg)

    def log(self, msg, console=True):
        if console:
            self.log_to_console(msg)
        self.log_to_file(msg)