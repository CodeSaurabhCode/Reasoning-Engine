import base64
from typing import List, Optional
from src.helpers.word_document import create_docx
from src.ragflow.document_transformers.filter.llm_powered_filter import LLMPoweredFilter
from src.ragflow.knowledge_retrievers.base_retriever import BaseRetriever
from src.ragflow.llm_client.zookeeper_api_client import ZooKeeperAIClient
from src.ragflow.utils.config_loader import load_class, load_protocol
from src.ragflow.document_loaders import get_loader


class WebCopyWorkflow:
    def __init__(self, ):

        self._init_retriever()
        self._client = ZooKeeperAIClient()

        self.web_protocol = load_protocol(
            module_path="src.ragflow.prompts.web_copy",
            protocol_name="web_copy_protocol",
            partial_values= {}
        )
        
        self.filter_protocol = load_protocol(
            module_path="src.ragflow.prompts.web_copy",
            protocol_name="filtering_protocol",
            partial_values= {}
        )
        self.query_protocol = load_protocol(
            module_path="src.ragflow.prompts.web_copy",
            protocol_name="generation_qa_with_reference_protocol",
            partial_values={}
        )
    
        self._filter = LLMPoweredFilter(self._client, self.web_protocol)
    
    def _init_retriever(self)-> None:
        retriever_class = load_class(
            module_path="src.ragflow.knowledge_retrievers",
            class_name="ChunkRetriever",
            base_class=BaseRetriever,
        )
        self._retriever = retriever_class()

    def evaluate(self) -> None:
        return None

    def run(self, file_path, prompt: Optional[str]=None) -> dict:
        texts, metadatas = [], []
        self.filtering_instructions = None
        if file_path is not None:

            doc_loader = get_loader(file_path=file_path, file_type=None)
            
            doc_content = doc_loader.load()
            
            for doc in doc_content:
                texts.append(doc.page_content)
                metadatas.append(doc.metadata)
                
            self.filtering_instructions  = self._filter.transform_documents(doc_content)

    
        else:
            reference_chunks: List[str] = self._retriever.retrieve_contents(prompt)
            texts = [doc.page_content for doc, _ in reference_chunks]
            metadatas = [doc.metadata for doc, _ in reference_chunks]
              
            
        messages = self.web_protocol.process_input(content=self.filtering_instructions, references=texts) if self.filtering_instructions else self.web_protocol.process_input(content=prompt, references=texts)

        response = self._client.generate_content_with_messages(messages)
        output_dict: dict = self.web_protocol.parse_output(response)

        doc_bytes = create_docx(output_dict)
        encoded_doc = base64.b64encode(doc_bytes).decode('utf-8')
        return encoded_doc

    def answer(self, message, chat_history):
        reference_chunks: List[str] = self._retriever.retrieve_contents(message)
        contents = [doc.page_content for doc, _ in reference_chunks]
        messages = self.query_protocol.process_input(content=message, references=contents)

        response = self._client.generate_content_with_messages(messages)
        output_dict: dict = self.query_protocol.parse_output(response)
        return output_dict["answer"]
    
    def glossary(self, prompt):
        reference_chunks: List[str] = self._retriever.retrieve_contents(prompt)
        
        glossary_set = set()
        for doc, _ in reference_chunks:
            glossary_items = doc.metadata.get("glossary")
            if isinstance(glossary_items, list):
                glossary_set.update(glossary_items)
            elif isinstance(glossary_items, str):
                glossary_set.add(glossary_items)
        
        return list(glossary_set)

    
    
    