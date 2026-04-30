import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

class TestAPI:
    def test_health_check(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_list_tools(self):
        response = client.get("/api/tools")
        assert response.status_code == 200
        assert "tools" in response.json()
    
    def test_execute_workflow(self):
        response = client.post(
            "/api/workflow/execute",
            json={"task": "计算 2+2"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert "status" in data
    
    def test_search_knowledge(self):
        response = client.post(
            "/api/knowledge/search",
            json={"query": "test", "k": 2}
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data