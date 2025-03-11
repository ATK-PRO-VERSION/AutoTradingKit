import logging
from atklip.gui.qfluentwidgets.common.icon import *
# Gets or creates a logger
logger_ = logging.getLogger(__name__)  
# set log level
# logger_.setLevel(logging.WARNING)
# define file handler and set formatter
log_path = get_real_path("atklip/appdata")
file_handler = logging.FileHandler(filename=f'{log_path}/logfile.log')
formatter    = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
file_handler.setFormatter(formatter)
# add file handler to logger
logger_.addHandler(file_handler)

class logger():
    def writer(self,log_type:str, content_log:str):
        log_type = log_type.lower()
        #content_log = content_log.encode('ascii', 'replace').decode('ascii')
        if log_type == 'info':
                logger_.setLevel(logging.INFO)
                logger_.info(content_log)
        elif log_type == 'warning':
                logger_.setLevel(logging.WARNING)
                logger_.warning(content_log)
        elif log_type ==  'error':
                logger_.setLevel(logging.ERROR)
                logger_.error(content_log)
        elif log_type ==  'critical':
                logger_.setLevel(logging.CRITICAL)
                logger_.critical(content_log)

# global AppLogger

AppLogger = logger()