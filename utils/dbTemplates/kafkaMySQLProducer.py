from copy import deepcopy
import sys
import json, time
from datetime import datetime, date
from decimal import Decimal
import datetime as dtTime


from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import BINLOG
from utils.CBase import CBase
from utils.dbLibs.CkafkaProducer import CKafka

from utils.connections.kafka import KafkaConfig

from utils.LoggingUtils import Logger, MessageTemplate

from inspect import stack
from pydash import get as get_by_path

class CMySQLProducerTemplate(CBase):
    def __init__(self, logger, classname, config):
        """
            config:
                mysql:  
                    >> tablename, mysql_host, mysql_port, mysql_user, mysql_pass,mysql_skip_duration
                        mysql_dbname, mysql_server_id
                kafka:
                    >> kafka_topic, kafka_topic_key
        
        """
        super(CMySQLProducerTemplate, self).__init__()
        self.m_oKafka = CKafka()
        self.classname = classname

        assert classname is not None and (classname != '') and len(classname) >= 5, '[classname] field should not be empty'

        if isinstance(config['tablename'], str):
            self.tablename = [config['tablename']]
        elif isinstance(config['tablename'], list):
            self.tablename = config['tablename']
        else:
            raise ValueError("[tablename] format is not supported!!!")

        self.logger = logger
        self.config = config
    

    def checkIncludeAdvanceMsg(self,messageIncludeAdvance:dict, message):
        """
            return True: msg is not produced
            return False: msg is produced
        """
        doc = message.get('fullDocument')
        
        if messageIncludeAdvance is None: return True
        
        iNum = len(messageIncludeAdvance)
        iCount = 0
        for key, arrValue in messageIncludeAdvance.items():
            v_mess = get_by_path(doc, key, None)
            if v_mess is not None: 
                if v_mess in arrValue:
                    iCount += 1
        
        if iCount == iNum:
            return True
        
        return False
    
    
    def checkConditionalMsg(self,messageIncludeAdvance:dict, message ):
        if 'fullDocument' not in message:
            return True
        
        if 'fullDocument' in message and message['fullDocument'] is None:
            return True
            
        ref_IncludeAdvance = self.checkIncludeAdvanceMsg(messageIncludeAdvance, message)
        
        
        if ref_IncludeAdvance:       
            return False
        else:
            return True
        
    
    def json_serial(self, obj):
        """JSON serializer for objects not serializable by default json code"""
        
        if isinstance(obj, (datetime, date)):
            serial = obj.isoformat()
            return serial
        if isinstance(obj, Decimal):
            return float(obj)
        else:
            print("Type '{}' for '{}' not serializable".format(obj.__class__, obj))
            return None

    def build_message(self, binlog_evt):
        #schema = {'table': getattr(binlog_evt, 'schema', '') + "." + getattr(binlog_evt, 'table', '')}
        schema = {'db': getattr(binlog_evt, 'schema', ''),  'coll':getattr(binlog_evt, 'table', '')}
        
        if binlog_evt.event_type in (BINLOG.WRITE_ROWS_EVENT_V2, BINLOG.WRITE_ROWS_EVENT_V1):
            # Insert
            return {'timestamp': binlog_evt.timestamp, 'operationType': 'insert', 'ns': schema,
                    'fullDocument': binlog_evt.rows[0]['values']}

        elif binlog_evt.event_type in (BINLOG.UPDATE_ROWS_EVENT_V2, BINLOG.UPDATE_ROWS_EVENT_V1):
            # Update
            return {'timestamp': binlog_evt.timestamp, 'operationType': 'update', 'ns': schema,
                    'fullDocument': binlog_evt.rows[0]['after_values']}
        elif binlog_evt.event_type in (BINLOG.DELETE_ROWS_EVENT_V2, BINLOG.DELETE_ROWS_EVENT_V1):
            # Delete
            return {'timestamp': binlog_evt.timestamp, 'operationType': 'delete', 'ns': schema,
                    'fullDocument': binlog_evt.rows[0]['values']}
        else:
            return None

    def producer_call(self):
        msgMain = MessageTemplate(f"[CMySQLProducerTemplate][{self.classname}]","producer_call","")
        mysql_settings = {'host': self.config['mysql_host'],
                        'port': self.config['mysql_port'],
                        'user': self.config['mysql_user'],
                        'passwd': self.config['mysql_pass']}
        

        messageIncludeAdvance   = self.config.get("message_include_advance", None)
        
        serverID = self.config['mysql_server_id']
        
        kafka_bootstrap_server = KafkaConfig().getConfig()['kafka_broker_list']
        TOPIC_NAME = self.config['kafka_topic']
        key_topic = self.config['kafka_topic_key']
        
        skipToTimeStamp = round(time.time()) - self.config['mysql_skip_duration']
        
        tempParam = {}
        tempParam = deepcopy(self.config)
        tempParam.pop('mysql_pass')
        msgMain.reps_data = {
            'config' : tempParam
        }
        self.logger.info(str(msgMain))
        
        producer_instance = self.m_oKafka.connect_kafka_producer(kafka_bootstrap_server, TOPIC_NAME)
        self.logger.info("[%s] Connected %s kafka successfully!", self.classname, kafka_bootstrap_server)
        
        self.stream = BinLogStreamReader(connection_settings=mysql_settings, server_id=serverID, resume_stream=True, blocking=True,
                                    only_schemas=self.config['mysql_dbname'], skip_to_timestamp=int(skipToTimeStamp),
                                    only_tables= self.tablename
                                    )
        msgMain.error_msg = "Begin BinLogStreamReader !"
        self.logger.info(str(msgMain))
        
        for evt in self.stream:
            msgStream = MessageTemplate(f"[CMySQLProducerTemplate][{self.classname}]","producer_call-stream","")
            if getattr(evt, 'table', '') == '':
                continue
            if evt.event_type in [BINLOG.WRITE_ROWS_EVENT_V2, BINLOG.UPDATE_ROWS_EVENT_V2, BINLOG.DELETE_ROWS_EVENT_V2,
                                BINLOG.WRITE_ROWS_EVENT_V1, BINLOG.UPDATE_ROWS_EVENT_V1, BINLOG.DELETE_ROWS_EVENT_V1]:
                msg = self.build_message(evt)
                
                if self.checkConditionalMsg(messageIncludeAdvance,msg): 
                    msgStream.error_msg = f"[CMySQLKafka][{msg}] Message is constrainted to publish"
                    # self.logger.info("[CMySQLKafka][%s] Message is constrainted to publish" % msg)
                    self.logger.info(str(msgStream))
                    continue
                msgStream.error_msg = f"[{msg}] Publish message: %s"
                # self.logger.info("[%s] Publish message: %s", self.classname, msg)
                self.logger.info(str(msgStream))
                self.m_oKafka.publish_message(producer_instance, TOPIC_NAME, key_topic,
                                json.dumps(msg, default=self.json_serial))
                     
    def run(self):
        
        try:
            print("Start to run the mysql watch streaming!!!")
            self.producer_call()
        except Exception as exc:
            strErrorMsg = '%s.%s Error: %s - Line: %s' % (self.__class__.__name__, str(exc), stack()[0][3], exc.__traceback__.tb_lineno) # give a error message
            self.logger.error(strErrorMsg)
            
            import pathlib
            msg_alert = "shutdown! please restart!!"
            print(msg_alert,str(exc))
            msg_alert = str(exc)
            path = str(pathlib.Path(__file__).absolute())
            self.m_oSlack.alert_job_failed(path, msg_alert)
            
if __name__ == '__main__':
    oProducer = CMySQLProducerTemplate()
    oProducer.run()

