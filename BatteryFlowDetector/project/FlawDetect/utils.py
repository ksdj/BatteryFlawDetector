import os
import os.path as osp
import logging
import logging.handlers 
import sys
import json

# config utils
class Config:
  Prj_Root = os.path.abspath(os.path.dirname(__file__))

  def getConfig(self, key, defval):
    config_dir = Config.Prj_Root
    # if it is a packaged file
    if 'python' not in sys.executable:
      config_dir = os.path.dirname(os.path.realpath(sys.executable))

    fp = os.path.abspath(os.path.join(config_dir,'config.json'))
    if not os.path.exists(fp):
        return defval

    configstr = open(fp).read()

    cfg = json.loads(configstr)

    if not key in cfg:
        return defval

    return cfg[key]

config = Config()

# logging util
_logfolder = osp.join(osp.dirname(__file__),config.getConfig('log_path', 'output/'))
# init log with default config
def initlogging(file_name, log_name=None, logerlevel=logging.DEBUG, consolelevel= logging.DEBUG,
                filelevel=logging.INFO, propagate=False):
    thelogger = logging.getLogger(log_name)
    thelogger.setLevel(logerlevel)
    thelogger.propagate = propagate

    fmt = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')

    cl = logging.StreamHandler()
    cl.setLevel(consolelevel)
    cl.setFormatter(fmt)
    thelogger.addHandler(cl)

    filepath = osp.join(osp.dirname(__file__),config.getConfig('log_path', 'output/'),file_name)
    if filepath:
        fl = logging.handlers.RotatingFileHandler(filepath,
                                                  mode='w',
                                                  maxBytes=2 * 1024 * 1024, backupCount=5)
        fl.setLevel(filelevel)
        fl.setFormatter(fmt)
        thelogger.addHandler(fl)
