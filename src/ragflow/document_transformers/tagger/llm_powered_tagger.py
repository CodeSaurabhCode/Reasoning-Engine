from typing import Any, List, Sequence

from langchain_core.documents import Document, BaseDocumentTransformer

from src.ragflow.llm_client import BaseLLMClient
from src.ragflow.prompts import CommunicationProtocol


class LLMPoweredTagger(BaseDocumentTransformer):
    NAME = "LLMPoweredTagger"

    def __init__(
        self,
        llm_client: BaseLLMClient,
        tagging_protocol: CommunicationProtocol,
        tag_name: str = "tags",
        llm_config: dict = {},
        **kwargs,
    ) -> None:
        super().__init__()

        self._llm_client = llm_client
        self._llm_config = llm_config

        self._tagging_protocol = tagging_protocol
        self._tag_name = tag_name

    def _get_tags_info(self, content: str, **metadata) -> List[Any]:
        messages = self._tagging_protocol.process_input(content=content, **metadata)

        # Call client for tags
        response = self._llm_client.generate_content_with_messages(messages=messages, **self._llm_config)

        return self._tagging_protocol.parse_output(content=response, **metadata)

    # TODO: create new interface like "TextSplitter" for tagging?
    def transform_documents(self, documents: Sequence[Document], **kwargs: Any) -> Sequence[Document]:
        ret_docs: List[Document] = []
        for idx, doc in enumerate(documents):
            content = doc.page_content
            metadata = doc.metadata

            tags = self._get_tags_info(content, **metadata)
         
            full_tags = metadata.get(self._tag_name, []) + tags
            metadata.update({self._tag_name: full_tags})
            ret_docs.append(doc)
        return ret_docs
