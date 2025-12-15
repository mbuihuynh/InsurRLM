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
    

class transfContextData(CBase):
    
    def __init__(self,template:str):
        super().__init__()

        self.template = template

        self.placeholder = {
            'list_of_question' : {
                'context' : 'context',
                'name' : 'name',
                'input' : 'input',
                'formula' : 'formula'
            }
        }

    def _load_data(self,data_set,rule_set): ### combine data_set and rule_set

        outs = []
        for k, v in data_set.items():
            rule = rule_set.get(k)
            if rule:
                item = {
                    'name' : k,
                    'input' : v,
                    'formula' : rule
                }

                outs.append(item)

        return outs
    
    def __call__(self, data_set:dict, rule_set:dict, list_field:list):
        
        result = {}

        for k, v in self.placeholder.items():
            if not(k in list_field):
                continue

            if isinstance(v, dict):
                act_v = self._load_data(data_set,rule_set)


            result.update({k:act_v})

        return result
    