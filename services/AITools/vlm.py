from agentscope.model import OpenAIChatModel,OllamaChatModel


import os

class AzureChatModel(OpenAIChatModel):
    def __init__(self, model_name, api_key = None, stream = True, reasoning_effort = None, organization = None, client_args = None, generate_kwargs = None, azure_kwargs = None):
        super().__init__(model_name, api_key, stream, reasoning_effort, organization, client_args, generate_kwargs)
        import openai
        self.client = openai.AsyncAzureOpenAI(
            api_key=api_key,
            organization=organization,
            http_client=openai.DefaultAsyncHttpxClient(
                proxy=os.environ.get('HTTPS_PROXY')
            ),
            **azure_kwargs,
            **(client_args or {})
        )

  
class LlamaOCR(OllamaChatModel):
    def __init__(self, model_name, stream = False, options = None, keep_alive = "5m", enable_thinking = None, host = None, **kwargs):
        SUPPORTIVE_MODELS = ['qwen2.5vl:7b','DeepSeek-V3']
        assert model_name in SUPPORTIVE_MODELS,f'The system does not support this model - {model_name}'
        super().__init__(model_name, stream, options, keep_alive, enable_thinking, host, **kwargs)
    
        