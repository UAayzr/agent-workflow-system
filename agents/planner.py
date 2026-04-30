from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser

class SubTask(BaseModel):
    id: str
    description: str
    dependencies: List[str]
    tool: Optional[str] = None
    priority: int = 1

class TaskPlan(BaseModel):
    tasks: List[SubTask]
    summary: str

class PlannerAgent:
    def __init__(self, model_name: str = "gpt-4o"):
        self.llm = ChatOpenAI(model_name=model_name, temperature=0.1)
        self.output_parser = PydanticOutputParser(pydantic_object=TaskPlan)
    
    def create_plan(self, task: str, tool_descriptions: List[Dict[str, Any]]) -> TaskPlan:
        tools_desc = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in tool_descriptions
        ])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
你是一个任务规划专家，负责将复杂任务拆解为有序的子任务序列。

可用工具：
{tools}

请根据任务需求，输出结构化的任务计划，包含：
1. 子任务列表（每个子任务包含ID、描述、依赖关系、所需工具）
2. 任务摘要

确保任务之间有正确的依赖关系，高优先级任务优先执行。
            """.strip()),
            ("human", "{task}"),
            ("system", "请按照以下格式输出：\n{format_instructions}")
        ])
        
        chain = prompt | self.llm | self.output_parser
        
        result = chain.invoke({
            "task": task,
            "tools": tools_desc,
            "format_instructions": self.output_parser.get_format_instructions()
        })
        
        return result