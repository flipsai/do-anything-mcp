import logging
from typing import Dict, Any

# Configure logging
logger = logging.getLogger("DoAnythingCommands")

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
            "machine": platform.machine()
        }
    else:
        raise Exception(f"Command not implemented: {command_type}")
            
    return result 