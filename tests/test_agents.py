import pytest
from agents import PlannerAgent, ExecutorAgent, ReviewerAgent, WorkflowCoordinator

class TestPlannerAgent:
    def test_create_plan(self):
        planner = PlannerAgent()
        tool_descriptions = [
            {"name": "web_search", "description": "搜索网络信息"}
        ]
        
        plan = planner.create_plan("查找今天的天气", tool_descriptions)
        
        assert plan is not None
        assert isinstance(plan.tasks, list)
        assert len(plan.tasks) > 0

class TestExecutorAgent:
    def test_execute_task_without_tool(self):
        executor = ExecutorAgent()
        result = executor.execute_task("计算 2+2")
        
        assert result["success"]
        assert "4" in str(result["result"])

class TestReviewerAgent:
    def test_review_result(self):
        reviewer = ReviewerAgent()
        result = {
            "task": "测试任务",
            "success": True,
            "result": "测试结果"
        }
        
        review = reviewer.review("测试任务", result)
        
        assert review is not None
        assert "quality_score" in review
        assert "issues" in review
        assert "suggestions" in review