import os
import importlib
from typing import List, Tuple
from src.ragflow.llm_client.zookeeper_api_client import ZooKeeperAIClient
from src.ragflow.document_loaders import get_loader
from src.ragflow.knowledge_retrievers.base_retriever import BaseRetriever
from src.ragflow.llm_client.base import BaseLLMClient
from src.ragflow.utils.config_loader import load_class, load_protocol
from src.ragflow.document_transformers import LLMPoweredTagger
from src.ragflow.workflows.webcopy import WebCopyWorkflow
from src.ragflow.workflows.tagging import TaggingWorkflow
from src.ragflow.utils.walker import list_files_recursively

class Glossary_generation(WebCopyWorkflow):
        
        def __init__(self):
                self._init_agent()
                self.__init_retriever()
                
        def _init_agent(self) -> None:
                self._init_protocol()
        
        def _init_protocol(self) -> None:
                self.glossary_protocol = load_protocol(
                        module_path="src.ragflow.prompts.glossary",
                        protocol_name="glossary_generation_protocol",
                        partial_values={}
                )
                self.query_protocol = load_protocol(
                        module_path = "src.ragflow.prompts.glossary",
                        protocol_name="generation_qa_with_reference_protocol",
                        partial_values = {}
                )
                self.glossary_chat_protocol = load_protocol(
                        module_path="src.ragflow.prompts.glossary",
                        protocol_name="glossary_chat_protocol",
                        partial_values={}  
                )
        def __init_retriever(self)-> None:
                retriever_class = load_class(
                        module_path="src.ragflow.knowledge_retrievers",
                        class_name="ChunkRetriever",
                        base_class=BaseRetriever,
                )
                self._retriever = retriever_class()      
                self._client = ZooKeeperAIClient()

        def context_vectordb_retrieval(self,message):
                reference_chunks: List[str] = self._retriever.retrieve_contents(message)
                messages = self.query_protocol.process_input(content = message, references = reference_chunks)
                
                response = self._client.generate_content_with_messages(messages)
                output_dict: dict = self.query_protocol.parse_output(response)
                return output_dict["answer"]
        #  For parsing document glossary generation
        def answer(self, message: str, file_path: str = None):
                doc_name = file_path
                doc_loader = get_loader(file_path=doc_name, file_type=None)
                doc_content = doc_loader.load()
                texts, metadatas = [],[]
                for doc in doc_content:
                        texts.append(doc.page_content)
                        metadatas.append(doc.metadata)
                messages = self.glossary_protocol.process_input(content=texts, references = message)
                response = self._client.generate_content_with_messages(messages)
                return response
        #  Fro glossary document chat-bot
        def glossary_answer(self, message: str):
                self.content = self.context_vectordb_retrieval(message)
                messages = self.glossary_chat_protocol.process_input(content = self.content, references = message)
                response = self._client.generate_content_with_messages(messages)
                return response
                
class glossaryGenerationFlow(TaggingWorkflow):
        def __init__(self, yaml_config: dict)-> None:
                self._yaml_config: dict = yaml_config
                self._init_tagger()

                self._init_file_infos()
                self._init_file_loader_and_saver()
                return
                
        def _init_file_infos(self) -> None:
                input_setting: dict = self._yaml_config.get("input_doc_setting", None)
                output_setting: dict = self._yaml_config.get("output_doc_setting", None)

                if input_setting is None or output_setting is None:
                        self._file_infos = None
                        return

                input_file_infos = list_files_recursively(
                        directory=input_setting.get("doc_dir"),
                        extensions=input_setting.get("extensions"),
                )

                output_dir = output_setting.get("doc_dir")
                output_suffix = output_setting.get("suffix")
                if not os.path.exists(output_dir):
                        os.makedirs(output_dir, exist_ok=True)

                self._file_infos: List[Tuple[str, str, str]] = [
                        (doc_name, doc_path, os.path.join(output_dir, f"{os.path.splitext(doc_name)[0]}.{output_suffix}"))
                        for doc_name, doc_path in input_file_infos
                ]
                return
        
        def _init_tagger(self) -> None:
                self._init_llm_client()

                tagger_config: dict = self._yaml_config["glossary"]

                # Dynamically import the tagging communication protocol
                self._tagging_protocol = load_protocol(
                module_path=tagger_config["tagging_protocol"]["module_path"],
                protocol_name=tagger_config["tagging_protocol"]["attr_name"],
                )

                self._tag_name: str = tagger_config["tag_name"]

                self._tagger = LLMPoweredTagger(
                llm_client=self._client,
                tagging_protocol=self._tagging_protocol,
                tag_name=self._tag_name,
                llm_config=self._yaml_config["llm_client"]["llm_config"],
                )

                return
        def _run_multi(self) -> None:
                for doc_name, input_path, output_path in self._file_infos:
                        if os.path.exists(output_path) is True:
                                continue
                        docs = self._load_func(input_path)
                        tagged_docs = self._tagger.transform_documents(docs)
                        self._save_func(tagged_docs, output_path)
        def run(self):
                if self._file_infos is None:
                        self._run_single()
                else:
                        self._run_multi()
                return