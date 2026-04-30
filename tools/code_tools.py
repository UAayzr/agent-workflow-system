import subprocess
import sys
import tempfile
import os
from typing import Dict
from .base import BaseTool, ToolResult, ToolRegistry

@ToolRegistry.register
class PythonCodeExecutor(BaseTool):
    name = "python_executor"
    description = "执行 Python 代码并返回结果，仅支持安全的代码执行，不支持文件系统操作"
    args = [
        {"name": "code", "type": "string", "description": "要执行的 Python 代码"}
    ]
    
    _DANGEROUS_FUNCTIONS = {
        'os', 'subprocess', 'sys', 'shutil', 'eval', 'exec', 
        '__import__', 'open', 'file', 'compile'
    }
    
    def _is_safe_code(self, code: str) -> bool:
        for dangerous in self._DANGEROUS_FUNCTIONS:
            if dangerous in code:
                return False
        return True
    
    def execute(self, code: str) -> ToolResult:
        try:
            if not self._is_safe_code(code):
                return ToolResult(
                    success=False,
                    content="",
                    error="代码包含危险操作，拒绝执行"
                )
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            os.unlink(temp_file)
            
            if result.returncode != 0:
                return ToolResult(
                    success=False,
                    content="",
                    error=f"执行错误: {result.stderr}"
                )
            
            return ToolResult(
                success=True,
                content=result.stdout
            )
        
        except subprocess.TimeoutExpired:
            os.unlink(temp_file)
            return ToolResult(
                success=False,
                content="",
                error="代码执行超时"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=f"执行失败: {str(e)}"
            )