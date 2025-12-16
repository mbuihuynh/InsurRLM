from services.common.ocrBase import AIBase


class MAS(AIBase):
    def __init__(self, model_name, auths):
        super().__init__(model_name, auths)


    async def execute(self,contents:dict,agent_list:list):
        """
            content:dict
            agent_list: the list of agents
        """

        



