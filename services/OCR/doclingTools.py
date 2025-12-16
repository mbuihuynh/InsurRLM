from services.common.ocrBase import AIBase

from docling.document_converter import DocumentConverter,PdfFormatOption,InputFormat
from docling.datamodel.pipeline_options import  PdfPipelineOptions, PipelineOptions, TesseractOcrOptions, EasyOcrOptions, RapidOcrOptions, OcrMacOptions

from docling.datamodel.document import ConversionResult

class DocumentIntelligentLayout(AIBase):
    def __init__(self, model_name, auths, format="Markdown"):
        super().__init__(model_name, auths)

        assert format in ["Markdown","HTML"],f"We don't support this value {format} but `Markdown` and `HTML` "

        self.format = format

    
    def _init_(self):
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True
        pipeline_options.ocr_options = TesseractOcrOptions()
        self.client = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)})
        
    
    def savetoMarkdown(self,result:ConversionResult):
        return result.document.export_to_markdown()
    
    def savetoHTML(self,result:ConversionResult):
        return result.document.export_to_html()

    def extract(self, filename):
        super().extract(filename)

        fnc_name = f"saveto{self.format}"
        document = None
        flg = True
        try:
            result = self.client.convert(filename)

            if hasattr(self, fnc_name) and callable(functionCaller := getattr(self, fnc_name)):
                document = functionCaller(result)

        except Exception as exec:
            flg = False
            self.logging_message(str(exec),action="extract",error=True)

        return {
            'status' : flg,
            'output' : document
        }



