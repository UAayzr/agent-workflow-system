import os
from typing import Dict
from .base import BaseTool, ToolResult, ToolRegistry

@ToolRegistry.register
class FileReaderTool(BaseTool):
    name = "file_reader"
    description = "读取指定文件的内容"
    args = [
        {"name": "file_path", "type": "string", "description": "文件路径"}
    ]
    
    def execute(self, file_path: str) -> ToolResult:
        try:
            if not os.path.exists(file_path):
                return ToolResult(
                    success=False,
                    content="",
                    error=f"文件不存在: {file_path}"
                )
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return ToolResult(
                success=True,
                content=content
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=f"读取文件失败: {str(e)}"
            )

@ToolRegistry.register
class FileWriterTool(BaseTool):
    name = "file_writer"
    description = "将内容写入指定文件"
    args = [
        {"name": "file_path", "type": "string", "description": "文件路径"},
        {"name": "content", "type": "string", "description": "要写入的内容"},
        {"name": "append", "type": "boolean", "description": "是否追加模式，默认为False"}
    ]
    
    def execute(self, file_path: str, content: str, append: bool = False) -> ToolResult:
        try:
            mode = 'a' if append else 'w'
            
            with open(file_path, mode, encoding='utf-8') as f:
                f.write(content)
            
            return ToolResult(
                success=True,
                content=f"文件已成功{'追加' if append else '写入'}: {file_path}"
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=f"写入文件失败: {str(e)}"
            )