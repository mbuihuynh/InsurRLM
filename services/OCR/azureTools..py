from services.common.ocrBase import AIBase

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult,DocumentContentFormat
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
import os


class DocumentIntelligentLayout(AIBase):
    def __init__(self, model_name, auths):
        super().__init__(model_name, auths)

        self.confidence_score = {}

        self.model_name = 'prebuilt-layout'

        os.environ['HTTP_PROXY'] = os.environ.get('HTTP_PROXY')
        os.environ['HTTPS_PROXY'] = os.environ.get('HTTPS_PROXY')
        

    def _init_(self):
        self.client = DocumentIntelligenceClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.key)
        )


    async def extract(self, filename) -> list:
        super().extract(filename)

        with open(filename, 'rb') as f:
            source_bytes = f.read()

        poller = await self.client.begin_analyze_document(self.model_name
                                                    , AnalyzeDocumentRequest(bytes_source=source_bytes)
                                                    , output_content_format=DocumentContentFormat.MARKDOWN
                                                    )

        result: AnalyzeResult = poller.result()
        document = result.content
        

        return document