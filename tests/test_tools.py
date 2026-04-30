import pytest
from tools import ToolRegistry, WebSearchTool, PythonCodeExecutor, FileReaderTool, FileWriterTool

class TestToolRegistry:
    def test_register_tool(self):
        tools_before = ToolRegistry.list_tools()
        assert "python_executor" in tools_before
        assert "web_search" in tools_before
        assert "file_reader" in tools_before
        assert "file_writer" in tools_before
    
    def test_get_tool(self):
        tool_class = ToolRegistry.get_tool("python_executor")
        assert tool_class is not None
        assert tool_class.name == "python_executor"
    
    def test_list_tools(self):
        tools = ToolRegistry.list_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0

class TestPythonCodeExecutor:
    def test_execute_safe_code(self):
        executor = PythonCodeExecutor()
        result = executor.execute("print(2 + 3)")
        assert result.success
        assert "5" in result.content
    
    def test_execute_dangerous_code(self):
        executor = PythonCodeExecutor()
        result = executor.execute("import os; os.system('rm -rf /')")
        assert not result.success
        assert "危险操作" in result.error

class TestFileTools:
    def test_file_writer_and_reader(self, tmp_path):
        file_path = tmp_path / "test.txt"
        writer = FileWriterTool()
        result = writer.execute(str(file_path), "Hello, World!")
        assert result.success
        
        reader = FileReaderTool()
        read_result = reader.execute(str(file_path))
        assert read_result.success
        assert read_result.content == "Hello, World!"