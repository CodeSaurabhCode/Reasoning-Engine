import math
import os
from typing import List, Tuple

from langchain_core.documents import Document

from src.ragflow.knowledge_retrievers.base_retriever import BaseRetriever
from src.ragflow.knowledge_retrievers.mixins.chroma_mixin import ChromaMetaType, ChromaMixin
from src.ragflow.utils.config_loader import load_callable, load_embedding_func
from src.ragflow.utils.document_ids import load_ids_and_chunks
from src.ragflow.knowledge_retrievers.query_parsers import question_as_query
from src.ragflow.utils.cosmos_vector_store import CosmosVectorStore
from azure.cosmos import CosmosClient, PartitionKey


def load_vector_store() -> CosmosVectorStore:

    COSMOS_URI = os.getenv("COSMOS_DB_URL")
    COSMOS_KEY = os.getenv("COSMOS_DB_KEY")
    COSMOS_DB = os.getenv("DATABASE_NAME", "KdiMarketing")
    COSMOS_CONTAINER = os.getenv("CONTAINER_NAME", "Documents")

    embedding = load_embedding_func()
    print(f"###################################################################")
    print(f"Cosmos DB: {COSMOS_KEY} - {COSMOS_URI} Building-Up finished.")

    cosmos_client = CosmosClient(COSMOS_URI, COSMOS_KEY)
    db = cosmos_client.create_database_if_not_exists(id=COSMOS_DB)
    container = db.create_container_if_not_exists(id=COSMOS_CONTAINER, partition_key=PartitionKey(path="/id"))

    vector_store = CosmosVectorStore(container=container, embedding_function=embedding)


    return vector_store


class ChunkRetriever(BaseRetriever, ChromaMixin):
    name: str = "ChunkRetriever"

    def __init__(self) -> None:
        super().__init__()

        self._init_chroma_mixin()

        self._query_parser = question_as_query

        self.vector_store = load_vector_store()


    def _get_relevant_strings(self, doc_infos: List[Tuple[Document, float]]) -> List[str]:
        contents = [doc.page_content for doc, _ in doc_infos]
        return doc_infos

    def _get_doc_and_score_with_query(self, query: str, **kwargs) -> List[Tuple[Document, float]]:
        retrieve_k = kwargs.get("retrieve_k", self.retrieve_k)
        retrieve_score_threshold = kwargs.get("retrieve_score_threshold", self.retrieve_score_threshold)
        return self._get_doc_with_query(query, self.vector_store, retrieve_k, retrieve_score_threshold)

    def retrieve_contents_by_query(self, query: str, **kwargs) -> List[str]:
        chunk_infos = self._get_doc_and_score_with_query(query, **kwargs)
        return self._get_relevant_strings(chunk_infos)

    def retrieve_contents(self, qa: str) -> List[str]:
        queries: List[str] = [qa]
        retrieve_k = math.ceil(self.retrieve_k / len(queries))

        all_chunks: List[str] = []
        for query in queries:
            chunks = self.retrieve_contents_by_query(query, retrieve_k=retrieve_k)
            all_chunks.extend(chunks)

        return all_chunks


class ChunkWithMetaRetriever(ChunkRetriever):
    name: str = "QaChunkWithMetaRetriever"

    def __init__(self, retriever_config: dict, log_dir: str) -> None:
        super().__init__(retriever_config, log_dir)

        assert "meta_name" in self._retriever_config, f"meta_name must be specified to use {self.name}"
        self._meta_name = self._retriever_config["meta_name"]

    def _get_relevant_strings(self, doc_infos: List[Tuple[Document, float]]) -> List[str]:
        meta_value_list: List[ChromaMetaType] = list(set([doc.metadata[self._meta_name] for doc, _ in doc_infos]))
        if len(meta_value_list) == 0:
            return []

        _, chunks, _ = self._get_infos_with_given_meta(
            store=self.vector_store,
            meta_name=self._meta_name,
            meta_value=meta_value_list,
        )

        return chunks
