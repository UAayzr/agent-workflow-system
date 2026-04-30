from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type, Optional
from pydantic import BaseModel

class ToolResult(BaseModel):
    success: bool
    content: str
    error: Optional[str] = None

class BaseTool(ABC):
    name: str
    description: str
    args: List[Dict[str, str]]
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        pass

class ToolRegistry:
    _tools: Dict[str, Type[BaseTool]] = {}
    
    @classmethod
    def register(cls, tool_class: Type[BaseTool]) -> Type[BaseTool]:
        cls._tools[tool_class.name] = tool_class
        return tool_class
    
    @classmethod
    def get_tool(cls, name: str) -> Optional[Type[BaseTool]]:
        return cls._tools.get(name)
    
    @classmethod
    def list_tools(cls) -> List[str]:
        return list(cls._tools.keys())
    
    @classmethod
    def get_tool_descriptions(cls) -> List[Dict[str, Any]]:
        descriptions = []
        for name, tool_class in cls._tools.items():
            descriptions.append({
                "name": tool_class.name,
                "description": tool_class.description,
                "args": tool_class.args
            })
        return descriptions