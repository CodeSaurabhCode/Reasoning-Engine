import os
from pathlib import Path
from typing import Optional
import logging
from src.ragflow.document_loaders.common import DocumentType


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def infer_file_type(file_path: str) -> Optional[str]:
    if os.path.exists(file_path):
        file_extension = Path(file_path).suffix[1:]
        for file_type in DocumentType:
            if file_extension in file_type.value:
                return file_type
        
        logger.warning(f"File type not supported: {file_extension}")
        return None
    else:
        ## TODO : URL handling
        pass
    return None


def get_loader(file_path: str, file_type: DocumentType = None) -> Optional[str]:
    inferred_file_type = file_type
    if file_type is None:
        inferred_file_type = infer_file_type(file_path)
        if inferred_file_type is None:
            logger.error("File type could not be inferred.")
            return None
    
    if inferred_file_type == DocumentType.word:
        from langchain_community.document_loaders import UnstructuredWordDocumentLoader
        # from helpers.docx_extractor import DocxTableExtractor
        # return DocxTableExtractor(file_path)
        return UnstructuredWordDocumentLoader(file_path)
    
    elif inferred_file_type == DocumentType.csv:
        from langchain_community.document_loaders import CSVLoader
        return CSVLoader(file_path)
    
    elif inferred_file_type == DocumentType.excel:
        from langchain_community.document_loaders import UnstructuredExcelLoader
        return UnstructuredExcelLoader(file_path, mode="elements")
    
    elif inferred_file_type == DocumentType.pdf:
        from langchain_community.document_loaders import PyMuPDFLoader
        return PyMuPDFLoader(file_path)
    
    elif inferred_file_type == DocumentType.text:
        from langchain_community.document_loaders import TextLoader
        return TextLoader(file_path)
    elif inferred_file_type == DocumentType.ppt:
        from langchain_community.document_loaders import UnstructuredPowerPointLoader
        return UnstructuredPowerPointLoader(file_path)
    else:
        if file_type is not None:
            logger.error(f"Document type not supported: {file_type}")
        else:
            logger.error(f"Document loader for inferred file type { infer_file_type } not found.")