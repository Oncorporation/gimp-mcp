#!/usr/bin/env python3
# GIMP MCP Server Script
# Provides an MCP interface to control GIMP via a socket connection.

from mcp.server.fastmcp import FastMCP, Context
import socket
import json
import logging
import inspect

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GimpMCPServer")

class GimpConnection:
    def __init__(self, host='localhost', port=9877):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        if self.sock:
            return
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)
            self.sock.connect((self.host, self.port))
            logger.info(f"Connected to GIMP at {self.host}:{self.port}")
        except socket.timeout:
            logger.error(f"Connection to GIMP at {self.host}:{self.port} timed out.")
            self._close_socket()
            raise ConnectionError(f"Connection to GIMP timed out. Ensure the MCP Server plugin is running and responsive.")
        except socket.error as e:
            logger.error(f"Socket error connecting to GIMP at {self.host}:{self.port}: {e}")
            self._close_socket()
            raise ConnectionError(f"Could not connect to GIMP. Ensure the MCP Server plugin is running. Error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error connecting to GIMP: {e}")
            self._close_socket()
            raise ConnectionError(f"An unexpected error occurred while connecting to GIMP: {e}")

    def _close_socket(self):
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except (socket.error, OSError):
                pass
            finally:
                self.sock.close()
                self.sock = None
                logger.info("Socket closed.")

    def send_command(self, command_type, params=None):
        if not self.sock:
            try:
                self.connect()
            except ConnectionError:
                raise

        command = {"type": command_type, "params": params or {}}
        try:
            self.sock.sendall(json.dumps(command).encode('utf-8'))
            
            response_data = b""
            self.sock.settimeout(10)

            while True:
                try:
                    chunk = self.sock.recv(4096) # Increased buffer size
                    if not chunk: # Connection closed by GIMP plugin
                        break
                    response_data += chunk
                except socket.timeout:
                    logger.error("Timeout while receiving data from GIMP.")
                    raise Exception("Timeout receiving data from GIMP.")
                except socket.error as e:
                    logger.error(f"Socket error while receiving data: {e}")
                    raise Exception(f"Socket error receiving data from GIMP: {e}")
            
            if not response_data:
                logger.error("No response data received from GIMP (connection closed).")
                raise Exception("No response data from GIMP (connection closed).")

            try:
                return json.loads(response_data.decode('utf-8'))
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON response from GIMP: '{response_data.decode('utf-8', errors='ignore')}'. Error: {e}")
                raise Exception(f"Invalid JSON response from GIMP: {e}")

        except socket.error as e:
            logger.error(f"Socket error during send/recv: {e}")
            raise Exception(f"Socket error communicating with GIMP: {e}")
        except Exception as e:
            logger.error(f"Communication error: {e}")
            raise Exception(f"Error communicating with GIMP: {e}")
        finally:
            self._close_socket()

# Global connection
_gimp_connection = None

def get_gimp_connection():
    global _gimp_connection
    
    if _gimp_connection is None:
        _gimp_connection = GimpConnection()

    if _gimp_connection.sock is None:
        try:
            logger.info("Attempting to connect/reconnect to GIMP.")
            _gimp_connection.connect()
        except ConnectionError as e:
            logger.error(f"Failed to get GIMP connection: {e}")
            raise 
    
    return _gimp_connection

# MCP server
mcp = FastMCP("GimpMCP", description="GIMP integration through MCP")

@mcp.tool()
def call_api(ctx: Context, api_path: str, args: list = [], kwargs: dict = {}) -> str:
    """Call any GIMP 3.0 API method dynamically.

    Parameters:
    - api_path: The path to the API method (e.g., "Gimp.Image.get_by_id"). Available methods are
     comprehensively documented at https://developer.gimp.org/api/3.0/libgimp/
    - args: List of positional arguments
    - kwargs: Dictionary of keyword arguments

    Returns:
    - JSON string of the result or error message
    """
    try:
        conn = get_gimp_connection()
        result = conn.send_command("call_api", {"api_path": api_path, "args": args, "kwargs": kwargs})
        if result["status"] == "success":
            return json.dumps(result["result"])
        else:
            return f"Error: {json.dumps(result['error'])}"
    except Exception as e:
        return f"Error: {e}"

# Specific tools for common operations
@mcp.tool()
def get_images(ctx: Context) -> str:
    """List all open images in GIMP.

    Returns:
    - JSON string of image IDs and names
    """
    return call_api(ctx, "Gimp.get_images")

