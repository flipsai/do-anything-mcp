import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional
import os
import sys

# Configure logging
logger = logging.getLogger("DoAnythingConnection")

@dataclass
class DoAnythingConnection:
    """Connection for the Do Anything MCP"""
    
    def connect(self) -> bool:
        """Connect to underlying services if needed"""
        try:
            logger.info("Connected to Do Anything MCP services")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to services: {str(e)}")
            return False
    
    def execute_command(self, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a command"""
        if params is None:
            params = {}
            
        try:
            logger.info(f"Executing command: {command_type} with params: {params}")
            
            # Import commands module directly without relative imports
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from src.do_anything_mcp.commands import execute_command
            return execute_command(self, command_type, params)
            
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            raise Exception(f"Error executing command {command_type}: {str(e)}")

# Global connection instance
do_anything_connection = None

def get_do_anything_connection():
    """Get or create the connection"""
    global do_anything_connection
    
    if not do_anything_connection:
        do_anything_connection = DoAnythingConnection()
        do_anything_connection.connect()
    
    return do_anything_connection 