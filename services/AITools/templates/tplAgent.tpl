{% comment %}
- who_are_you: define who the agent are, what skill it excels at.
- global_context: system prompting
- local_context: input contents as documents/input...
- tasks: the agent will execute these tasks in the details
    - name:     task name
    - personas:  describe an internal skill that guides AI to think
    - goal:     identify the goal achievement
    - task:  describe step by step to implement this task
{% endcomment %}

You are {{who_are_you}}. If you can't proceed the formula, please return `empty`. And then output to list of json format without any thoughts {'name':name, 'output':value}
{{global_context}}
{{local_context}}
--
{% for item in tasks -%}
Name: {{item['name']}}
Personas: {{item['personas']}}
Goal: {{item['goal']}}
Task: {{item['task']}}
Output:
--
{% endfor -%}