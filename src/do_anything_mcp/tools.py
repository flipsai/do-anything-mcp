import json
import logging
import sys
import os
from mcp.server.fastmcp import Context

# Configure logging
logger = logging.getLogger("DoAnythingMCPTools")

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import connection functionality using absolute imports
from src.do_anything_mcp.connection import get_do_anything_connection

def register_tools(mcp):
    """Register all MCP tools with the FastMCP instance"""
    
    @mcp.tool()
    def echo_message(ctx: Context, message: str = "Hello!") -> str:
        """
        Echo a message back to the user
        
        Args:
            message: The message to echo back
        """
        try:
            connection = get_do_anything_connection()
            result = connection.execute_command("echo", {"message": message})
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    def get_system_info(ctx: Context) -> str:
        """
        Get information about the system
        """
        try:
            connection = get_do_anything_connection()
            result = connection.execute_command("system_info")
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    def execute_python_code(ctx: Context, code: str) -> str:
        """
        Execute arbitrary Python code
        
        Args:
            code: The Python code to execute
        """
        try:
            # This is just a placeholder - in a real implementation,
            # you would need to add security considerations
            import ast
            
            # Try to parse the code to catch syntax errors
            ast.parse(code)
            
            # Execute in a safe environment
            result = {"output": "Code execution is not implemented for security reasons"}
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"
            
    # Additional tools can be added here
    
    @mcp.prompt()
    def general_strategy() -> str:
        """Prompt to help Claude understand how to use the Do Anything MCP"""
        return """
        You have access to a flexible Model Context Protocol (MCP) server designed to handle
        various tasks through a clean API.
        
        To work with the Do Anything MCP, you can use the following general approach:
        
        1. Get system information with `get_system_info()`
        2. Echo messages with `echo_message(message="Your message")`
        3. Execute Python code with `execute_python_code(code="your_code_here")`
           (Note that code execution has safety limitations)
        
        Additional capabilities can be added as needed for specific use cases.
        """ 