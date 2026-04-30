from typing import List, Dict, Any, Optional
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import JsonOutputParser
from tools import ToolRegistry, ToolResult

class ExecutorAgent:
    def __init__(self, model_name: str = "gpt-4o"):
        self.llm = ChatOpenAI(model_name=model_name, temperature=0.2)
    
    def execute_task(self, task: str, context: str = "") -> Dict[str, Any]:
        tool_descriptions = ToolRegistry.get_tool_descriptions()
        
        tools_desc = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in tool_descriptions
        ])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
你是一个任务执行专家，负责执行具体的子任务。

可用工具：
{tools}

请分析任务需求，选择合适的工具执行。

输出格式：
{{
  "tool_name": "<工具名称>",
  "args": {{<参数键值对>}},
  "reason": "<选择此工具的原因>"
}}

如果不需要工具，直接输出结果：
{{
  "tool_name": "none",
  "args": {{}},
  "result": "<直接返回的结果>"
}}
            """.strip()),
            ("human", "上下文：{context}\n\n任务：{task}")
        ])
        
        chain = prompt | self.llm
        
        response = chain.invoke({
            "task": task,
            "context": context,
            "tools": tools_desc
        })
        
        try:
            parser = JsonOutputParser()
            result = parser.parse(response.content)
        except:
            result = {"tool_name": "none", "args": {}, "result": response.content}
        
        if result["tool_name"] != "none":
            tool_class = ToolRegistry.get_tool(result["tool_name"])
            if tool_class:
                tool_instance = tool_class()
                tool_result = tool_instance.execute(**result["args"])
                return {
                    "task": task,
                    "tool_used": result["tool_name"],
                    "reason": result.get("reason", ""),
                    "success": tool_result.success,
                    "result": tool_result.content,
                    "error": tool_result.error
                }
        
        return {
            "task": task,
            "tool_used": result["tool_name"],
            "reason": result.get("reason", ""),
            "success": True,
            "result": result.get("result", ""),
            "error": None
        }