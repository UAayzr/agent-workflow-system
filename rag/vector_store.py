import os
from typing import List, Optional, Any, Dict
from langchain.vectorstores import FAISS, Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

class VectorStoreManager:
    def __init__(self, db_type: str = "faiss", db_path: str = "./data/vector_db"):
        self.db_type = db_type
        self.db_path = db_path
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None
        self._init_store()
    
    def _init_store(self):
        os.makedirs(self.db_path, exist_ok=True)
        
        if self.db_type == "faiss":
            if os.path.exists(os.path.join(self.db_path, "index.faiss")):
                self.vector_store = FAISS.load_local(
                    self.db_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            else:
                self.vector_store = FAISS.from_texts([""], self.embeddings)
                self.vector_store.save_local(self.db_path)
        elif self.db_type == "chroma":
            self.vector_store = Chroma(
                persist_directory=self.db_path,
                embedding_function=self.embeddings
            )
        else:
            raise ValueError(f"不支持的向量数据库类型: {self.db_type}")
    
    def add_documents(self, documents: List[Document]) -> None:
        if not documents:
            return
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len
        )
        
        split_docs = text_splitter.split_documents(documents)
        
        if self.db_type == "faiss":
            self.vector_store.add_documents(split_docs)
            self.vector_store.save_local(self.db_path)
        elif self.db_type == "chroma":
            self.vector_store.add_documents(split_docs)
            self.vector_store.persist()
    
    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        documents = []
        for i, text in enumerate(texts):
            metadata = metadatas[i] if metadatas else {}
            documents.append(Document(page_content=text, metadata=metadata))
        self.add_documents(documents)
    
    def search(self, query: str, k: int = 4) -> List[Document]:
        if not self.vector_store:
            return []
        
        results = self.vector_store.similarity_search(query, k=k)
        return results
    
    def get_relevant_context(self, query: str, k: int = 4) -> str:
        results = self.search(query, k=k)
        context = "\n\n".join([doc.page_content for doc in results])
        return context
    
    def delete_all(self) -> None:
        if self.db_type == "faiss":
            self.vector_store = FAISS.from_texts([""], self.embeddings)
            self.vector_store.save_local(self.db_path)
        elif self.db_type == "chroma":
            self.vector_store.delete_collection()
            self._init_store()
    
    def get_document_count(self) -> int:
        if self.db_type == "faiss":
            return len(self.vector_store.index_to_docstore_id)
        elif self.db_type == "chroma":
            return self.vector_store._collection.count()
        return 0