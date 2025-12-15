from dataclasses import dataclass, asdict
import os


@dataclass
class CONFIGS:
    
    ENDPOINT = os.environ.get('AZURE_DOC_INTEL_HOST')
    KEY = os.environ.get('AZURE_DOC_INTEL_KEY')
    MODEL_ID = 'prebuilt-read'