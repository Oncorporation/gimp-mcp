# GIMP-MCP

GIMP-MCP is a system designed to enable external control of GIMP (GNU Image Manipulation Program) using a Model Control Protocol (MCP). This project allows you to automate image manipulation tasks in GIMP programmatically, making it ideal for integrating GIMP into automated workflows, batch processing, or advanced design systems.

## Components

The system consists of two components:

1. **GIMP Plugin (`mcp_server_plugin.py`)**: A Python plugin that runs inside GIMP and starts a socket server to listen for commands.
2. **External Client Script (`gimp_mcp_client.py`)**: A standalone Python script that connects to the GIMP plugin's server and sends commands to manipulate images.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [GIMP Plugin Installation](#gimp-plugin-installation)
  - [External Client Script](#external-client-script)
- [Usage](#usage)
  - [Starting the GIMP Plugin](#starting-the-gimp-plugin)
  - [Running the External Client Script](#running-the-external-client-script)
  - [Sending Commands](#sending-commands)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

Before you begin, ensure you have the following installed:

- **GIMP 2.10** or later with Python support enabled (GIMP-Python is required).
- **Python 3.x** installed on your system.
- Basic familiarity with running Python scripts and using GIMP.

The external script uses standard Python libraries (`socket` and `json`), so no additional dependencies are required beyond Python itself.

## Installation

### GIMP Plugin Installation

The GIMP plugin (`mcp_server_plugin.py`) must be installed in GIMP's plugin directory.

1. **Locate the GIMP Plugin Directory**:
   - **Linux**: `~/.config/GIMP/2.10/plug-ins/`
   - **Windows**: `C:\Users\<username>\AppData\Roaming\GIMP\2.10\plug-ins\`
   - **macOS**: `~/Library/Application Support/GIMP/2.10/plug-ins/`

2. **Copy the Plugin File**:
   - Place `mcp_server_plugin.py` into the GIMP plugin directory.

3. **Make the Plugin Executable (Linux/macOS only)**:
   ```bash
   chmod +x ~/.config/GIMP/2.10/plug-ins/mcp_server_plugin.py