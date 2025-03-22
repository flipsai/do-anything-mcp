import logging
import os
from typing import Dict, Any

# Configure logging
logger = logging.getLogger("DoAnythingCommands")

# Import the FLUX Schnell command
from .flux_schnell import flux_schnell_command

def execute_command(connection, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Execute a command using the Do Anything MCP system"""
    if params is None:
        params = {}
        
    # Execute different commands based on the command_type
    if command_type == "echo":
        result = {"message": params.get("message", "Hello from Do Anything MCP!")}
    elif command_type == "system_info":
        import platform
        result = {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "machine": platform.machine(),
            "working_directory": os.environ.get("MCP_WORK_DIR", os.getcwd())
        }
    elif command_type == "flux_generate_image":
        # Call the FLUX.1-schnell image generation
        result = flux_schnell_command.generate_image(params)
    elif command_type == "flux_get_image":
        # Get a base64 encoded image
        image_path = params.get("image_path")
        if not image_path:
            result = {"success": False, "message": "Image path is required"}
        else:
            # Load the image directly using PIL to ensure proper format
            from PIL import Image as PILImage
            import io
            import base64
            
            try:
                # Open the image with PIL
                pil_image = PILImage.open(image_path)
                
                # Convert to bytes
                img_byte_arr = io.BytesIO()
                pil_image.save(img_byte_arr, format='PNG')
                img_bytes = img_byte_arr.getvalue()
                # Encode to base64 (backwards compatibility)
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                
                result = {
                    "success": True,
                    "image_data": base64_image,
                    "message": "Image encoded successfully",
                    "format": "png"
                }
                
            except Exception as e:
                logger.error(f"Error processing image: {str(e)}")
                result = {"success": False, "message": f"Failed to process image: {str(e)}"}
    else:
        raise Exception(f"Command not implemented: {command_type}")
            
    return result
