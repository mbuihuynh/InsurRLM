# encoding: utf-8
from utils.Slack import SlackWebhookBot
from utils.LoggingUtils import Logger

class CBase:
    def __init__(self):
        # logger
        try:
            self.logger = Logger(self.name)
        except:
            self.logger = Logger("CBase")
        self.m_oSlack  = SlackWebhookBot()