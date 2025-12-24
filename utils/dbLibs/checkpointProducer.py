from inspect import stack
import threading
import time
import os

from utils.LoggingUtils import Logger
from utils.connections.global_env import *

from utils.connections import redis

MODE_TEMPLATE = int(os.getenv('REDIS_KAFKA_MODE', default="cluster"))

RedisConnection = redis.getRedisConnection(MODE_TEMPLATE)
    
LOGGER = Logger('CheckPointProducer')

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.next_call = time.time()
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self.next_call += self.interval
            self._timer = threading.Timer(self.next_call - time.time(), self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

hkey = DATALAKE_REDIS_HASHKEY_MONGO_PRODUCER

class CCheckPointProducer(object):
    def __init__(self):
        pass
    
    @staticmethod
    def setCheckPoint(master, key_check_point, data):        
        """
        Attempt to set a checkpoint in Redis with retry logic.
        """
        retries = int(os.getenv('MAX_RETRY_CONNECTION', default="5"))
        for attempt in range(retries):
            try:
                if len(data) > 0:
                    LOGGER.info("check_pointed")
                    master.hset(hkey, key_check_point, str(data[-1]))
                    data.clear()
                else:
                    LOGGER.info('Do you have checkpoint?')
                return
            
            except Exception as exc:
                msg = '%s Error: %s - Line: %s' % (str(exc), stack()[0][3], exc.__traceback__.tb_lineno) # give a error message
                LOGGER.error(f"[SetCheckPoint][hset:{hkey}][field:{key_check_point}]{msg}")
                
                if attempt < retries - 1:
                    LOGGER.info(f"Retrying connect to redis... ({attempt + 1}/{retries})")
                    time.sleep(0.2)
                    master = RedisConnection().getConnection()
                else:
                    LOGGER.error("Failed to set checkpoint in Redis after multiple attempts")
                    
    @staticmethod
    def getCheckPoint(master, key_check_point):    
        """
        Attempt to get a checkpoint from Redis with retry logic.
        """
        retries = int(os.getenv('MAX_RETRY_CONNECTION', default="5"))
        for attempt in range(retries):
            try:
                checkpoint = master.hget(hkey, key_check_point)
                if checkpoint is None:
                    LOGGER.info('i do not checkpoint')
                elif checkpoint == 'None':
                    checkpoint = None
                return checkpoint
            except Exception as exc:
                msg = '%s Error: %s - Line: %s' % (str(exc), stack()[0][3], exc.__traceback__.tb_lineno) # give a error message
                LOGGER.error(f"[getCheckPoint][hget:{hkey}][field:{key_check_point}]{msg}")
                
                if attempt < retries - 1:
                    LOGGER.info(f"Retrying connect to redis... ({attempt + 1}/{retries})")
                    time.sleep(0.2)
                    master = RedisConnection().getConnection()
                else:
                    LOGGER.error("Failed to get checkpoint in Redis after multiple attempts")
                    return None