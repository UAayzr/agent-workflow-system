import pytest
import tempfile
import os
from rag import VectorStoreManager, DocumentLoader
from langchain.schema import Document

class TestVectorStoreManager:
    def test_add_and_search(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = VectorStoreManager(db_type="faiss", db_path=tmp_dir)
            
            store.add_texts(["Hello, World!", "This is a test"])
            
            results = store.search("Hello")
            assert len(results) > 0
            assert "Hello" in results[0].page_content
    
    def test_get_relevant_context(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = VectorStoreManager(db_type="faiss", db_path=tmp_dir)
            
            store.add_texts(["Artificial Intelligence is the simulation of human intelligence processes.", "Machine learning is a subset of AI."])
            
            context = store.get_relevant_context("What is AI?")
            assert "Artificial Intelligence" in context
    
    def test_delete_all(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = VectorStoreManager(db_type="faiss", db_path=tmp_dir)
            
            store.add_texts(["Test content"])
            assert store.get_document_count() > 0
            
            store.delete_all()
            assert store.get_document_count() == 0

class TestDocumentLoader:
    def test_load_txt_file(self, tmp_path):
        file_path = tmp_path / "test.txt"
        file_path.write_text("Test content")
        
        docs = DocumentLoader.load_file(str(file_path))
        assert len(docs) == 1
        assert docs[0].page_content == "Test content"
    
    def test_load_markdown_file(self, tmp_path):
        file_path = tmp_path / "test.md"
        file_path.write_text("# Title\n\nContent")
        
        docs = DocumentLoader.load_file(str(file_path))
        assert len(docs) == 1
        assert "Title" in docs[0].page_content