from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import uuid
from .models import (
    TaskRequest,
    TaskResponse,
    DocumentUploadRequest,
    DocumentUploadResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    SessionContextResponse
)
from agents import WorkflowCoordinator
from rag import VectorStoreManager, DocumentLoader
from utils import ContextManager

router = APIRouter()

workflow_coordinator = WorkflowCoordinator()
vector_store = VectorStoreManager()
context_manager = ContextManager()

@router.post("/api/workflow/execute", response_model=TaskResponse)
async def execute_workflow(request: TaskRequest):
    try:
        task_id = str(uuid.uuid4())
        
        if not request.session_id:
            request.session_id = task_id
        
        context = context_manager.get_context_text(request.session_id)
        
        result = workflow_coordinator.execute_workflow(request.task)
        
        context_manager.add_message(request.session_id, "user", request.task)
        context_manager.add_message(request.session_id, "assistant", str(result.get("summary", "")))
        
        return TaskResponse(
            task_id=task_id,
            status="completed",
            plan=result.get("plan"),
            results=result.get("results"),
            summary=result.get("summary")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/workflow/{task_id}", response_model=TaskResponse)
async def get_workflow_status(task_id: str):
    try:
        context = context_manager.get_context(task_id)
        if not context:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return TaskResponse(
            task_id=task_id,
            status="completed",
            summary="任务已完成"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/knowledge/upload", response_model=DocumentUploadResponse)
async def upload_document(request: DocumentUploadRequest):
    try:
        documents = DocumentLoader.load_file(request.file_path)
        vector_store.add_documents(documents)
        
        return DocumentUploadResponse(
            success=True,
            message=f"成功上传 {len(documents)} 个文档",
            document_count=vector_store.get_document_count()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/knowledge/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(request: KnowledgeSearchRequest):
    try:
        context = vector_store.get_relevant_context(request.query, k=request.k)
        results = vector_store.search(request.query, k=request.k)
        sources = [doc.metadata.get('source', '') for doc in results]
        
        return KnowledgeSearchResponse(
            success=True,
            context=context,
            sources=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/knowledge/clear")
async def clear_knowledge():
    try:
        vector_store.delete_all()
        return {"success": True, "message": "知识库已清空"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/session/{session_id}", response_model=SessionContextResponse)
async def get_session_context(session_id: str):
    try:
        messages = context_manager.get_context(session_id)
        context_size = context_manager.get_context_size(session_id)
        
        return SessionContextResponse(
            session_id=session_id,
            context_size=context_size,
            messages=messages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    try:
        context_manager.clear_context(session_id)
        return {"success": True, "message": "会话已清空"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/tools")
async def list_tools():
    from tools import ToolRegistry
    return {"tools": ToolRegistry.get_tool_descriptions()}

@router.get("/api/health")
async def health_check():
    return {"status": "healthy"}