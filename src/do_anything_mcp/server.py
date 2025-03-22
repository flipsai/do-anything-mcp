"""Do Anything MCP Server

This module provides a Model Context Protocol (MCP) server that exposes
functionality through a clean API.
"""
import logging
import sys
import os
import argparse
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DoAnythingMCPServer")

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import connection management using absolute imports
from src.do_anything_mcp.connection import (
    get_do_anything_connection,
    do_anything_connection
)

# Import tools registration
from src.do_anything_mcp.tools import register_tools

@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage the lifecycle of the MCP server"""
    
    # Initialize connection
    logger.info("Initializing Do Anything MCP connection")
    
    if not get_do_anything_connection().connect():
        logger.error("Failed to initialize connection")
        raise ConnectionError("Could not initialize the MCP connection")
    
    # Ensure working directory exists
    work_dir = os.environ.get("MCP_WORK_DIR", os.path.join(os.getcwd(), "mcp_data"))
    os.makedirs(work_dir, exist_ok=True)
    logger.info(f"Using working directory: {work_dir}")
    
    logger.info("Do Anything MCP Server started successfully")
    
    yield {"status": "running", "message": "Do Anything MCP Server is running"}
    
    # Cleanup on shutdown
    logger.info("Shutting down Do Anything MCP Server")

# Get timeout from environment or use default (increased from default 10 seconds to 120 seconds)
DEFAULT_TIMEOUT = 120  # 2 minutes
timeout = int(os.environ.get("MCP_TIMEOUT", DEFAULT_TIMEOUT))

# Setup the MCP server with increased timeout
mcp = FastMCP(lifespan=server_lifespan, timeout=timeout)

# Register all tools
register_tools(mcp)

def main():
    """Run the MCP server"""
    parser = argparse.ArgumentParser(description="Do Anything MCP Server")
    parser.add_argument("--host", default="localhost", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=9877, help="Port to listen on")
    parser.add_argument("--work-dir", default=os.environ.get("MCP_WORK_DIR", os.path.join(os.getcwd(), "mcp_data")),
                        help="Working directory for file storage")
    parser.add_argument("--hf-token", default=os.environ.get("HF_TOKEN"),
                        help="Hugging Face token for accessing private spaces")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help=f"Timeout in seconds for tool operations (default: {DEFAULT_TIMEOUT})")
    
    args = parser.parse_args()
    
    # Set environment variables for other components to use
    os.environ["MCP_WORK_DIR"] = args.work_dir
    if args.hf_token:
        os.environ["HF_TOKEN"] = args.hf_token
    
    # Set timeout globally
    os.environ["MCP_TIMEOUT"] = str(args.timeout)
    global timeout
    timeout = args.timeout
    
    logger.info(f"Starting Do Anything MCP Server on {args.host}:{args.port}")
    logger.info(f"Using working directory: {args.work_dir}")
    logger.info(f"Tool operation timeout: {timeout} seconds")
    
    # Note: FastMCP.run() doesn't accept host/port arguments
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
