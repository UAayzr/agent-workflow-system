from typing import List, Dict, Any, Optional
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import hashlib

class ContextManager:
    def __init__(self, max_context_size: int = 4000, compression_threshold: int = 2000):
        self.max_context_size = max_context_size
        self.compression_threshold = compression_threshold
        self.llm = ChatOpenAI(model_name="gpt-4o", temperature=0.1)
        self.conversations: Dict[str, List[Dict[str, str]]] = {}
    
    def _hash_session_id(self, session_id: str) -> str:
        return hashlib.md5(session_id.encode()).hexdigest()
    
    def add_message(self, session_id: str, role: str, content: str) -> None:
        session_hash = self._hash_session_id(session_id)
        
        if session_hash not in self.conversations:
            self.conversations[session_hash] = []
        
        self.conversations[session_hash].append({
            "role": role,
            "content": content
        })
        
        self._compress_context(session_hash)
    
    def get_context(self, session_id: str) -> List[Dict[str, str]]:
        session_hash = self._hash_session_id(session_id)
        return self.conversations.get(session_hash, [])
    
    def get_context_text(self, session_id: str) -> str:
        messages = self.get_context(session_id)
        return "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    
    def _compress_context(self, session_hash: str) -> None:
        messages = self.conversations.get(session_hash, [])
        if not messages:
            return
        
        total_tokens = sum(len(m["content"]) for m in messages)
        
        if total_tokens > self.compression_threshold:
            summary = self._summarize_context(messages)
            
            self.conversations[session_hash] = [
                {"role": "system", "content": f"之前对话摘要：{summary}"},
                messages[-1]
            ] if messages else []
    
    def _summarize_context(self, messages: List[Dict[str, str]]) -> str:
        messages_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages[:-1]])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "请将以下对话内容进行精简总结，保留关键信息和上下文。"),
            ("human", messages_text)
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({})
        
        return response.content
    
    def clear_context(self, session_id: str) -> None:
        session_hash = self._hash_session_id(session_id)
        if session_hash in self.conversations:
            del self.conversations[session_hash]
    
    def get_context_size(self, session_id: str) -> int:
        session_hash = self._hash_session_id(session_id)
        messages = self.conversations.get(session_hash, [])
        return sum(len(m["content"]) for m in messages)