@mcp.tool()
def get_image_info(ctx: Context, image_id: int) -> str:
    """Get information about a specific image.

    Parameters:
    - image_id: The ID of the image

    Returns:
    - JSON string of image details
    """
    image = call_api(ctx, "Gimp.Image.get_by_id", args=[image_id])
    if "Error" in image:
        return image
    image_obj = json.loads(image)
    info = {
        "width": call_api(ctx, "Gimp.Image.get_width", args=[image_obj["id"]]),
        "height": call_api(ctx, "Gimp.Image.get_height", args=[image_obj["id"]]),
        "layers": call_api(ctx, "Gimp.Image.get_layers", args=[image_obj["id"]])
    }
    return json.dumps(info)

@mcp.tool()
def apply_gaussian_blur(ctx: Context, image_id: int, radius: float = 5.0) -> str:
    """Apply Gaussian blur to an image.

    Parameters:
    - image_id: The ID of the image
    - radius: Blur radius

    Returns:
    - Success message or error
    """
    image = call_api(ctx, "Gimp.Image.get_by_id", args=[image_id])
    if "Error" in image:
        return image
    image_obj = json.loads(image)
    drawable = call_api(ctx, "Gimp.Image.get_active_layer", args=[image_obj["id"]])
    if "Error" in drawable:
        return drawable
    drawable_obj = json.loads(drawable)
    result = call_api(ctx, "Gimp.get_pdb.run_procedure", 
                     args=["plug-in-gauss", image_obj["id"], drawable_obj["id"], radius, radius, 0])
    if "Error" in result:
        return result
    call_api(ctx, "Gimp.displays_flush")
    return "Applied Gaussian blur successfully"

@mcp.tool(name="describe_tools", description="Provides a description of all available tools in OpenAPI 3.0.x JSON format.")
def describe_server_tools(ctx: Context) -> str:
    """
    Describes all available tools in an OpenAPI (Swagger) 3.0.x JSON format.
    This allows clients to dynamically understand the server's capabilities.
    """
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": mcp.name,
            "version": "1.0.0", 
            "description": mcp.description
        },
        "paths": {}
    }

    for tool_name, tool_data in mcp.tools.items():
        tool_func = tool_data.func
        
        sig = inspect.signature(tool_func)
        docstring = inspect.getdoc(tool_func) or "No detailed description available."
        summary = docstring.splitlines()[0] if docstring else "No description"

        path_item = {
            "post": {
                "summary": summary,
                "description": docstring,
                "operationId": tool_name,
                "requestBody": None, 
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": _map_type_to_json_schema_type(sig.return_annotation)
                                }
                            }
                        }
                    },
                    "default": { 
                        "description": "Error response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        request_body_schema_props = {}
        required_params = []

        for param_name, param in sig.parameters.items():
            if param_name == "ctx": 
                continue

            param_schema = {
                "type": _map_type_to_json_schema_type(param.annotation),
                "description": f"Parameter: {param_name}"
            }
            if param.default != inspect.Parameter.empty:
                try:
                    json.dumps(param.default) 
                    param_schema["default"] = param.default
                except TypeError:
                    param_schema["default"] = str(param.default) 
            else:
                required_params.append(param_name)
            
            request_body_schema_props[param_name] = param_schema

        if request_body_schema_props:
            path_item["post"]["requestBody"] = {
                "required": bool(required_params),
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": request_body_schema_props,
                        }
                    }
                }
            }
            if required_params:
                path_item["post"]["requestBody"]["content"]["application/json"]["schema"]["required"] = required_params
        else:
            del path_item["post"]["requestBody"]

        openapi_spec["paths"][f"/{tool_name}"] = path_item
    
    try:
        return json.dumps(openapi_spec, indent=2)
    except TypeError as e:
        logger.error(f"Error serializing OpenAPI spec: {e}")
        return json.dumps({"error": "Failed to generate OpenAPI spec", "details": str(e)})

def _map_type_to_json_schema_type(py_type: type) -> str:
    """Maps Python type hints to JSON schema type strings."""
    if py_type == str:
        return "string"
    elif py_type == int:
        return "integer"
    elif py_type == float:
        return "number"
    elif py_type == bool:
        return "boolean"
    elif py_type == list or getattr(py_type, '__origin__', None) == list:
        return "array"
    elif py_type == dict or getattr(py_type, '__origin__', None) == dict:
        return "object"
    elif py_type == inspect.Parameter.empty or py_type is None:
        return "string"  # Default for missing annotation
    else:
        return "string" # Fallback for unhandled types

def main():
    mcp.run()

if __name__ == "__main__":
    main()