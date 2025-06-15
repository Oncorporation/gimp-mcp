# GIMP-MCP: Integrating GIMP with AI through Model Context Protocol

**GIMP-MCP** is an initiative to integrate the **Model Context Protocol (MCP)** into the GNU Image Manipulation Program (GIMP), enabling seamless interaction between GIMP and AI models. This integration allows users to harness advanced AI capabilities directly within GIMP, enhancing image editing workflows with intelligent automation and context-aware operations.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Installing the GIMP-MCP Plugin](#installing-the-gimp-mcp-plugin)
- [Client Interaction](#client-interaction)
- [Usage Examples](#usage-examples)
  - [AI-Powered Background Removal](#ai-powered-background-removal)
  - [Image Inpainting with AI](#image-inpainting-with-ai)
- [Human-AI Interaction Prompts](#human-ai-interaction-prompts)
- [Available API Commands](#available-api-commands)
- [Additional Resources](#additional-resources)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Introduction

The **Model Context Protocol (MCP)** is an open standard developed to facilitate seamless integration between AI systems and external applications. By implementing MCP within GIMP, users can leverage AI models for tasks such as object recognition, style transfer, and automated enhancements, thereby extending GIMP's native functionalities.

## Features

- **AI Integration**: Connect GIMP with state-of-the-art AI models for enhanced image processing capabilities.
- **Automated Workflows**: Utilize AI to perform repetitive tasks, allowing for more efficient editing processes.
- **Context-Aware Operations**: AI models can interpret and manipulate images based on contextual understanding, leading to more intelligent edits.

## Installation

### Prerequisites

Before installing the GIMP-MCP plugin, ensure you have the following:

- **GIMP 3.0** or later installed on your system.
- **Python 3.x** installed.
- **PyGObject**: This is required for the `gi` bindings used by GIMP Python plugins. Installation varies by OS:
    - Linux: Often available via system package manager (e.g., `sudo apt install python3-gi`).
    - Windows/macOS: May require specific installers or `pip install PyGObject` if build tools are configured. Refer to [PyGObject documentation](https://pygobject.readthedocs.io/en/latest/getting_started.html).
- Basic knowledge of Python scripting and GIMP's plugin architecture.

### Installing the GIMP-MCP Plugin

The GIMP-MCP plugin (`gimp-mcp-plugin.py`) integrates GIMP with MCP and starts a server instance when activated within GIMP.

1.  **Clone the GIMP-MCP Repository**:```bash
git clone https://github.com/oncorporation/gimp-mcp.git
cd gimp-mcp
```    (Note: The `gimp-mcp-plugin.py` file should be in the root of this repository).

2.  **Locate GIMP’s Plugin Directory**:
    *   Linux: `~/.config/GIMP/3.0/plug-ins/`
    *   Windows: `C:\Users\<username>\AppData\Roaming\GIMP\3.0\plug-ins\`
    *   macOS: `~/Library/Application Support/GIMP/3.0/plug-ins/`

3.  **Copy the Plugin File**:
    *   Create a directory in the plug-ins folder named `gimp-mcp-plugin` (e.g., `~/.config/GIMP/3.0/plug-ins/gimp-mcp-plugin/`).
    *   Place the `gimp-mcp-plugin.py` file (from the cloned repository) into this newly created directory.

4.  **Make the Plugin Executable (Linux/macOS)**:```bash
chmod +x <your_gimp_plugin_directory>/gimp-mcp-plugin/gimp-mcp-plugin.py
```    (Replace `<your_gimp_plugin_directory>` with the actual path from step 2, e.g., `~/.config/GIMP/3.0/plug-ins`).

5.  **Restart GIMP**:
    Relaunch GIMP to recognize the new plugin.

6.  **Start the MCP Server via GIMP**:
    To start the MCP server, navigate to `Filters > Development > Start MCP Server` in GIMP's menu. This will activate the plugin and initiate the server, which will then listen on `localhost:9876` (or as configured).

## Client Interaction

Once the MCP server is running within GIMP (activated via the plugin), an external MCP client application is needed to send commands to GIMP. An example client (`gimp_mcp_client.py` in some older versions or related projects) can serve as a basic template for how a Python client connects to the server and sends JSON-based commands to interact with GIMP.

The typical workflow involves the client sending a JSON object specifying the `type` of command (e.g., `call_api`) and `params` detailing the GIMP procedure to execute along with its arguments.

## Usage Examples

(Ensure the MCP server is started via the GIMP plugin as described above, and you have an MCP client to send commands.)

### AI-Powered Background Removal

### Image Inpainting with AI

## Human-AI Interaction Prompts

To effectively utilize AI within GIMP via MCP, an AI client application would typically interpret human prompts and translate them into actions. These actions often involve communicating with AI models and then using MCP to instruct GIMP:

*   **Object Recognition**:
    *   User Prompt to AI Client: “Identify and select all objects in the image.”
    *   AI Client Process:
        1.  Retrieves image from GIMP via MCP.
        2.  Sends to an object recognition AI model.
        3.  Receives object boundaries/masks from the model.
        4.  Uses MCP to send commands to GIMP to create selections based on these boundaries.
*   **Style Transfer**:
    *   User Prompt to AI Client: “Apply Van Gogh’s Starry Night style to the current image.”
    *   AI Client Process:
        1.  Retrieves image from GIMP.
        2.  Sends to a style transfer AI model along with the style reference.
        3.  Receives stylized image.
        4.  Uses MCP to update the image in GIMP.
*   **Image Enhancement**:
    *   Prompt: “Enhance the image resolution and reduce noise.”
    *   AI Response: The AI upscales the image and applies noise reduction techniques.

## Available API Commands

The `gimp-mcp-plugin.py` plugin allows external MCP clients to call GIMP PDB (Procedural Database) functions using a JSON structure. The primary command `type` is `call_api`.

Example JSON command sent by a client:{
  "type": "call_api",
  "params": {
    "api_path": "Image.new",
    "args": [400, 300, 0],
    "kwargs": {}
  }
}(In this example, `api_path: "Image.new"` might correspond to `Gimp.Image.new` or a similar PDB call, `args` are positional arguments like width, height, Gimp.ImageType (0 for RGB), and `kwargs` for named arguments.)

Commonly used `api_path` values correspond to GIMP procedures (often found within `Gimp.PDB` or as methods of `Gimp` objects). The plugin resolves `api_path` by `getattr` starting from the `Gimp` module. Some examples:
- `Image.new`: Create a new image.
- `Layer.new`: Add a new layer.
- `TextLayer.new`: Create a new text layer.
- `file_load`: Load an image file.
- `file_save`: Save the current image.
- `edit_fill`: Fill a selection or layer.
- `context_set_foreground`: Set the foreground color.
- `Layer.set_offsets`: Set layer position.

The specific command names like `gimp_image_new` mentioned previously might be simplified representations or aliases. For a comprehensive list of GIMP procedures and their parameters, refer to the official GIMP Python API documentation (accessible through GIMP's help system: `Help > Python Console`, then browse PDB).

## Extras

### gimp-api-scraper.py

This was created to scrape the Gimp 3.0 API documentation and turn it into an OpenAPI spec for easier consumption by the Model Context Protocol.

## Additional Resources

- **MCP Hub - GIMP MCP**: For more details and context on GIMP MCP integrations, you might find information on sites like [mcphub.tools](https://mcphub.tools/detail/libreearth/gimp-mcp) (note: this link points to the `libreearth` fork, but may still contain relevant conceptual information).
- **GIMP Python Documentation**: Consult the official GIMP documentation for Python scripting and available PDB procedures.

## Contributing

We welcome contributions to enhance GIMP-MCP:
1. Fork the Repository:
  Click the “Fork” button on GitHub.
2. Create a Feature Branch:
  `git checkout -b feature/your-feature-name`
3. Commit Your Changes:
  `git commit -m "Add feature: your feature description"`
4. Push to Your Fork:
  `git push origin feature/your-feature-name`
5. Submit a Pull Request:
  Describe your changes and submit for review.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

We extend our gratitude to the developers and researchers who have contributed to integrating AI capabilities within GIMP, making advanced image editing accessible to all.

⸻

Note: The integration of MCP with GIMP is an ongoing project. For the latest updates and community support, visit our discussion forum.
