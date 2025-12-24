import time
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from bson.json_util import dumps

from utils.dbLibs.checkpointProducer import RepeatedTimer, CCheckPointProducer
from utils.LoggingUtils import Logger,MessageTemplate
import json
from inspect import stack
from pydash import get as get_by_path
from utils.connections.global_env import *
import os

    

MONGO_MAX_RETRY_CONNECTION = int(os.get('MONGO_MAX_RETRY_CONNECTION','3'))

logger = Logger('CKafka')
class CKafka:
    def __init__(self):
        pass
           
    def checkAndCreateTopics(self, kafka_broker_list=None, topic_name=None, partition_num=1, replication_factor=3):
        assert topic_name is not None
        assert partition_num is not None
        assert replication_factor is not None
        try:
            a = KafkaAdminClient(bootstrap_servers=kafka_broker_list)
            if topic_name in a.list_topics():
                return True

            new_topic = [NewTopic(name=topic_name, num_partitions=partition_num, replication_factor=replication_factor)]
            a.create_topics(new_topic)
        except Exception as ex:
            logger.info(str(ex))

        return True

    def publish_message(self, producer_instance, topic_name, key, value):
        try:
            key_bytes = bytes(key, encoding='utf-8')
            value_bytes = bytes(value, encoding='utf-8')
            producer_instance.send(topic_name, key=key_bytes, value=value_bytes)
            producer_instance.flush()
            logger.info('Message published successfully.')
        except Exception as ex:
            logger.info('Exception in publishing message')
            logger.info(str(ex))

    def connect_kafka_producer(self, bootstrap_servers, topic_name='default'):
        self.checkAndCreateTopics(bootstrap_servers, topic_name)
        _producer = None
        try:
            _producer = KafkaProducer(bootstrap_servers=bootstrap_servers, api_version=(0, 10), acks='all',
                                    retries=2147483647)
        except Exception as exc:
            msg = '%s.%s Error: %s - Line: %s' % (self.__class__.__name__, str(exc), stack()[0][3], exc.__traceback__.tb_lineno) # give a error message
            logger.error(f"Exception while connecting Kafka: {msg}")
        finally:
            return _producer
          
    def producer(self, params, hook_function=None):
        pass