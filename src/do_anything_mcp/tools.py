import json
import logging
import sys
import os
import base64
from mcp.server.fastmcp import Context
from mcp.server.fastmcp import Image

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
    
    @mcp.tool()
    def FLUX_1_schnell_infer(
        ctx: Context, 
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        num_inference_steps: int = 4,
        seed: int = 0,
        randomize_seed: bool = True
    ):
        """
        Call the FLUX.1-schnell endpoint /infer to generate an image
        
        Args:
            prompt: The text prompt describing the image to generate
            width: Width of the generated image (default: 1024)
            height: Height of the generated image (default: 1024)
            num_inference_steps: Number of inference steps (default: 4)
            seed: Seed for generation (default: 0)
            randomize_seed: Whether to randomize the seed (default: True)
        """
        try:
            connection = get_do_anything_connection()
            result = connection.execute_command("flux_generate_image", {
                "prompt": prompt,
                "width": width,
                "height": height,
                "num_inference_steps": num_inference_steps,
                "seed": seed,
                "randomize_seed": randomize_seed
            })
            
            if not result.get("success", False):
                return {"error": f"Error generating image: {result.get('message', 'Unknown error')}"}
                
            # Get the image path
            image_path = result.get("image_path")
            
            # Read the image data
            image_result = connection.execute_command("flux_get_image", {"image_path": image_path})
            
            if not image_result.get("success", False):
                return {"error": f"Error retrieving image: {image_result.get('message', 'Unknown error')}"}
                
            # Get the binary image data from the result
            image_data = base64.b64decode(image_result.get("image_data", ""))
            
            # Create an Image object and return its image content
            image = Image(data=image_data)
            return image.to_image_content()
        except Exception as e:
            return {"error": f"Error: {str(e)}"}
            
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
        4. Generate images with `FLUX_1_schnell_infer(prompt="your image description")`
           Additional parameters:
           - width: Image width (default: 1024)
           - height: Image height (default: 1024)
           - num_inference_steps: Number of inference steps (default: 4)
           - seed: Random seed (default: 0)
           - randomize_seed: Whether to use random seed (default: True)
        
        Additional capabilities can be added as needed for specific use cases.
        """
