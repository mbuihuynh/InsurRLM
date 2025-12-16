from utils.CBase import CBase

import jinja2
from jinja2schema import infer
import os, json
from pathlib import Path


class TemplateLoading(CBase):
    def __init__(self, root_template, template_name):
        super().__init__()
        self.root_template = root_template
        self.template_name = template_name
        template_path = os.path.join(root_template,f"{template_name}.tpl")

        self.logger.info(f"TemplateLoading is {template_path}")

        assert os.path.isfile(template_path) and os.path.splitext(template_path)[1] == '.tpl',f"Invalid {template_path} file"

        self.template_path = template_path


    def load_data(self,data) -> str:
        template_path = self.template_path

        strTemplateDir = Path(template_path).parent
        fileName = Path(template_path).name
        templateFilePath = jinja2.FileSystemLoader( strTemplateDir )
        jinjaEvn = jinja2.Environment(loader=templateFilePath, trim_blocks=True, lstrip_blocks=True)
        jTemplate = jinjaEvn.get_template(fileName)

        return jTemplate.render(data)
    

class AgentTask(CBase):
    
    def __init__(self):
        super().__init__()

        self.placeholder = {
            'tasks' : {
                'name' : 'name',
                'personas' : 'personas',
                'goal' : 'goal',
                'task' : 'task'
            },
            'who_are_you' : 'who_are_you',
            'global_context' : 'global_context',
            'local_context' : 'local_context'
        }

        self.assessment = ['who_are_you','local_context']

    def _load_task(self,task_list:list,params:dict): ### combine data_set and rule_set

        outs = []

        params = self.placeholder.get('tasks') if not params else params

        for task in task_list:
            item = {}
            for k, v in task.items():
                if k in params.keys():
                    item.update({k:v})

            outs.append(item)

        return outs
    
    def _load_context(self,data_context:dict,params:str):
        
        res = None

        if params in data_context.keys():
            res = data_context.get(params)
        
        return res
    
    def _valid_task(self,result:dict):

        for acq_key in self.assessment:
            if not (acq_key in result.keys()):
                self.logger.error(f"The info {acq_key} need identified to be Agent better!!!")
                return False

        return True
    
    def __call__(self, data_content:dict, task_list:list):
        
        result = {}

        for k, v in self.placeholder.items():
            if isinstance(v, dict):
                act_v = self._load_task(task_list,v)

            else:
                act_v = self._load_context(data_content,v)

            if act_v:
                result.update({k:act_v})

        flag = self._valid_task(result)

        return flag, result
    