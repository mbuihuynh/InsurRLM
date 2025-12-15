from services.common.ocrBase import AIBase
from services.AITools.configs import cfazure

from services.AITools.vlm import AzureChatModel

from utils.JinjaTemplate import TemplateLoading
from utils.LoggingUtils import MessageTemplate

import os, json

class AzureQuery(AIBase):
    def __init__(self, model_name, auths, root:str, template:str):
        super().__init__(model_name, auths)

        # setup configs/ environments
        env = cfazure.CONFIGS()
        self.model_name = model_name
        self.endpoint = env.ENDPOINT
        self.key = env.KEY
        self.version = env.VERSION

        self.tplObj = TemplateLoading(root,template)


    def _init_(self):
        
        self.client = AzureChatModel(
            model_name=self.model_name,
            api_key=self.key,
            azure_kwargs={
                        "azure_endpoint": self.endpoint,
                        "api_version": self.version,
                        "azure_deployment": self.model_id,
                    },
            stream=False
        )

    def _format_data(self,data_request):
        """
            standard parameters in template: who_are_you, global_context, local_context, requests : {name, formula}
        """

        final_outputs = []
        



    def _fill_data_into_template(self,data):

        content = self.tplObj.load_data(data)

        return content
    
    def _format_output(self,response):
        outs = {}
        res = True
        try:
            outs = json.loads(response)
            if isinstance(outs,dict): outs = [outs]
            return res, outs
        except Exception as exec:
            res = False

        return res, outs 

    def _merge_output(self, result, responses):
        for res in responses:
            result.append(res)

        return result       
    
    async def _extract_output(self,input_content):

        outputs = []

        response = await self.client(
            [{"role" : "user", "content" :input_content}]
        )

        output_contents = response.content

        self.logging_message(f"[Query] = {input_content}. [Response] = {output_contents}")

        for ou_item in output_contents:
            for k, v in ou_item.items():
                flg, outs = self._format_output(v)

                if flg:
                    outputs = self._merge_output(outputs,outs)

        return outputs

    async def execute(self,data_request:dict):

        msgMain = MessageTemplate(f"AzureQuery", "execute","")
        status = True
        results = []
        try:
            #01. format data as template definition
            flgsta, data = self._format_data(data_request)

            #02. loading data
            if flgsta:
                input_content = self.tplObj.load_data(data)


            #03. execute model
            if flgsta:
                results = await self._extract_output(input_content)


        except Exception as exec:
            status = False
            self.logging_message(str(exec),msgMain,"execute")


        return {
            'status' : status,
            'result' : results
        }



        

    



