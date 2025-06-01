from typing import Any, List, Sequence, Tuple
from langchain_core.documents import Document, BaseDocumentTransformer

from src.ragflow.llm_client import BaseLLMClient
from src.ragflow.prompts import CommunicationProtocol
from src.ragflow.utils.json_parser import parse_json


class LLMPoweredFilter(BaseDocumentTransformer):
    NAME = "LLMPoweredFilter"

    def __init__(
        self,
        llm_client: BaseLLMClient,
        filter_protocol: CommunicationProtocol,
        **kwargs,
    ) -> None:
        super().__init__()

        self._llm_client = llm_client

        self._filter_protocol: CommunicationProtocol = filter_protocol

    def _get_filter_info(self, content: str, **metadata) -> Tuple[str, bool]:
        messages = self._filter_protocol.process_input(content, **metadata)

        response = self._llm_client.generate_content_with_messages(messages=messages)

        return self._filter_protocol.parse_output(content=response, **metadata)

    def transform_documents(self, documents: Sequence[Document], keep_unrelated: bool = False, **kwargs: Any) -> Sequence[Document]:
        ret_docs: List[Document] = []
        for idx, doc in enumerate(documents):
            content = doc.page_content
            metadata = doc.metadata

            filter_info= self._get_filter_info(content, **metadata)
            filter_info = parse_json(filter_info)
            metadata.update({"filter_info": filter_info})
            ret_docs.append(doc)
        return ret_docs
