import os

class Configs():
    def __init__(self):
        self.config = {}

    def getConfig(self):
        return self.config
    

class KafkaConfig(Configs):
    def __init__(self):
        super().__init__()
        self.config.update({'kafka_broker_list': os.getenv('BE_KAFKA_BROKER_LIST')})
        self.config.update({'auto_offset_reset': os.getenv('BE_KAFKA_AUTO_OFFSET_RESET')})

        self.config.update({'kafka_topic': os.getenv('BE_KAFKA_TOPIC')})
        self.config.update({'kafka_topic_key':  os.getenv('BE_KAFKA_TOPIC_KEY')})
        self.config.update({'kafka_groupid': os.getenv('BE_KAFKA_GROUPID')})
        self.config.update({'partition_number':  int(os.getenv('BE_KAFKA_PARTITION_TOPIC', default=3))})

