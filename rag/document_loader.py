import os
from typing import List
from langchain.document_loaders import (
    TextLoader,
    UnstructuredMarkdownLoader,
    PyMuPDFLoader,
    DirectoryLoader
)
from langchain.schema import Document

class DocumentLoader:
    SUPPORTED_EXTENSIONS = {
        '.txt': TextLoader,
        '.md': UnstructuredMarkdownLoader,
        '.pdf': PyMuPDFLoader
    }
    
    @classmethod
    def load_file(cls, file_path: str) -> List[Document]:
        _, ext = os.path.splitext(file_path)
        
        if ext.lower() not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"不支持的文件格式: {ext}")
        
        loader_class = cls.SUPPORTED_EXTENSIONS[ext.lower()]
        loader = loader_class(file_path)
        
        try:
            documents = loader.load()
            for doc in documents:
                doc.metadata['source'] = file_path
            return documents
        except Exception as e:
            raise ValueError(f"加载文件失败: {str(e)}")
    
    @classmethod
    def load_directory(cls, dir_path: str) -> List[Document]:
        all_docs = []
        
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file)
                
                if ext.lower() in cls.SUPPORTED_EXTENSIONS:
                    try:
                        docs = cls.load_file(file_path)
                        all_docs.extend(docs)
                    except Exception as e:
                        print(f"加载文件失败 {file_path}: {e}")
        
        return all_docs