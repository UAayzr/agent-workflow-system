import os
from typing import Dict, List
from serpapi import GoogleSearch
from .base import BaseTool, ToolResult, ToolRegistry

@ToolRegistry.register
class WebSearchTool(BaseTool):
    name = "web_search"
    description = "使用网络搜索获取最新信息，适用于需要实时数据或最新资讯的任务"
    args = [
        {"name": "query", "type": "string", "description": "搜索查询词"}
    ]
    
    def execute(self, query: str) -> ToolResult:
        try:
            api_key = os.getenv("SERPAPI_API_KEY")
            if not api_key:
                return ToolResult(
                    success=False,
                    content="",
                    error="未配置 SERPAPI_API_KEY 环境变量"
                )
            
            search = GoogleSearch({
                "q": query,
                "api_key": api_key,
                "num": 5
            })
            
            results = search.get_dict()
            organic_results = results.get("organic_results", [])
            
            formatted_results = []
            for i, result in enumerate(organic_results[:5], 1):
                title = result.get("title", "")
                link = result.get("link", "")
                snippet = result.get("snippet", "")
                formatted_results.append(f"{i}. [{title}]({link})\n{snippet}")
            
            return ToolResult(
                success=True,
                content="\n\n".join(formatted_results)
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=f"搜索失败: {str(e)}"
            )