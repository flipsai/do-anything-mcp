"""
FLUX.1-schnell image generation command for Do Anything MCP.

This module provides integration with the FLUX.1-schnell text-to-image model
on Hugging Face Spaces.
"""

import os
import uuid
import base64
import logging
from typing import Dict, Any

import requests
from PIL import Image
from io import BytesIO

# Configure logging
logger = logging.getLogger("FluxSchnellCommand")

# Constants
DEFAULT_SPACE = "black-forest-labs/FLUX.1-schnell"
DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 1024
DEFAULT_INFERENCE_STEPS = 4

class FluxSchnellCommand:
    """Command handler for FLUX.1-schnell image generation"""
    
    def __init__(self, work_dir: str = None, hf_token: str = None):
        """Initialize the FLUX.1-schnell command handler.
        
        Args:
            work_dir: Directory to save generated images
            hf_token: Hugging Face token for accessing private spaces
        """
        self.work_dir = work_dir or os.path.join(os.getcwd(), "mcp_data")
        self.hf_token = hf_token
        
        # Create working directory if it doesn't exist
        os.makedirs(self.work_dir, exist_ok=True)
        
        # Configure Hugging Face client headers
        if self.hf_token:
            self.headers = {"Authorization": f"Bearer {self.hf_token}"}
            logger.info(f"Hugging Face token provided (length: {len(self.hf_token)})")
        else:
            self.headers = {}
            logger.warning("No Hugging Face token provided. API calls may fail for protected models.")
    
    def generate_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an image using FLUX.1-schnell.
        
        Args:
            params: Dictionary containing the generation parameters:
                - prompt: Text prompt for image generation
                - width: Image width (default: 1024)
                - height: Image height (default: 1024)
                - num_inference_steps: Number of diffusion steps (default: 4)
                - seed: Random seed (default: 0)
                - randomize_seed: Whether to randomize seed (default: True)
                
        Returns:
            Dictionary with generation results:
                - image_path: Path to saved image
                - success: Whether generation was successful
                - message: Status or error message
        """
        # Parse parameters
        prompt = params.get("prompt")
        if not prompt:
            return {"success": False, "message": "Prompt is required"}
        
        width = params.get("width", DEFAULT_WIDTH)
        height = params.get("height", DEFAULT_HEIGHT)
        num_inference_steps = params.get("num_inference_steps", DEFAULT_INFERENCE_STEPS)
        seed = params.get("seed", 0)
        randomize_seed = params.get("randomize_seed", True)
        
        # Validate parameters
        if not isinstance(width, int) or not isinstance(height, int):
            return {"success": False, "message": "Width and height must be integers"}
        
        # Define the API URL
        api_url = f"https://api-inference.huggingface.co/models/{DEFAULT_SPACE}"
        
        # Prepare the request payload
        payload = {
            "inputs": prompt,
            "parameters": {
                "width": width,
                "height": height,
                "num_inference_steps": num_inference_steps,
                "seed": seed if not randomize_seed else None
            }
        }
        
        # Remove None values from payload
        payload["parameters"] = {k: v for k, v in payload["parameters"].items() if v is not None}
        
        try:
            # Make the API request
            response = requests.post(api_url, headers=self.headers, json=payload)
            
            # Check for errors
            if response.status_code != 200:
                error_msg = f"API request failed with status {response.status_code}: {response.text}"
                
                if response.status_code == 401:
                    error_msg = "Authentication failed: Invalid or missing Hugging Face token. Please check your HF_TOKEN environment variable."
                    logger.error(f"HF Token authentication error. Token length: {len(self.hf_token) if self.hf_token else 0}")
                
                logger.error(error_msg)
                return {"success": False, "message": error_msg}
            
            # Generate a unique filename
            image_id = uuid.uuid4().hex
            image_filename = f"flux_image_{image_id}.png"
            image_path = os.path.join(self.work_dir, image_filename)
            
            # Save the image
            image = Image.open(BytesIO(response.content))
            image.save(image_path)
            
            # Return the result
            return {
                "success": True,
                "message": "Image generated successfully",
                "image_path": image_path,
                "image_id": image_id,
                "prompt": prompt,
                "width": width,
                "height": height
            }
            
        except Exception as e:
            error_msg = f"Error generating image: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
    
    def get_image_base64(self, image_path: str) -> str:
        """Get the base64 encoded content of an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image data
        """
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                return encoded_string
        except Exception as e:
            logger.error(f"Error encoding image: {str(e)}")
            return ""

# Create a singleton instance of the command
hf_token = os.environ.get("HF_TOKEN")
if not hf_token:
    logger.warning("HF_TOKEN environment variable not set. API calls may fail for protected models.")

flux_schnell_command = FluxSchnellCommand(
    work_dir=os.environ.get("MCP_WORK_DIR"),
    hf_token=hf_token
)
