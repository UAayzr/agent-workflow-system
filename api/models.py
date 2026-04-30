from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class TaskRequest(BaseModel):
    task: str
    session_id: Optional[str] = None

class TaskResponse(BaseModel):
    task_id: str
    status: str
    plan: Optional[Dict[str, Any]] = None
    results: Optional[List[Dict[str, Any]]] = None
    summary: Optional[str] = None
    error: Optional[str] = None

class DocumentUploadRequest(BaseModel):
    file_path: str

class DocumentUploadResponse(BaseModel):
    success: bool
    message: str
    document_count: int

class KnowledgeSearchRequest(BaseModel):
    query: str
    k: int = 4

class KnowledgeSearchResponse(BaseModel):
    success: bool
    context: str
    sources: List[str]

class SessionContextResponse(BaseModel):
    session_id: str
    context_size: int
    messages: List[Dict[str, str]]