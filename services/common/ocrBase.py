from utils.CBase import CBase
from utils.LoggingUtils import MessageTemplate

import os



class AIBase(CBase):
    def __init__(self,model_name:str,auths:dict):
        super().__init__()

        self.name = self.__class__.__name__

        self.model_name = model_name
        self.auths = auths

        self.endpoint = auths.get('endpoint')
        self.key = auths.get('key')

        # init client
        self._init_()

    def _init_(self):
        self.client = None

    def logging_message(self,message,msgObj:MessageTemplate=None,action="Action",error=True):
        if not msgObj:
            msgObj = MessageTemplate(self.name,action,"")

        msgObj.code = msgObj.vFAIL if error else msgObj.vINFO
        msgObj.msg = message

        if error:
            self.logger.error(str(msgObj))

        else:
            self.logger.info(str(msgObj))

    async def extract(self,filename):
        assert os.path.exists(filename) , "File is not existed!"
