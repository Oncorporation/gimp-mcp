#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
from gi.repository import GLib
from gi.repository import Gio
import socket
import json
import sys
import traceback
import os
import threading
import inspect

def N_(message): return message
def _(message): return GLib.dgettext(None, message)

class MCPPlugin(Gimp.PlugIn):
    def __init__(self, host='localhost', port=9877):
        super().__init__()
        self.host = host
        self.port = port
        self.running = False
        self.socket = None
        self.server_thread = None

    def do_query_procedures(self):
        """Register the plugin procedure."""
        return ["plug-in-mcp-server"]

    def do_create_procedure(self, name):
        """Define the procedure properties."""
        procedure = Gimp.ImageProcedure.new(self, name, Gimp.PDBProcType.PLUGIN, self.run, None)
        procedure.set_menu_label(_("Start MCP Server"))
        procedure.set_documentation(_("Starts an MCP server to control GIMP externally"),
                                    _("Starts an MCP server to control GIMP externally"),
                                    name)
        procedure.set_attribution("Your Name", "Your Name", "2023")
        procedure.add_menu_path('<Image>/Filters/Development/')
        return procedure

    def run(self, procedure, run_mode, image, drawables, config, run_data):
        """Run the plugin and start the server."""
        if self.running:
            Gimp.message("MCP Server is already running")
            return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

        self.running = True

        try:
            Gimp.message("Creating socket...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)

            Gimp.message(f"GimpMCP server started on {self.host}:{self.port}")

            while self.running:
                client, address = self.socket.accept()
                print(f"Connected to client: {address}")

                # Handle client in a separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client,)
                )
                client_thread.daemon = True
                client_thread.start()

        except Exception as e:
            Gimp.message(f"Error starting server: {str(e)}")
            self.running = False

            if self.socket:
                self.socket.close()
                self.socket = None

            if self.server_thread:
                self.server_thread.join(timeout=1.0)
                self.server_thread = None

            return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

    def _handle_client(self, client):
        """Handle connected client"""
        Gimp.message("Client handler started")
        # client.settimeout(None)  # No timeout
        buffer = b''

        data = client.recv(4096)
        Gimp.message(f"Received data: {data}")
        # if not data:
        #     print("Client disconnected")
        #     break

        buffer += data
        request = json.loads(buffer.decode('utf-8'))
        buffer = b''
        Gimp.message(f"Parsed request: {request}")
        response = self.execute_command(request)
        Gimp.message(f"Generated response: {response}")
        response_data = json.dumps(response)
        client.sendall(response_data.encode('utf-8'))
        Gimp.message("Response sent successfully")
        client.close()
        Gimp.message("Client closed")
        return        

    def execute_command(self, request):
        """Execute commands in GIMP's main thread."""
        try:
            Gimp.message(f"Raw request: {request}")
            
            # Handle both old and new request formats
            params = request.get('params', {})
            api_path = params.get('api_path', '')
            args = params.get('args', [])
            kwargs = params.get('kwargs', {})
            
            # If params is empty, try the old format
            if not params:
                api_path = request.get('api_path', '')
                args = request.get('args', [])
                kwargs = request.get('kwargs', {})

            Gimp.message(f"Executing command: {api_path} with args {args} and kwargs {kwargs}")

            # Get Gimp.Image if kwargs specifies it
            image = None
            if kwargs.get('image_id'):
                image = Gimp.Image.get_by_id(kwargs.get('image_id'))
                del kwargs['image_id']

            # Dynamically resolve the API method
            current = Gimp
            for part in api_path.split('.')[1:]:  # Skip 'Gimp' as we already have it
                current = getattr(current, part)

            # Call the method
            if callable(current):
                sig = inspect.signature(current)
                if 'image' in sig.parameters:
                    args[0] = image
                result = current(*args, **kwargs)
            else:
                result = current

            # Serialize result
            if hasattr(result, "id"):  # For Gimp objects
                result = {"id": result.id}
            elif isinstance(result, list):
                result = [self.serialize_gimp_object(item) for item in result]
            else:
                result = str(result)

            Gimp.message(f"Command result: {result}")
            return {"status": "success", "result": result}

        except Exception as e:
            error_msg = f"Error executing command: {str(e)}\n{traceback.format_exc()}"
            Gimp.message(error_msg)
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    def serialize_gimp_object(self, obj):
        """Serialize Gimp objects to JSON-friendly formats."""
        Gimp.message(f"Serializing object: {obj}")
        if obj.__class__.__name__ == "Image":
            return {"id": Gimp.Image.get_id(obj), "type": obj.__class__.__name__}
        return str(obj)

Gimp.main(MCPPlugin.__gtype__, sys.argv)