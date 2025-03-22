import json
import logging
import sys
import os
import base64
from mcp.server.fastmcp import Context
from mcp.server.fastmcp import Image
from io import BytesIO
from PIL import Image as PILImage

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
    ) -> Image:
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
                raise Exception(f"Error generating image: {result.get('message', 'Unknown error')}")
                
            # Get the image path
            image_path = result.get("image_path")
            
            # Read the image data
            image_result = connection.execute_command("flux_get_image", {"image_path": image_path})
            
            if not image_result.get("success", False):
                raise Exception(f"Error retrieving image: {image_result.get('message', 'Unknown error')}")
                
            # Get the binary image data from the result
            base64_data = image_result.get("image_data", "")
            
            # Resize the image if it's too large
            # The max response size is around 1MB, and base64 encoding adds ~33% overhead
            # So we should aim for an image that's around 750KB when base64 encoded
            if len(base64_data) > 750000:
                # Decode the base64 data
                image_bytes = base64.b64decode(base64_data)
                img = PILImage.open(BytesIO(image_bytes))
                
                # Calculate the resize factor needed
                # We aim for ~750KB after base64 encoding
                current_size = len(base64_data)
                resize_factor = (750000 / current_size) ** 0.5  # Square root for 2D scaling
                
                # Resize the image
                new_width = int(img.width * resize_factor)
                new_height = int(img.height * resize_factor)
                img = img.resize((new_width, new_height), PILImage.LANCZOS)
                
                # Convert back to base64
                buffer = BytesIO()
                img.save(buffer, format="PNG", optimize=True)
                base64_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
            
            # Create an Image object as expected by the MCP framework
            # Convert base64 string to bytes for the data parameter
            image_data = base64.b64decode(base64_data)
            return Image(data=image_data, format="png")
            
        except Exception as e:
            logger.error(f"Error in FLUX_1_schnell_infer: {str(e)}")
            # Create a TextContent object for the error
            from mcp.types import TextContent
            return TextContent(type="text", text=f"Error generating image: {str(e)}")
            
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
