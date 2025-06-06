import importlib
import os
from typing import List, Tuple
import pickle

from src.ragflow.document_loaders import get_loader
from src.ragflow.document_transformers import LLMPoweredRecursiveSplitter
from src.ragflow.llm_client import BaseLLMClient
# from src.ragflow.utils.logger import Logger
from src.ragflow.utils.walker import list_files_recursively


class ChunkingWorkflow:
    def __init__(self, yaml_config: dict) -> None:
        self._yaml_config: dict = yaml_config

        self._init_splitter()

        self._init_file_infos()
        return


    def _init_llm_client(self) -> None:

        llm_client_config = self._yaml_config["llm_client"]


        client_module = importlib.import_module(llm_client_config["module_path"])
        client_class = getattr(client_module, llm_client_config["class_name"])
        assert issubclass(client_class, BaseLLMClient)
        self._client = client_class(
            llm_config=llm_client_config["llm_config"],
            **llm_client_config.get("args", {}),
        )
        return

    def _init_splitter(self) -> None:
        self._init_llm_client()

        protocol_configs = self._yaml_config["chunking_protocol"]
        protocol_module = importlib.import_module(protocol_configs["module_path"])
        chunk_summary_protocol = getattr(protocol_module, protocol_configs["chunk_summary"])
        chunk_summary_refinement_protocol = getattr(protocol_module, protocol_configs["chunk_summary_refinement"])
        chunk_resplit_protocol = getattr(protocol_module, protocol_configs["chunk_resplit"])

        self._splitter = LLMPoweredRecursiveSplitter(
            llm_client=self._client,
            first_chunk_summary_protocol=chunk_summary_protocol,
            last_chunk_summary_protocol=chunk_summary_refinement_protocol,
            chunk_resplit_protocol=chunk_resplit_protocol,
            llm_config=self._yaml_config["llm_client"]["llm_config"],
            **self._yaml_config["splitter"],
        )
        return

    def _init_file_infos(self) -> None:
        input_setting: dict = self._yaml_config.get("input_doc_setting")
        output_setting: dict = self._yaml_config.get("output_doc_setting")
        assert input_setting is not None and output_setting is not None, (
            f"input_doc_setting and output_doc_setting should be provided!"
        )

        input_file_infos = list_files_recursively(
            directory=input_setting.get("doc_dir"),
            extensions=input_setting.get("extensions"),
        )

        output_dir = output_setting.get("doc_dir")
        output_suffix = output_setting.get("suffix", "pkl")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        self._file_infos: List[Tuple[str, str, str]] = [
            (doc_name, doc_path, os.path.join(output_dir, f"{os.path.splitext(doc_name)[0]}.{output_suffix}"))
            for doc_name, doc_path in input_file_infos
        ]
        return

    def run(self) -> None:
        for doc_name, input_path, output_path in self._file_infos:
            if os.path.exists(output_path) is True:
             continue

            doc_loader = get_loader(file_path=input_path, file_type=None)
            if doc_loader is None:
                continue
            docs = doc_loader.load()

            for doc in docs:
                doc.metadata.update({"filename": doc_name})

            chunk_docs = self._splitter.transform_documents(docs)

            with open(output_path, "wb") as fout:
                pickle.dump(chunk_docs, fout)
