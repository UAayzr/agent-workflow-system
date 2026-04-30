from typing import List, Dict, Any
from .planner import PlannerAgent, TaskPlan
from .executor import ExecutorAgent
from .reviewer import ReviewerAgent
from tools import ToolRegistry

class WorkflowCoordinator:
    def __init__(self):
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.reviewer = ReviewerAgent()
    
    def execute_workflow(self, task: str, max_retries: int = 2) -> Dict[str, Any]:
        tool_descriptions = ToolRegistry.get_tool_descriptions()
        
        plan = self.planner.create_plan(task, tool_descriptions)
        
        results = []
        executed_tasks = set()
        
        for attempt in range(max_retries + 1):
            for sub_task in plan.tasks:
                if sub_task.id in executed_tasks:
                    continue
                
                dependencies_met = all(
                    dep in executed_tasks 
                    for dep in sub_task.dependencies
                )
                
                if not dependencies_met:
                    continue
                
                context = "\n".join([
                    f"{r['task']}: {r['result'][:200]}..." 
                    for r in results 
                    if len(r.get('result', '')) > 0
                ])
                
                execution_result = self.executor.execute_task(sub_task.description, context)
                results.append(execution_result)
                
                if execution_result["success"]:
                    review = self.reviewer.review(sub_task.description, execution_result)
                    execution_result["review"] = review
                    
                    if review["needs_retry"] and attempt < max_retries:
                        continue
                    
                    executed_tasks.add(sub_task.id)
                else:
                    executed_tasks.add(sub_task.id)
            
            if len(executed_tasks) == len(plan.tasks):
                break
        
        return {
            "plan": plan.dict() if hasattr(plan, 'dict') else plan,
            "results": results,
            "summary": plan.summary
        }