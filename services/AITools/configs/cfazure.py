from dataclasses import dataclass, asdict
import os


@dataclass
class CONFIGS:

    ENDPOINT = os.environ.get('AZURE_CHATBOT_HOST')
    KEY = os.environ.get('AZURE_CHATBOT_KEY')
    MODEL_ID = os.environ.get('AZURE_MODEL_NAME')
    VERSION = os.environ.get('AZURE_CHATBOT_VERSION')


    NBR_TASKS = 10