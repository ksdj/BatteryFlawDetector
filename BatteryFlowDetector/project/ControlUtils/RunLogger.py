'''
Created on May 12, 2018

@author: qiuyx
'''

import logging.handlers

class RunLogger(logging.getLoggerClass()):
    def __init__(self, name, filename = '/opt/BatteryFlawDetector/logs/console.log'):
        super(RunLogger, self).__init__(self, name)
        self.filename = filename
        
        filehandler = logging.handlers.TimedRotatingFileHandler(self.filename, 'D', encoding = 'UTF8')
        filehandler.suffix = "%Y%m%d%H%M%S.log"
        filehandler.setLevel(logging.DEBUG)
        
        consolehandler = logging.StreamHandler()
        consolehandler.setLevel(logging.DEBUG)
        
        
        formatter = logging.Formatter("%(asctime)s - [%(levelname)s]  %(message)s")
        filehandler.setFormatter(formatter)
        consolehandler.setFormatter(formatter)
        
        self.addHandler(filehandler)
        self.addHandler(consolehandler)
        
