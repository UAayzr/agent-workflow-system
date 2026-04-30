from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router
from utils import Config

app = FastAPI(
    title="Agent Workflow System",
    description="基于多 Agent 架构的 AI 自动化工作流系统",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=Config.APP_HOST,
        port=Config.APP_PORT,
        reload=True
    )