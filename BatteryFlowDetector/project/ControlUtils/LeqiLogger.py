import logging, logging.handlers

def logger(name, loc):
    log = logging.getLogger(name)
    log.setLevel(level = logging.DEBUG)
    filehandler = logging.handlers.TimedRotatingFileHandler(loc, 'D', encoding = 'UTF8')
    filehandler.suffix = "%Y%m%d%H%M%S.log"
    filehandler.setLevel(logging.DEBUG)
    
    consolehandler = logging.StreamHandler()
    consolehandler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter("%(asctime)s - %(name)s [%(levelname)s]  %(message)s")
    filehandler.setFormatter(formatter)
    consolehandler.setFormatter(formatter)
    
    log.addHandler(filehandler)
    log.addHandler(consolehandler)

    return log



