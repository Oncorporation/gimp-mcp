GIMP-MCP README
GIMP-MCP is a system designed to enable external control of GIMP (GNU Image Manipulation Program) using a Model Control Protocol (MCP). This project allows you to automate image manipulation tasks in GIMP programmatically, making it ideal for integrating GIMP into automated workflows, batch processing, or advanced design systems.
The system consists of two components:
GIMP Plugin (mcp_server_plugin.py): A Python plugin that runs inside GIMP and starts a socket server to listen for commands.
External Client Script (gimp_mcp_client.py): A standalone Python script that connects to the GIMP plugin's server and sends commands to manipulate images.
Table of Contents
Prerequisites (#prerequisites)
Installation (#installation)
GIMP Plugin Installation (#gimp-plugin-installation)
External Client Script (#external-client-script)
Usage (#usage)
Starting the GIMP Plugin (#starting-the-gimp-plugin)
Running the External Client Script (#running-the-external-client-script)
Sending Commands (#sending-commands)
Examples (#examples)
Troubleshooting (#troubleshooting)
Contributing (#contributing)
License (#license)
Prerequisites
Before you begin, ensure you have the following installed:
GIMP 2.10 or later with Python support enabled (GIMP-Python is required).
Python 3.x installed on your system.
Basic familiarity with running Python scripts and using GIMP.
The external script uses standard Python libraries (socket and json), so no additional dependencies are required beyond Python itself.
Installation
GIMP Plugin Installation
The GIMP plugin (mcp_server_plugin.py) must be installed in GIMP's plugin directory to function.
Locate the GIMP Plugin Directory:
Linux: ~/.config/GIMP/2.10/plug-ins/
Windows: C:\Users\<username>\AppData\Roaming\GIMP\2.10\plug-ins\
macOS: ~/Library/Application Support/GIMP/2.10/plug-ins/
Copy the Plugin File:
Place mcp_server_plugin.py into the GIMP plugin directory.
Make the Plugin Executable (Linux/macOS only):
Open a terminal and run:
bash
chmod +x ~/.config/GIMP/2.10/plug-ins/mcp_server_plugin.py
Restart GIMP:
Close and reopen GIMP to register the plugin. You should see it appear under Filters > Development.
External Client Script
The external script (gimp_mcp_client.py) can be run from any location on your system.
Clone the Repository:
Download or clone the gimp-mcp repository:
bash
git clone https://github.com/yourusername/gimp-mcp.git
Navigate to the Repository Directory:
Move to the directory containing the script:
bash
cd gimp-mcp
Verify Python Installation:
Ensure Python 3 is installed by running:
bash
python3 --version
No additional dependencies are needed since the script relies on Python's built-in libraries.
Usage
Starting the GIMP Plugin
Open GIMP.
Launch the MCP Server:
Navigate to Filters > Development > Start MCP Server in the GIMP menu.
This starts a socket server on localhost:9876, which listens for commands from the external script.
Running the External Client Script
Ensure the GIMP Plugin is Running:
The MCP server must be active in GIMP before running the client script.
Execute the Script:
In a terminal, navigate to the repository directory and run:
bash
python3 gimp_mcp_client.py
The script connects to the GIMP plugin’s server and allows you to send commands.
Sending Commands
The external script communicates with GIMP by sending JSON-formatted commands over a socket connection. Below are some example commands you can send:
Load an Image:
json
{
  "command": "load_image",
  "file_path": "/path/to/image.png"
}
Loads an image into GIMP.
Apply a Gaussian Blur:
json
{
  "command": "apply_filter",
  "filter_name": "gaussian_blur",
  "params": {"radius": 5.0}
}
Applies a Gaussian blur with a specified radius.
Save an Image:
json
{
  "command": "save_image",
  "file_path": "/path/to/output.png"
}
Saves the current image to the specified path.
To stop the server, either close GIMP or (if implemented) send a shutdown command like:
json
{
  "command": "shutdown"
}
Examples
Here’s an example workflow to load an image, apply a filter, and save it using a custom Python script.
Example Script
Create a file (e.g., example.py) with the following content:
python
import json
import socket

def send_command(command):
    """Send a command to the GIMP MCP server and return the response."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 9876))
        s.sendall(json.dumps(command).encode('utf-8'))
        response = s.recv(1024)
        return json.loads(response.decode('utf-8'))

# Load an image
load_cmd = {"command": "load_image", "file_path": "/path/to/image.png"}
print("Loading image:", send_command(load_cmd))

# Apply Gaussian blur
blur_cmd = {"command": "apply_filter", "filter_name": "gaussian_blur", "params": {"radius": 5.0}}
print("Applying blur:", send_command(blur_cmd))

# Save the image
save_cmd = {"command": "save_image", "file_path": "/path/to/output.png"}
print("Saving image:", send_command(save_cmd))
Running the Example
Start the GIMP plugin (Filters > Development > Start MCP Server).
Run the script:
bash
python3 example.py
Check the output file (/path/to/output.png) to verify the result.
This script demonstrates a simple automation task, but you can extend it with more commands based on your needs.
Troubleshooting
Cannot Connect to Server:
Ensure the GIMP plugin is running and the server is started.
Verify the port (9876) is not blocked by a firewall or in use by another process.
Plugin Not Visible in GIMP:
Confirm the plugin file is in the correct directory and has executable permissions (Linux/macOS).
Restart GIMP after installation.
Command Fails:
Check the JSON syntax of your command.
Look for error messages in GIMP’s console or the script’s output.
Contributing
Contributions are welcome! To contribute:
Fork the repository.
Create a branch for your changes:
bash
git checkout -b feature/your-feature-name
Commit your changes with clear messages:
bash
git commit -m "Add feature X"
Push to your fork and submit a pull request.
Please adhere to Python coding standards and include comments where necessary.
License
This project is licensed under the MIT License. See the LICENSE file for details.
This Markdown-formatted README provides a comprehensive guide to setting up and using the gimp-mcp system. Replace placeholders like /path/to/image.png or yourusername with actual values specific to your setup as needed. Enjoy automating GIMP!
