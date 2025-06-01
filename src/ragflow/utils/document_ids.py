
import pickle
from typing import List
from langchain_core.documents import Document


from src.ragflow.utils.walker import list_files_recursively

def load_ids_and_chunks(chunk_file_dir: str):
    chunks: List[Document] = []
    chunk_idx: int = 0
    for doc_name, doc_path in list_files_recursively(directory=chunk_file_dir, extensions=["pkl"]):
        with open(doc_path, "rb") as fin:
            chunks_in_file: List[Document] = pickle.load(fin)

        for doc in chunks_in_file:
            doc.metadata.update(
                {
                    "filename": doc_name,
                    "chunk_idx": chunk_idx,
                }
            )
            chunk_idx += 1

        chunks.extend(chunks_in_file)

    return None, chunks