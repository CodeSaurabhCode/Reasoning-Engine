import importlib
from typing import Optional
from helpers.word_document import create_docx
from src.ragflow.llm_client.base import BaseLLMClient
from src.ragflow.utils.config_loader import load_protocol
from src.ragflow.document_loaders import get_loader
from langchain_core.documents import Document, BaseDocumentTransformer

class WebCopyWorkflow:
    def __init__(self, yaml_config: dict):
        self._yaml_config: dict = yaml_config
        
        self._init_agent()

    def _init_agent(self) -> None:
        self._init_protocol()
        self._init_llm_client()
        self.__init_filter()

    def _init_protocol(self) -> None:
        self.web_protocol = load_protocol(
            module_path=self._yaml_config["protocol"]["module_path"],
            protocol_name=self._yaml_config["protocol"]["attr_name"],
            partial_values=self._yaml_config["protocol"].get("partial_values", {}),
        )
    
    def _init_llm_client(self) -> None:
        llm_client_config = self._yaml_config["llm_client"]
        client_module = importlib.import_module(llm_client_config["module_path"])
        client_class = getattr(client_module, llm_client_config["class_name"])
        assert issubclass(client_class, BaseLLMClient)
        self.llm_config = llm_client_config["llm_config"]

        self._client = client_class(
            llm_config=self.llm_config,
            **llm_client_config.get("args", {}),
        )
    def __init_filter(self) -> None:
        module_path = self._yaml_config["filter"]["module_path"]
        class_name = self._yaml_config["filter"]["class_name"]
        filter_module = importlib.import_module(module_path)
        filter_class = getattr(filter_module, class_name)
        assert issubclass(filter_class, BaseDocumentTransformer)
        self._filter = filter_class(self._client, self.web_protocol, self.llm_config)

    def evaluate(self) -> None:
        return None

    def run(self, qa: Optional[str]=None) -> dict:
        doc_name = self._yaml_config["PO_doc_path"]

        doc_loader = get_loader(file_path=doc_name, file_type=None)
        doc_content = doc_loader.load()
        # doc_content = doc_loader.extract_tables()
        texts, metadatas = [], []
        for doc in doc_content:
            texts.append(doc.page_content)
            metadatas.append(doc.metadata)
        # messages = self.web_protocol.process_input(content=qa, references=dict(doc_content[0]))
        response = self._filter.transform_documents(doc_content)

        # response = self._client.generate_content_with_messages(messages, **self.llm_config)
        output_dict: dict = self.web_protocol.parse_output(response[0].metadata['filter_info'])

        filename = create_docx(output_dict)
        print(f"Document saved as {filename}")

        return output_dict