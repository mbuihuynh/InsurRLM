You are {{who_are_you}}. If you can't proceed the formula, please return `empty`. And then output to list of json format without any thoughts {'name':name, 'output':value}
{{global_context}}
{{local_context}}
--
{% for request in requests -%}
name: {{request['name']}}
formula: {{request['formula']}}
output:
--
{% endfor -%}