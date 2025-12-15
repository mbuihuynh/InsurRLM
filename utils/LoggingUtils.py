import json
from utils.CDateTime import get_current_unixtime

def Logger(name, max_MBbyte=500, log_level=None, log_file=None):
    import logging.handlers

    logger = logging.getLogger(name)
    logger.propagate = False

    # Prevent duplicate log messages
    if (logger.hasHandlers()):
        logger.handlers.clear()
    if log_level:
        logger.setLevel(log_level)
    else:
        logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
    if log_file:
        # print("LOGGING TO %s" % log_file)
        fh = logging.handlers.RotatingFileHandler(log_file, maxBytes=max_MBbyte * 1024 * 1024, backupCount=3, mode='a')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    else:
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

class MessageTemplate(object):
    vOK = "OK"
    vFAIL = "FAIL"
    vINFO = "INFOS"
    
    def __init__(self,module,action,type=None, **kwargs):
        self.start = get_current_unixtime()
        self.module = module 
        self.action = action
        self.kwargs = kwargs
        self.code = ""
        self.type = type
        self.msg = ""
        self.reps_data = {}

    def __str__(self):
        end = get_current_unixtime()
        msg = {
            "module" : self.module,
            "action" : self.action,
            "start" : self.start,
            "end" : end,
            "duration_ms" : end - self.start,
            "type" : self.vINFO if not self.type else self.type,
            "code" : self.vOK if self.code == "" else self.code,
            "msg" : self.msg,
            "data" : self.kwargs,
            "reps_data" : self.reps_data
        }
        return '%s' % (msg) 

if __name__ == "__main__":
    msg = MessageTemplate("Module","Which action",message="test", service = "service")
    msg.code = "ERR_123"
    msg.reps_data = {'a' : 123}
    print("Msg=",str(msg))