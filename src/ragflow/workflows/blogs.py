from typing import List
from src.ragflow.knowledge_retrievers.base_retriever import BaseRetriever
from src.ragflow.llm_client.zookeeper_api_client import ZooKeeperAIClient
from src.ragflow.utils.config_loader import load_class, load_protocol
from src.ragflow.workflows.webcopy import WebCopyWorkflow

class Blog_generation(WebCopyWorkflow):
        
        def __init__(self):
                self._init_agent()
                self._init_retriever()
                self._client = ZooKeeperAIClient()
                
        def _init_agent(self) -> None:
                self._init_protocol()

        
        def _init_protocol(self) -> None:
                self.blog_protocol = load_protocol(
                        module_path="src.ragflow.prompts.blogs",
                        protocol_name="blog_generation_protocol",
                        partial_values= {}
                )
                self.query_protocol = load_protocol(
                        module_path = "src.ragflow.prompts.blogs",
                        protocol_name="generation_qa_with_reference_protocol",
                        partial_values =  {}
                )
        def _init_retriever(self)-> None:
                retriever_class = load_class(
                        module_path="src.ragflow.knowledge_retrievers",
                        class_name="ChunkRetriever",
                        base_class=BaseRetriever,
                )
                self._retriever = retriever_class()
        

        def context_vectordb_retrieval(self,message):
                reference_chunks: List[str] = self._retriever.retrieve_contents(message)
                contents = [doc.page_content for doc, _ in reference_chunks]
                messages = self.query_protocol.process_input(content = message, references = contents)
                
                response = self._client.generate_content_with_messages(messages)
                output_dict: dict = self.query_protocol.parse_output(response)
                return output_dict["answer"]
        
        def run(self, message: str):
                self.content = self.context_vectordb_retrieval(message)
                messages = self.blog_protocol.process_input(content = self.content, references = message) 
                response = self._client.generate_content_with_messages(messages)
                return response
                