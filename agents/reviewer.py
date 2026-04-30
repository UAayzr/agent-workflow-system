from typing import List, Dict, Any
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import JsonOutputParser

class ReviewerAgent:
    def __init__(self, model_name: str = "gpt-4o"):
        self.llm = ChatOpenAI(model_name=model_name, temperature=0.1)
    
    def review(self, task: str, result: Dict[str, Any]) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
你是一个结果审核专家，负责评估任务执行结果的质量。

请按照以下标准评估：
1. 结果是否准确回答了问题/完成了任务
2. 结果是否完整，没有遗漏重要信息
3. 结果是否清晰易懂
4. 结果是否符合预期格式

输出格式：
{{
  "quality_score": 0-100,
  "issues": ["问题1", "问题2"],
  "suggestions": ["建议1", "建议2"],
  "needs_retry": true/false,
  "revised_task": "如果需要重试，请提供修正后的任务描述"
}}
            """.strip()),
            ("human", "任务：{task}\n\n执行结果：{result}")
        ])
        
        chain = prompt | self.llm
        
        response = chain.invoke({
            "task": task,
            "result": str(result)
        })
        
        try:
            parser = JsonOutputParser()
            review = parser.parse(response.content)
        except:
            review = {
                "quality_score": 50,
                "issues": ["无法解析结果"],
                "suggestions": ["重新执行任务"],
                "needs_retry": True,
                "revised_task": task
            }
        
        return review