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
            self.sock.connect((self.host, self.port))
            logger.info(f"Connected to GIMP at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            raise ConnectionError("Could not connect to GIMP. Ensure the MCP Server plugin is running.")

    def send_command(self, command_type, params=None):
        if not self.sock:
            self.connect()
        command = {"type": command_type, "params": params or {}}
        try:
            self.sock.sendall(json.dumps(command).encode('utf-8'))
            response = self.sock.recv(1024)
            self.sock = None
            return json.loads(response.decode('utf-8'))
        except Exception as e:
            logger.error(f"Communication error: {e}")
            self.sock = None
            raise Exception(f"Error communicating with GIMP: {e}")

# Global connection
_gimp_connection = None

def get_gimp_connection():
    global _gimp_connection
    if _gimp_connection is None:
        _gimp_connection = GimpConnection()
        _gimp_connection.connect()
    return _gimp_connection

# MCP server
mcp = FastMCP('SampleMCP', description='Sample integration through MCP')

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
            return f"Error: {json.dumps(result["error"])}"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def Gimp_Brush_get_angle(ctx: Context, angle: float) -> str:
    """Gets the rotation angle of a generated brush.

    :param angle: The rotation angle of the brush in degree.
    """
    return call_api(ctx, 'Gimp.Brush.get_angle', args=[angle])

@mcp.tool()
def Gimp_Brush_get_aspect_ratio(ctx: Context, aspect_ratio: float) -> str:
    """Gets the aspect ratio of a generated brush.

    :param aspect_ratio: The aspect ratio of the brush.
    """
    return call_api(ctx, 'Gimp.Brush.get_aspect_ratio', args=[aspect_ratio])

@mcp.tool()
def Gimp_Brush_get_buffer(ctx: Context, max_width: int, max_height: int, format: str) -> str:
    """Gets pixel data of the brush within the bounding box specified by max_width
and max_height. The data will be scaled down so that it fits within this
size without changing its ratio. If the brush is smaller than this size to
begin with, it will not be scaled up.

    :param max_width: A maximum width for the returned buffer.
    :param max_height: A maximum height for the returned buffer.
    :param format: An optional Babl format.
    """
    return call_api(ctx, 'Gimp.Brush.get_buffer', args=[max_width, max_height, format])

@mcp.tool()
def Gimp_Brush_get_hardness(ctx: Context, hardness: float) -> str:
    """Gets the hardness of a generated brush.

    :param hardness: The hardness of the brush.
    """
    return call_api(ctx, 'Gimp.Brush.get_hardness', args=[hardness])

@mcp.tool()
def Gimp_Brush_get_info(ctx: Context, width: int, height: int, mask_bpp: int, color_bpp: int) -> str:
    """Gets information about the brush.

    :param width: The brush width.
    :param height: The brush height.
    :param mask_bpp: The brush mask bpp.
    :param color_bpp: The brush color bpp.
    """
    return call_api(ctx, 'Gimp.Brush.get_info', args=[width, height, mask_bpp, color_bpp])

@mcp.tool()
def Gimp_Brush_get_mask(ctx: Context, max_width: int, max_height: int, format: str) -> str:
    """Gets mask data of the brush within the bounding box specified by max_width
and max_height. The data will be scaled down so that it fits within this
size without changing its ratio. If the brush is smaller than this size to
begin with, it will not be scaled up.

    :param max_width: A maximum width for the returned buffer.
    :param max_height: A maximum height for the returned buffer.
    :param format: An optional Babl format.
    """
    return call_api(ctx, 'Gimp.Brush.get_mask', args=[max_width, max_height, format])

@mcp.tool()
def Gimp_Brush_get_radius(ctx: Context, radius: float) -> str:
    """Gets the radius of a generated brush.

    :param radius: The radius of the brush in pixels.
    """
    return call_api(ctx, 'Gimp.Brush.get_radius', args=[radius])

@mcp.tool()
def Gimp_Brush_get_shape(ctx: Context, shape: str) -> str:
    """Gets the shape of a generated brush.

    :param shape: The brush shape.
    """
    return call_api(ctx, 'Gimp.Brush.get_shape', args=[shape])

@mcp.tool()
def Gimp_Brush_get_spacing(ctx: Context) -> str:
    """Gets the brush spacing, the stamping frequency.

    """
    return call_api(ctx, 'Gimp.Brush.get_spacing', args=[])

@mcp.tool()
def Gimp_Brush_get_spikes(ctx: Context, spikes: int) -> str:
    """Gets the number of spikes for a generated brush.

    :param spikes: The number of spikes on the brush.
    """
    return call_api(ctx, 'Gimp.Brush.get_spikes', args=[spikes])

@mcp.tool()
def Gimp_Brush_is_generated(ctx: Context) -> str:
    """Whether the brush is generated (parametric versus raster).

    """
    return call_api(ctx, 'Gimp.Brush.is_generated', args=[])

@mcp.tool()
def Gimp_Brush_set_angle(ctx: Context, angle_in: float, angle_out: float) -> str:
    """Sets the rotation angle of a generated brush.

    :param angle_in: The desired brush rotation angle in degrees.
    :param angle_out: The brush rotation angle actually assigned.
    """
    return call_api(ctx, 'Gimp.Brush.set_angle', args=[angle_in, angle_out])

@mcp.tool()
def Gimp_Brush_set_aspect_ratio(ctx: Context, aspect_ratio_in: float, aspect_ratio_out: float) -> str:
    """Sets the aspect ratio of a generated brush.

    :param aspect_ratio_in: The desired brush aspect ratio.
    :param aspect_ratio_out: The brush aspect ratio actually assigned.
    """
    return call_api(ctx, 'Gimp.Brush.set_aspect_ratio', args=[aspect_ratio_in, aspect_ratio_out])

@mcp.tool()
def Gimp_Brush_set_hardness(ctx: Context, hardness_in: float, hardness_out: float) -> str:
    """Sets the hardness of a generated brush.

    :param hardness_in: The desired brush hardness.
    :param hardness_out: The brush hardness actually assigned.
    """
    return call_api(ctx, 'Gimp.Brush.set_hardness', args=[hardness_in, hardness_out])

@mcp.tool()
def Gimp_Brush_set_radius(ctx: Context, radius_in: float, radius_out: float) -> str:
    """Sets the radius of a generated brush.

    :param radius_in: The desired brush radius in pixel.
    :param radius_out: The brush radius actually assigned.
    """
    return call_api(ctx, 'Gimp.Brush.set_radius', args=[radius_in, radius_out])

@mcp.tool()
def Gimp_Brush_set_shape(ctx: Context, shape_in: str, shape_out: str) -> str:
    """Sets the shape of a generated brush.

    :param shape_in: The brush shape.
    :param shape_out: The brush shape actually assigned.
    """
    return call_api(ctx, 'Gimp.Brush.set_shape', args=[shape_in, shape_out])

@mcp.tool()
def Gimp_Brush_set_spacing(ctx: Context, spacing: int) -> str:
    """Sets the brush spacing.

    :param spacing: The brush spacing.
    """
    return call_api(ctx, 'Gimp.Brush.set_spacing', args=[spacing])

@mcp.tool()
def Gimp_Brush_set_spikes(ctx: Context, spikes_in: int, spikes_out: int) -> str:
    """Sets the number of spikes for a generated brush.

    :param spikes_in: The desired number of spikes.
    :param spikes_out: The number of spikes actually assigned.
    """
    return call_api(ctx, 'Gimp.Brush.set_spikes', args=[spikes_in, spikes_out])

@mcp.tool()
def Gimp_Channel_combine_masks(ctx: Context, channel2: str, operation: str, offx: int, offy: int) -> str:
    """Combine two channel masks.

    :param channel2: The channel2.
    :param operation: The selection operation.
    :param offx: X offset between upper left corner of channels: (second - first).
    :param offy: Y offset between upper left corner of channels: (second - first).
    """
    return call_api(ctx, 'Gimp.Channel.combine_masks', args=[channel2, operation, offx, offy])

@mcp.tool()
def Gimp_Channel_copy(ctx: Context) -> str:
    """Copy a channel.

    """
    return call_api(ctx, 'Gimp.Channel.copy', args=[])

@mcp.tool()
def Gimp_Channel_get_color(ctx: Context) -> str:
    """Get the compositing color of the specified channel.

    """
    return call_api(ctx, 'Gimp.Channel.get_color', args=[])

@mcp.tool()
def Gimp_Channel_get_opacity(ctx: Context) -> str:
    """Get the opacity of the specified channel.

    """
    return call_api(ctx, 'Gimp.Channel.get_opacity', args=[])

@mcp.tool()
def Gimp_Channel_get_show_masked(ctx: Context) -> str:
    """Get the composite method of the specified channel.

    """
    return call_api(ctx, 'Gimp.Channel.get_show_masked', args=[])

@mcp.tool()
def Gimp_Channel_set_color(ctx: Context, color: str) -> str:
    """Set the compositing color of the specified channel.

    :param color: The new channel compositing color.
    """
    return call_api(ctx, 'Gimp.Channel.set_color', args=[color])

@mcp.tool()
def Gimp_Channel_set_opacity(ctx: Context, opacity: float) -> str:
    """Set the opacity of the specified channel.

    :param opacity: The new channel opacity.
    """
    return call_api(ctx, 'Gimp.Channel.set_opacity', args=[opacity])

@mcp.tool()
def Gimp_Channel_set_show_masked(ctx: Context, show_masked: bool) -> str:
    """Set the composite method of the specified channel.

    :param show_masked: The new channel composite method.
    """
    return call_api(ctx, 'Gimp.Channel.set_show_masked', args=[show_masked])

@mcp.tool()
def Gimp_Choice_add(ctx: Context, nick: str, id: int, label: str, help: str) -> str:
    """This procedure adds a new possible value to choice list of values.
The id is an optional integer identifier. This can be useful for instance
when you want to work with different enum values mapped to each nick.

    :param nick: The nick of choice.
    :param id: Optional integer ID for nick.
    :param label: The label of choice.
    :param help: Optional longer help text for nick.
    """
    return call_api(ctx, 'Gimp.Choice.add', args=[nick, id, label, help])

@mcp.tool()
def Gimp_Choice_get_documentation(ctx: Context, nick: str, label: str, help: str) -> str:
    """Returns the documentation strings for nick.

    :param nick: The possible value’s nick you need documentation for.
    :param label: The label of nick.
    :param help: The help text of nick.
    """
    return call_api(ctx, 'Gimp.Choice.get_documentation', args=[nick, label, help])

@mcp.tool()
def Gimp_Choice_get_help(ctx: Context, nick: str) -> str:
    """Returns the longer documentation for nick.

    :param nick: The nick to lookup.
    """
    return call_api(ctx, 'Gimp.Choice.get_help', args=[nick])

@mcp.tool()
def Gimp_Choice_get_id(ctx: Context, nick: str) -> str:
    """Available since: 3.0

    :param nick: The nick to lookup.
    """
    return call_api(ctx, 'Gimp.Choice.get_id', args=[nick])

@mcp.tool()
def Gimp_Choice_get_label(ctx: Context, nick: str) -> str:
    """Available since: 3.0

    :param nick: The nick to lookup.
    """
    return call_api(ctx, 'Gimp.Choice.get_label', args=[nick])

@mcp.tool()
def Gimp_Choice_is_valid(ctx: Context, nick: str) -> str:
    """This procedure checks if the given nick is valid and refers to
an existing choice.

    :param nick: The nick to check.
    """
    return call_api(ctx, 'Gimp.Choice.is_valid', args=[nick])

@mcp.tool()
def Gimp_Choice_list_nicks(ctx: Context) -> str:
    """This procedure returns the list of nicks allowed for choice.

    """
    return call_api(ctx, 'Gimp.Choice.list_nicks', args=[])

@mcp.tool()
def Gimp_Choice_set_sensitive(ctx: Context, nick: str, sensitive: bool) -> str:
    """Change the sensitivity of a possible nick. Technically a non-sensitive nick
means it cannot be chosen anymore (so gimp_choice_is_valid() will
return FALSE; nevertheless gimp_choice_list_nicks() and other
functions to get information about a choice will still function).

    :param nick: The nick to lookup.
    :param sensitive: No description available.
    """
    return call_api(ctx, 'Gimp.Choice.set_sensitive', args=[nick, sensitive])

@mcp.tool()
def Gimp_ColorConfig_get_cmyk_color_profile(ctx: Context) -> str:
    """Available since: 2.10

    """
    return call_api(ctx, 'Gimp.ColorConfig.get_cmyk_color_profile', args=[])

@mcp.tool()
def Gimp_ColorConfig_get_display_bpc(ctx: Context) -> str:
    """Available since: 2.10

    """
    return call_api(ctx, 'Gimp.ColorConfig.get_display_bpc', args=[])

@mcp.tool()
def Gimp_ColorConfig_get_display_color_profile(ctx: Context) -> str:
    """Available since: 2.10

    """
    return call_api(ctx, 'Gimp.ColorConfig.get_display_color_profile', args=[])

@mcp.tool()
def Gimp_ColorConfig_get_display_intent(ctx: Context) -> str:
    """Available since: 2.10

    """
    return call_api(ctx, 'Gimp.ColorConfig.get_display_intent', args=[])

@mcp.tool()
def Gimp_ColorConfig_get_display_optimize(ctx: Context) -> str:
    """Available since: 2.10

    """
    return call_api(ctx, 'Gimp.ColorConfig.get_display_optimize', args=[])

@mcp.tool()
def Gimp_ColorConfig_get_display_profile_from_gdk(ctx: Context) -> str:
    """Available since: 2.10

    """
    return call_api(ctx, 'Gimp.ColorConfig.get_display_profile_from_gdk', args=[])

@mcp.tool()
def Gimp_ColorConfig_get_gray_color_profile(ctx: Context) -> str:
    """Available since: 2.10

    """
    return call_api(ctx, 'Gimp.ColorConfig.get_gray_color_profile', args=[])

@mcp.tool()
def Gimp_ColorConfig_get_mode(ctx: Context) -> str:
    """Available since: 2.10

    """
    return call_api(ctx, 'Gimp.ColorConfig.get_mode', args=[])

@mcp.tool()
def Gimp_ColorConfig_get_out_of_gamut_color(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.ColorConfig.get_out_of_gamut_color', args=[])

@mcp.tool()
def Gimp_ColorConfig_get_rgb_color_profile(ctx: Context) -> str:
    """Available since: 2.10

    """
    return call_api(ctx, 'Gimp.ColorConfig.get_rgb_color_profile', args=[])

@mcp.tool()
def Gimp_ColorConfig_get_simulation_bpc(ctx: Context) -> str:
    """Available since: 2.10

    """
    return call_api(ctx, 'Gimp.ColorConfig.get_simulation_bpc', args=[])

@mcp.tool()
def Gimp_ColorConfig_get_simulation_color_profile(ctx: Context) -> str:
    """Available since: 2.10

    """
    return call_api(ctx, 'Gimp.ColorConfig.get_simulation_color_profile', args=[])

@mcp.tool()
def Gimp_ColorConfig_get_simulation_gamut_check(ctx: Context) -> str:
    """Available since: 2.10

    """
    return call_api(ctx, 'Gimp.ColorConfig.get_simulation_gamut_check', args=[])

@mcp.tool()
def Gimp_ColorConfig_get_simulation_intent(ctx: Context) -> str:
    """Available since: 2.10

    """
    return call_api(ctx, 'Gimp.ColorConfig.get_simulation_intent', args=[])

@mcp.tool()
def Gimp_ColorConfig_get_simulation_optimize(ctx: Context) -> str:
    """Available since: 2.10

    """
    return call_api(ctx, 'Gimp.ColorConfig.get_simulation_optimize', args=[])

@mcp.tool()
def Gimp_ColorProfile_get_copyright(ctx: Context) -> str:
    """Available since: 2.10

    """
    return call_api(ctx, 'Gimp.ColorProfile.get_copyright', args=[])

@mcp.tool()
def Gimp_ColorProfile_get_description(ctx: Context) -> str:
    """Available since: 2.10

    """
    return call_api(ctx, 'Gimp.ColorProfile.get_description', args=[])

@mcp.tool()
def Gimp_ColorProfile_get_format(ctx: Context, format: str, intent: str, error: str = None) -> str:
    """This function takes a GimpColorProfile and a Babl format and
returns a new Babl format with profile‘s RGB primaries and TRC,
and format‘s pixel layout.

    :param format: A Babl format.
    :param intent: A GimpColorRenderingIntent.
    :param error: No description available.
    """
    return call_api(ctx, 'Gimp.ColorProfile.get_format', args=[format, intent, error])

@mcp.tool()
def Gimp_ColorProfile_get_icc_profile(ctx: Context, length: int) -> str:
    """This function returns profile as ICC profile data. The returned
memory belongs to profile and must not be modified or freed.

    :param length: Return location for the number of bytes.
    """
    return call_api(ctx, 'Gimp.ColorProfile.get_icc_profile', args=[length])

@mcp.tool()
def Gimp_ColorProfile_get_label(ctx: Context) -> str:
    """This function returns a string containing profile‘s “title”, a
string that can be used to label the profile in a user interface.

    """
    return call_api(ctx, 'Gimp.ColorProfile.get_label', args=[])

@mcp.tool()
def Gimp_ColorProfile_get_lcms_profile(ctx: Context) -> str:
    """This function returns profile‘s cmsHPROFILE. The returned
value belongs to profile and must not be modified or freed.

    """
    return call_api(ctx, 'Gimp.ColorProfile.get_lcms_profile', args=[])

@mcp.tool()
def Gimp_ColorProfile_get_manufacturer(ctx: Context) -> str:
    """Available since: 2.10

    """
    return call_api(ctx, 'Gimp.ColorProfile.get_manufacturer', args=[])

@mcp.tool()
def Gimp_ColorProfile_get_model(ctx: Context) -> str:
    """Available since: 2.10

    """
    return call_api(ctx, 'Gimp.ColorProfile.get_model', args=[])

@mcp.tool()
def Gimp_ColorProfile_get_space(ctx: Context, intent: str, error: str = None) -> str:
    """This function returns the Babl space of profile, for the
specified intent.

    :param intent: A GimpColorRenderingIntent.
    :param error: No description available.
    """
    return call_api(ctx, 'Gimp.ColorProfile.get_space', args=[intent, error])

@mcp.tool()
def Gimp_ColorProfile_get_summary(ctx: Context) -> str:
    """This function return a string containing a multi-line summary of
profile‘s description, model, manufacturer and copyright, to be
used as detailed information about the profile in a user interface.

    """
    return call_api(ctx, 'Gimp.ColorProfile.get_summary', args=[])

@mcp.tool()
def Gimp_ColorProfile_is_cmyk(ctx: Context) -> str:
    """Available since: 2.10

    """
    return call_api(ctx, 'Gimp.ColorProfile.is_cmyk', args=[])

@mcp.tool()
def Gimp_ColorProfile_is_equal(ctx: Context, profile2: str) -> str:
    """Compares two profiles.

    :param profile2: A GimpColorProfile.
    """
    return call_api(ctx, 'Gimp.ColorProfile.is_equal', args=[profile2])

@mcp.tool()
def Gimp_ColorProfile_is_gray(ctx: Context) -> str:
    """Available since: 2.10

    """
    return call_api(ctx, 'Gimp.ColorProfile.is_gray', args=[])

@mcp.tool()
def Gimp_ColorProfile_is_linear(ctx: Context) -> str:
    """This function determines is the ICC profile represented by a GimpColorProfile
is a linear RGB profile or not, some profiles that are LUTs though linear
will also return FALSE;

    """
    return call_api(ctx, 'Gimp.ColorProfile.is_linear', args=[])

@mcp.tool()
def Gimp_ColorProfile_is_rgb(ctx: Context) -> str:
    """Available since: 2.10

    """
    return call_api(ctx, 'Gimp.ColorProfile.is_rgb', args=[])

@mcp.tool()
def Gimp_ColorProfile_new_linear_from_color_profile(ctx: Context) -> str:
    """This function creates a new RGB GimpColorProfile with a linear TRC
and profile‘s RGB chromacities and whitepoint.

    """
    return call_api(ctx, 'Gimp.ColorProfile.new_linear_from_color_profile', args=[])

@mcp.tool()
def Gimp_ColorProfile_new_srgb_trc_from_color_profile(ctx: Context) -> str:
    """This function creates a new RGB GimpColorProfile with a sRGB gamma
TRC and profile‘s RGB chromacities and whitepoint.

    """
    return call_api(ctx, 'Gimp.ColorProfile.new_srgb_trc_from_color_profile', args=[])

@mcp.tool()
def Gimp_ColorProfile_save_to_file(ctx: Context, file: str, error: str = None) -> str:
    """This function saves profile to file as ICC profile.

    :param file: A GFile.
    :param error: No description available.
    """
    return call_api(ctx, 'Gimp.ColorProfile.save_to_file', args=[file, error])

@mcp.tool()
def Gimp_ColorTransform_process_buffer(ctx: Context, src_buffer: str, src_rect: str, dest_buffer: str, dest_rect: str) -> str:
    """This function transforms buffer into another buffer.

    :param src_buffer: Source GeglBuffer.
    :param src_rect: Rectangle in src_buffer.
    :param dest_buffer: Destination GeglBuffer.
    :param dest_rect: Rectangle in dest_buffer.
    """
    return call_api(ctx, 'Gimp.ColorTransform.process_buffer', args=[src_buffer, src_rect, dest_buffer, dest_rect])

@mcp.tool()
def Gimp_ColorTransform_process_pixels(ctx: Context, src_format: str, src_pixels: str = None, dest_format: str, dest_pixels: str = None, length: int) -> str:
    """This function transforms a contiguous line of pixels.

    :param src_format: Babl format of src_pixels.
    :param src_pixels: Pointer to the source pixels.
    :param dest_format: Babl format of dest_pixels.
    :param dest_pixels: Pointer to the destination pixels.
    :param length: Number of pixels to process.
    """
    return call_api(ctx, 'Gimp.ColorTransform.process_pixels', args=[src_format, src_pixels, dest_format, dest_pixels, length])

@mcp.tool()
def Gimp_Display_delete(ctx: Context) -> str:
    """Delete the specified display.

    """
    return call_api(ctx, 'Gimp.Display.delete', args=[])

@mcp.tool()
def Gimp_Display_get_id(ctx: Context) -> str:
    """mostly internal data and not reusable across sessions.

    """
    return call_api(ctx, 'Gimp.Display.get_id', args=[])

@mcp.tool()
def Gimp_Display_get_window_handle(ctx: Context) -> str:
    """Get a handle to the native window for an image display.

    """
    return call_api(ctx, 'Gimp.Display.get_window_handle', args=[])

@mcp.tool()
def Gimp_Display_is_valid(ctx: Context) -> str:
    """Returns TRUE if the display is valid.

    """
    return call_api(ctx, 'Gimp.Display.is_valid', args=[])

@mcp.tool()
def Gimp_Display_present(ctx: Context) -> str:
    """Present the specified display.

    """
    return call_api(ctx, 'Gimp.Display.present', args=[])

@mcp.tool()
def Gimp_Drawable_append_filter(ctx: Context, filter: str) -> str:
    """This procedure appends the specified drawable effect at the top of the
effect list of drawable.

    :param filter: The drawable filter to append.
    """
    return call_api(ctx, 'Gimp.Drawable.append_filter', args=[filter])

@mcp.tool()
def Gimp_Drawable_append_new_filter(ctx: Context, operation_name: str, name: str, mode: str, opacity: float, ...: str = None) -> str:
    """Utility function which combines gimp_drawable_filter_new()
followed by setting arguments for the
GimpDrawableFilterConfig returned by
gimp_drawable_filter_get_config(), and finally appending with
gimp_drawable_append_filter()

    :param operation_name: The GEGL operation’s name.
    :param name: The effect name.
    :param mode: The blend mode.
    :param opacity: The opacity from 0.0 (transparent) to 1.0 (opaque).
    :param ...: A NULL-terminated list of operation argument names
                 and values.
    """
    return call_api(ctx, 'Gimp.Drawable.append_new_filter', args=[operation_name, name, mode, opacity, ...])

@mcp.tool()
def Gimp_Drawable_brightness_contrast(ctx: Context, brightness: float, contrast: float) -> str:
    """Modify brightness/contrast in the specified drawable.

    :param brightness: Brightness adjustment.
    :param contrast: Contrast adjustment.
    """
    return call_api(ctx, 'Gimp.Drawable.brightness_contrast', args=[brightness, contrast])

@mcp.tool()
def Gimp_Drawable_color_balance(ctx: Context, transfer_mode: str, preserve_lum: bool, cyan_red: float, magenta_green: float, yellow_blue: float) -> str:
    """Modify the color balance of the specified drawable.

    :param transfer_mode: Transfer mode.
    :param preserve_lum: Preserve luminosity values at each pixel.
    :param cyan_red: Cyan-Red color balance.
    :param magenta_green: Magenta-Green color balance.
    :param yellow_blue: Yellow-Blue color balance.
    """
    return call_api(ctx, 'Gimp.Drawable.color_balance', args=[transfer_mode, preserve_lum, cyan_red, magenta_green, yellow_blue])

@mcp.tool()
def Gimp_Drawable_colorize_hsl(ctx: Context, hue: float, saturation: float, lightness: float) -> str:
    """Render the drawable as a grayscale image seen through a colored glass.

    :param hue: Hue in degrees.
    :param saturation: Saturation in percent.
    :param lightness: Lightness in percent.
    """
    return call_api(ctx, 'Gimp.Drawable.colorize_hsl', args=[hue, saturation, lightness])

@mcp.tool()
def Gimp_Drawable_curves_explicit(ctx: Context, channel: str, num_values: int, values: str) -> str:
    """Modifies the intensity curve(s) for specified drawable.

    :param channel: The channel to modify.
    :param num_values: The number of values in the new curve.
    :param values: The explicit curve.
    """
    return call_api(ctx, 'Gimp.Drawable.curves_explicit', args=[channel, num_values, values])

@mcp.tool()
def Gimp_Drawable_curves_spline(ctx: Context, channel: str, num_points: int, points: str) -> str:
    """Modifies the intensity curve(s) for specified drawable.

    :param channel: The channel to modify.
    :param num_points: The number of values in the control point array.
    :param points: The spline control points: { cp1.x, cp1.y, cp2.x, cp2.y, … }.
    """
    return call_api(ctx, 'Gimp.Drawable.curves_spline', args=[channel, num_points, points])

@mcp.tool()
def Gimp_Drawable_desaturate(ctx: Context, desaturate_mode: str) -> str:
    """Desaturate the contents of the specified drawable, with the
specified formula.

    :param desaturate_mode: The formula to use to desaturate.
    """
    return call_api(ctx, 'Gimp.Drawable.desaturate', args=[desaturate_mode])

@mcp.tool()
def Gimp_Drawable_edit_bucket_fill(ctx: Context, fill_type: str, x: float, y: float) -> str:
    """Fill the area by a seed fill starting at the specified coordinates.

    :param fill_type: The type of fill.
    :param x: The x coordinate of this bucket fill’s application.
    :param y: The y coordinate of this bucket fill’s application.
    """
    return call_api(ctx, 'Gimp.Drawable.edit_bucket_fill', args=[fill_type, x, y])

@mcp.tool()
def Gimp_Drawable_edit_clear(ctx: Context) -> str:
    """Clear selected area of drawable.

    """
    return call_api(ctx, 'Gimp.Drawable.edit_clear', args=[])

@mcp.tool()
def Gimp_Drawable_edit_fill(ctx: Context, fill_type: str) -> str:
    """Fill selected area of drawable.

    :param fill_type: The type of fill.
    """
    return call_api(ctx, 'Gimp.Drawable.edit_fill', args=[fill_type])

@mcp.tool()
def Gimp_Drawable_edit_gradient_fill(ctx: Context, gradient_type: str, offset: float, supersample: bool, supersample_max_depth: int, supersample_threshold: float, dither: bool, x1: float, y1: float, x2: float, y2: float) -> str:
    """Draw a gradient between the starting and ending coordinates with the
specified gradient type.

    :param gradient_type: The type of gradient.
    :param offset: Offset relates to the starting and ending coordinates specified for the blend. This parameter is mode dependent.
    :param supersample: Do adaptive supersampling.
    :param supersample_max_depth: Maximum recursion levels for supersampling.
    :param supersample_threshold: Supersampling threshold.
    :param dither: Use dithering to reduce banding.
    :param x1: The x coordinate of this gradient’s starting point.
    :param y1: The y coordinate of this gradient’s starting point.
    :param x2: The x coordinate of this gradient’s ending point.
    :param y2: The y coordinate of this gradient’s ending point.
    """
    return call_api(ctx, 'Gimp.Drawable.edit_gradient_fill', args=[gradient_type, offset, supersample, supersample_max_depth, supersample_threshold, dither, x1, y1, x2, y2])

@mcp.tool()
def Gimp_Drawable_edit_stroke_item(ctx: Context, item: str) -> str:
    """Stroke the specified item

    :param item: The item to stroke.
    """
    return call_api(ctx, 'Gimp.Drawable.edit_stroke_item', args=[item])

@mcp.tool()
def Gimp_Drawable_edit_stroke_selection(ctx: Context) -> str:
    """Stroke the current selection

    """
    return call_api(ctx, 'Gimp.Drawable.edit_stroke_selection', args=[])

@mcp.tool()
def Gimp_Drawable_equalize(ctx: Context, mask_only: bool) -> str:
    """Equalize the contents of the specified drawable.

    :param mask_only: Equalization option.
    """
    return call_api(ctx, 'Gimp.Drawable.equalize', args=[mask_only])

@mcp.tool()
def Gimp_Drawable_extract_component(ctx: Context, component: int, invert: bool, linear: bool) -> str:
    """Extract a color model component.

    :param component: Component (RGB Red (0), RGB Green (1), RGB Blue (2), Hue (3), HSV Saturation (4), HSV Value (5), HSL Saturation (6), HSL Lightness (7), CMYK Cyan (8), CMYK Magenta (9), CMYK Yellow (10), CMYK Key (11), Y’CbCr Y’ (12), Y’CbCr Cb (13), Y’CbCr Cr (14), LAB L (15), LAB A (16), LAB B (17), LCH C(ab) (18), LCH H(ab) (19), Alpha (20)).
    :param invert: Invert the extracted component.
    :param linear: Use linear output instead of gamma corrected.
    """
    return call_api(ctx, 'Gimp.Drawable.extract_component', args=[component, invert, linear])

@mcp.tool()
def Gimp_Drawable_fill(ctx: Context, fill_type: str) -> str:
    """Fill the drawable with the specified fill mode.

    :param fill_type: The type of fill.
    """
    return call_api(ctx, 'Gimp.Drawable.fill', args=[fill_type])

@mcp.tool()
def Gimp_Drawable_foreground_extract(ctx: Context, mode: str, mask: str) -> str:
    """Extract the foreground of a drawable using a given trimap.

    :param mode: The algorithm to use.
    :param mask: Tri-Map.
    """
    return call_api(ctx, 'Gimp.Drawable.foreground_extract', args=[mode, mask])

@mcp.tool()
def Gimp_Drawable_free_shadow(ctx: Context) -> str:
    """Free the specified drawable’s shadow data (if it exists).

    """
    return call_api(ctx, 'Gimp.Drawable.free_shadow', args=[])

@mcp.tool()
def Gimp_Drawable_get_bpp(ctx: Context) -> str:
    """Returns the bytes per pixel.

    """
    return call_api(ctx, 'Gimp.Drawable.get_bpp', args=[])

@mcp.tool()
def Gimp_Drawable_get_buffer(ctx: Context) -> str:
    """Returns a GeglBuffer of a specified drawable. The buffer can be used
like any other GEGL buffer. Its data will we synced back with the core
drawable when the buffer gets destroyed, or when gegl_buffer_flush()
is called.

    """
    return call_api(ctx, 'Gimp.Drawable.get_buffer', args=[])

@mcp.tool()
def Gimp_Drawable_get_filters(ctx: Context) -> str:
    """Returns the list of filters applied to the drawable.

    """
    return call_api(ctx, 'Gimp.Drawable.get_filters', args=[])

@mcp.tool()
def Gimp_Drawable_get_format(ctx: Context) -> str:
    """Returns the Babl format of the drawable.

    """
    return call_api(ctx, 'Gimp.Drawable.get_format', args=[])

@mcp.tool()
def Gimp_Drawable_get_height(ctx: Context) -> str:
    """Returns the height of the drawable.

    """
    return call_api(ctx, 'Gimp.Drawable.get_height', args=[])

@mcp.tool()
def Gimp_Drawable_get_offsets(ctx: Context, offset_x: int, offset_y: int) -> str:
    """Returns the offsets for the drawable.

    :param offset_x: X offset of drawable.
    :param offset_y: Y offset of drawable.
    """
    return call_api(ctx, 'Gimp.Drawable.get_offsets', args=[offset_x, offset_y])

@mcp.tool()
def Gimp_Drawable_get_pixel(ctx: Context, x_coord: int, y_coord: int) -> str:
    """Gets the value of the pixel at the specified coordinates.

    :param x_coord: The x coordinate.
    :param y_coord: The y coordinate.
    """
    return call_api(ctx, 'Gimp.Drawable.get_pixel', args=[x_coord, y_coord])

@mcp.tool()
def Gimp_Drawable_get_shadow_buffer(ctx: Context) -> str:
    """Returns a GeglBuffer of a specified drawable’s shadow tiles. The
buffer can be used like any other GEGL buffer. Its data will we
synced back with the core drawable’s shadow tiles when the buffer
gets destroyed, or when gegl_buffer_flush() is called.

    """
    return call_api(ctx, 'Gimp.Drawable.get_shadow_buffer', args=[])

@mcp.tool()
def Gimp_Drawable_get_sub_thumbnail(ctx: Context, src_x: int, src_y: int, src_width: int, src_height: int, dest_width: int, dest_height: int, alpha: str) -> str:
    """Retrieves a thumbnail pixbuf for the drawable identified by
drawable. The thumbnail will be not larger than the requested size.

    :param src_x: The x coordinate of the area.
    :param src_y: The y coordinate of the area.
    :param src_width: The width of the area.
    :param src_height: The height of the area.
    :param dest_width: The requested thumbnail width  (<= 1024 pixels)
    :param dest_height: The requested thumbnail height (<= 1024 pixels)
    :param alpha: How to handle an alpha channel.
    """
    return call_api(ctx, 'Gimp.Drawable.get_sub_thumbnail', args=[src_x, src_y, src_width, src_height, dest_width, dest_height, alpha])

@mcp.tool()
def Gimp_Drawable_get_sub_thumbnail_data(ctx: Context, src_x: int, src_y: int, src_width: int, src_height: int, dest_width: int, dest_height: int, actual_width: int, actual_height: int, bpp: int) -> str:
    """Retrieves thumbnail data for the drawable identified by drawable.
The thumbnail will be not larger than the requested size.

    :param src_x: The x coordinate of the area.
    :param src_y: The y coordinate of the area.
    :param src_width: The width of the area.
    :param src_height: The height of the area.
    :param dest_width: The requested thumbnail width  (<= 1024 pixels)
    :param dest_height: The requested thumbnail height (<= 1024 pixels)
    :param actual_width: The width of the returned thumbnail.
    :param actual_height: The height of the returned thumbnail.
    :param bpp: The bytes per pixel of the returned thumbnail data.
    """
    return call_api(ctx, 'Gimp.Drawable.get_sub_thumbnail_data', args=[src_x, src_y, src_width, src_height, dest_width, dest_height, actual_width, actual_height, bpp])

@mcp.tool()
def Gimp_Drawable_get_thumbnail(ctx: Context, width: int, height: int, alpha: str) -> str:
    """Retrieves a thumbnail pixbuf for the drawable identified by
drawable. The thumbnail will be not larger than the requested size.

    :param width: The requested thumbnail width  (<= 1024 pixels)
    :param height: The requested thumbnail height (<= 1024 pixels)
    :param alpha: How to handle an alpha channel.
    """
    return call_api(ctx, 'Gimp.Drawable.get_thumbnail', args=[width, height, alpha])

@mcp.tool()
def Gimp_Drawable_get_thumbnail_data(ctx: Context, width: int, height: int, actual_width: int, actual_height: int, bpp: int) -> str:
    """Retrieves thumbnail data for the drawable identified by drawable.
The thumbnail will be not larger than the requested size.

    :param width: The requested thumbnail width  (<= 1024 pixels)
    :param height: The requested thumbnail height (<= 1024 pixels)
    :param actual_width: The resulting thumbnail’s actual width.
    :param actual_height: The resulting thumbnail’s actual height.
    :param bpp: The bytes per pixel of the returned thubmnail data.
    """
    return call_api(ctx, 'Gimp.Drawable.get_thumbnail_data', args=[width, height, actual_width, actual_height, bpp])

@mcp.tool()
def Gimp_Drawable_get_thumbnail_format(ctx: Context) -> str:
    """Returns the Babl thumbnail format of the drawable.

    """
    return call_api(ctx, 'Gimp.Drawable.get_thumbnail_format', args=[])

@mcp.tool()
def Gimp_Drawable_get_width(ctx: Context) -> str:
    """Returns the width of the drawable.

    """
    return call_api(ctx, 'Gimp.Drawable.get_width', args=[])

@mcp.tool()
def Gimp_Drawable_has_alpha(ctx: Context) -> str:
    """Returns TRUE if the drawable has an alpha channel.

    """
    return call_api(ctx, 'Gimp.Drawable.has_alpha', args=[])

@mcp.tool()
def Gimp_Drawable_histogram(ctx: Context, channel: str, start_range: float, end_range: float, mean: float, std_dev: float, median: float, pixels: float, count: float, percentile: float) -> str:
    """Returns information on the intensity histogram for the specified drawable.

    :param channel: The channel to query.
    :param start_range: Start of the intensity measurement range.
    :param end_range: End of the intensity measurement range.
    :param mean: Mean intensity value.
    :param std_dev: Standard deviation of intensity values.
    :param median: Median intensity value.
    :param pixels: Alpha-weighted pixel count for entire image.
    :param count: Alpha-weighted pixel count for range.
    :param percentile: Percentile that range falls under.
    """
    return call_api(ctx, 'Gimp.Drawable.histogram', args=[channel, start_range, end_range, mean, std_dev, median, pixels, count, percentile])

@mcp.tool()
def Gimp_Drawable_hue_saturation(ctx: Context, hue_range: str, hue_offset: float, lightness: float, saturation: float, overlap: float) -> str:
    """Modify hue, lightness, and saturation in the specified drawable.

    :param hue_range: Range of affected hues.
    :param hue_offset: Hue offset in degrees.
    :param lightness: Lightness modification.
    :param saturation: Saturation modification.
    :param overlap: Overlap other hue channels.
    """
    return call_api(ctx, 'Gimp.Drawable.hue_saturation', args=[hue_range, hue_offset, lightness, saturation, overlap])

@mcp.tool()
def Gimp_Drawable_invert(ctx: Context, linear: bool) -> str:
    """Invert the contents of the specified drawable.

    :param linear: Whether to invert in linear space.
    """
    return call_api(ctx, 'Gimp.Drawable.invert', args=[linear])

@mcp.tool()
def Gimp_Drawable_is_gray(ctx: Context) -> str:
    """Returns whether the drawable is a grayscale type.

    """
    return call_api(ctx, 'Gimp.Drawable.is_gray', args=[])

@mcp.tool()
def Gimp_Drawable_is_indexed(ctx: Context) -> str:
    """Returns whether the drawable is an indexed type.

    """
    return call_api(ctx, 'Gimp.Drawable.is_indexed', args=[])

@mcp.tool()
def Gimp_Drawable_is_rgb(ctx: Context) -> str:
    """Returns whether the drawable is an RGB type.

    """
    return call_api(ctx, 'Gimp.Drawable.is_rgb', args=[])

@mcp.tool()
def Gimp_Drawable_levels(ctx: Context, channel: str, low_input: float, high_input: float, clamp_input: bool, gamma: float, low_output: float, high_output: float, clamp_output: bool) -> str:
    """Modifies intensity levels in the specified drawable.

    :param channel: The channel to modify.
    :param low_input: Intensity of lowest input.
    :param high_input: Intensity of highest input.
    :param clamp_input: Clamp input values before applying output levels.
    :param gamma: Gamma adjustment factor.
    :param low_output: Intensity of lowest output.
    :param high_output: Intensity of highest output.
    :param clamp_output: Clamp final output values.
    """
    return call_api(ctx, 'Gimp.Drawable.levels', args=[channel, low_input, high_input, clamp_input, gamma, low_output, high_output, clamp_output])

@mcp.tool()
def Gimp_Drawable_levels_stretch(ctx: Context) -> str:
    """Automatically modifies intensity levels in the specified drawable.

    """
    return call_api(ctx, 'Gimp.Drawable.levels_stretch', args=[])

@mcp.tool()
def Gimp_Drawable_mask_bounds(ctx: Context, x1: int, y1: int, x2: int, y2: int) -> str:
    """Find the bounding box of the current selection in relation to the
specified drawable.

    :param x1: X coordinate of the upper left corner of selection bounds.
    :param y1: Y coordinate of the upper left corner of selection bounds.
    :param x2: X coordinate of the lower right corner of selection bounds.
    :param y2: Y coordinate of the lower right corner of selection bounds.
    """
    return call_api(ctx, 'Gimp.Drawable.mask_bounds', args=[x1, y1, x2, y2])

@mcp.tool()
def Gimp_Drawable_mask_intersect(ctx: Context, x: int, y: int, width: int, height: int) -> str:
    """Find the bounding box of the current selection in relation to the
specified drawable.

    :param x: X coordinate of the upper left corner of the intersection.
    :param y: Y coordinate of the upper left corner of the intersection.
    :param width: Width of the intersection.
    :param height: Height of the intersection.
    """
    return call_api(ctx, 'Gimp.Drawable.mask_intersect', args=[x, y, width, height])

@mcp.tool()
def Gimp_Drawable_merge_filter(ctx: Context, filter: str) -> str:
    """This procedure applies the specified drawable effect on drawable
and merge it (therefore before any non-destructive effects are computed).

    :param filter: The drawable filter to merge.
    """
    return call_api(ctx, 'Gimp.Drawable.merge_filter', args=[filter])

@mcp.tool()
def Gimp_Drawable_merge_filters(ctx: Context) -> str:
    """Merge the layer effect filters to the specified drawable.

    """
    return call_api(ctx, 'Gimp.Drawable.merge_filters', args=[])

@mcp.tool()
def Gimp_Drawable_merge_new_filter(ctx: Context, operation_name: str, name: str, mode: str, opacity: float, ...: str = None) -> str:
    """Utility function which combines gimp_drawable_filter_new()
followed by setting arguments for the
GimpDrawableFilterConfig returned by
gimp_drawable_filter_get_config(), and finally applying the
effect to drawable with gimp_drawable_merge_filter()

    :param operation_name: The GEGL operation’s name.
    :param name: The effect name which will show in undo step.
    :param mode: The blend mode.
    :param opacity: The opacity from 0.0 (transparent) to 1.0 (opaque).
    :param ...: A NULL-terminated list of operation argument names
                 and values.
    """
    return call_api(ctx, 'Gimp.Drawable.merge_new_filter', args=[operation_name, name, mode, opacity, ...])

@mcp.tool()
def Gimp_Drawable_merge_shadow(ctx: Context, undo: bool) -> str:
    """Merge the shadow buffer with the specified drawable.

    :param undo: Push merge to undo stack?
    """
    return call_api(ctx, 'Gimp.Drawable.merge_shadow', args=[undo])

@mcp.tool()
def Gimp_Drawable_offset(ctx: Context, wrap_around: bool, fill_type: str, color: str, offset_x: int, offset_y: int) -> str:
    """Offset the drawable by the specified amounts in the X and Y directions

    :param wrap_around: Wrap image around or fill vacated regions.
    :param fill_type: Fill vacated regions of drawable with background or transparent.
    :param color: Fills in the background color when fill_type is set to OFFSET-COLOR.
    :param offset_x: Offset by this amount in X direction.
    :param offset_y: Offset by this amount in Y direction.
    """
    return call_api(ctx, 'Gimp.Drawable.offset', args=[wrap_around, fill_type, color, offset_x, offset_y])

@mcp.tool()
def Gimp_Drawable_posterize(ctx: Context, levels: int) -> str:
    """Posterize the specified drawable.

    :param levels: Levels of posterization.
    """
    return call_api(ctx, 'Gimp.Drawable.posterize', args=[levels])

@mcp.tool()
def Gimp_Drawable_set_pixel(ctx: Context, x_coord: int, y_coord: int, color: str) -> str:
    """Sets the value of the pixel at the specified coordinates.

    :param x_coord: The x coordinate.
    :param y_coord: The y coordinate.
    :param color: The pixel color.
    """
    return call_api(ctx, 'Gimp.Drawable.set_pixel', args=[x_coord, y_coord, color])

@mcp.tool()
def Gimp_Drawable_shadows_highlights(ctx: Context, shadows: float, highlights: float, whitepoint: float, radius: float, compress: float, shadows_ccorrect: float, highlights_ccorrect: float) -> str:
    """Perform shadows and highlights correction.

    :param shadows: Adjust exposure of shadows.
    :param highlights: Adjust exposure of highlights.
    :param whitepoint: Shift white point.
    :param radius: Spatial extent.
    :param compress: Compress the effect on shadows/highlights and preserve midtones.
    :param shadows_ccorrect: Adjust saturation of shadows.
    :param highlights_ccorrect: Adjust saturation of highlights.
    """
    return call_api(ctx, 'Gimp.Drawable.shadows_highlights', args=[shadows, highlights, whitepoint, radius, compress, shadows_ccorrect, highlights_ccorrect])

@mcp.tool()
def Gimp_Drawable_threshold(ctx: Context, channel: str, low_threshold: float, high_threshold: float) -> str:
    """Threshold the specified drawable.

    :param channel: The channel to base the threshold on.
    :param low_threshold: The low threshold value.
    :param high_threshold: The high threshold value.
    """
    return call_api(ctx, 'Gimp.Drawable.threshold', args=[channel, low_threshold, high_threshold])

@mcp.tool()
def Gimp_Drawable_type(ctx: Context) -> str:
    """Returns the drawable’s type.

    """
    return call_api(ctx, 'Gimp.Drawable.type', args=[])

@mcp.tool()
def Gimp_Drawable_type_with_alpha(ctx: Context) -> str:
    """Returns the drawable’s type with alpha.

    """
    return call_api(ctx, 'Gimp.Drawable.type_with_alpha', args=[])

@mcp.tool()
def Gimp_Drawable_update(ctx: Context, x: int, y: int, width: int, height: int) -> str:
    """Update the specified region of the drawable.

    :param x: X coordinate of upper left corner of update region.
    :param y: Y coordinate of upper left corner of update region.
    :param width: Width of update region.
    :param height: Height of update region.
    """
    return call_api(ctx, 'Gimp.Drawable.update', args=[x, y, width, height])

@mcp.tool()
def Gimp_DrawableFilter_delete(ctx: Context) -> str:
    """Delete a drawable filter.

    """
    return call_api(ctx, 'Gimp.DrawableFilter.delete', args=[])

@mcp.tool()
def Gimp_DrawableFilter_get_blend_mode(ctx: Context) -> str:
    """Get the blending mode of the specified filter.

    """
    return call_api(ctx, 'Gimp.DrawableFilter.get_blend_mode', args=[])

@mcp.tool()
def Gimp_DrawableFilter_get_config(ctx: Context) -> str:
    """Get the GimpConfig with properties that match filter‘s arguments.

    """
    return call_api(ctx, 'Gimp.DrawableFilter.get_config', args=[])

@mcp.tool()
def Gimp_DrawableFilter_get_id(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.DrawableFilter.get_id', args=[])

@mcp.tool()
def Gimp_DrawableFilter_get_name(ctx: Context) -> str:
    """Get a drawable filter’s name.

    """
    return call_api(ctx, 'Gimp.DrawableFilter.get_name', args=[])

@mcp.tool()
def Gimp_DrawableFilter_get_opacity(ctx: Context) -> str:
    """Get the opacity of the specified filter.

    """
    return call_api(ctx, 'Gimp.DrawableFilter.get_opacity', args=[])

@mcp.tool()
def Gimp_DrawableFilter_get_operation_name(ctx: Context) -> str:
    """Get a drawable filter’s operation name.

    """
    return call_api(ctx, 'Gimp.DrawableFilter.get_operation_name', args=[])

@mcp.tool()
def Gimp_DrawableFilter_get_visible(ctx: Context) -> str:
    """Get the visibility of the specified filter.

    """
    return call_api(ctx, 'Gimp.DrawableFilter.get_visible', args=[])

@mcp.tool()
def Gimp_DrawableFilter_is_valid(ctx: Context) -> str:
    """Returns TRUE if the drawable_filter is valid.

    """
    return call_api(ctx, 'Gimp.DrawableFilter.is_valid', args=[])

@mcp.tool()
def Gimp_DrawableFilter_set_aux_input(ctx: Context, input_pad_name: str, input: str) -> str:
    """When a filter has one or several auxiliary inputs, you can use this
function to set them.

    :param input_pad_name: Name of the filter’s input pad.
    :param input: The drawable to use as auxiliary input.
    """
    return call_api(ctx, 'Gimp.DrawableFilter.set_aux_input', args=[input_pad_name, input])

@mcp.tool()
def Gimp_DrawableFilter_set_blend_mode(ctx: Context, mode: str) -> str:
    """This procedure sets the blend mode of filter.

    :param mode: Blend mode.
    """
    return call_api(ctx, 'Gimp.DrawableFilter.set_blend_mode', args=[mode])

@mcp.tool()
def Gimp_DrawableFilter_set_opacity(ctx: Context, opacity: float) -> str:
    """This procedure sets the opacity of filter on a range from 0.0
(transparent) to 1.0 (opaque).

    :param opacity: The opacity.
    """
    return call_api(ctx, 'Gimp.DrawableFilter.set_opacity', args=[opacity])

@mcp.tool()
def Gimp_DrawableFilter_set_visible(ctx: Context, visible: bool) -> str:
    """Set the visibility of the specified filter.

    :param visible: The new filter visibility.
    """
    return call_api(ctx, 'Gimp.DrawableFilter.set_visible', args=[visible])

@mcp.tool()
def Gimp_DrawableFilter_update(ctx: Context) -> str:
    """Syncs the GimpConfig with properties that match filter‘s arguments.
This procedure updates the settings of the specified filter all at
once, including the arguments of the GimpDrawableFilterConfig
obtained with gimp_drawable_filter_get_config() as well as the
blend mode and opacity.

    """
    return call_api(ctx, 'Gimp.DrawableFilter.update', args=[])

@mcp.tool()
def Gimp_ExportOptions_get_image(ctx: Context, image: str) -> str:
    """Takes an image to be exported, possibly creating a temporary copy
modified according to export settings in options (such as the
capabilities of the export format).

    :param image: The image.
    """
    return call_api(ctx, 'Gimp.ExportOptions.get_image', args=[image])

@mcp.tool()
def Gimp_ExportProcedure_get_support_comment(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.ExportProcedure.get_support_comment', args=[])

@mcp.tool()
def Gimp_ExportProcedure_get_support_exif(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.ExportProcedure.get_support_exif', args=[])

@mcp.tool()
def Gimp_ExportProcedure_get_support_iptc(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.ExportProcedure.get_support_iptc', args=[])

@mcp.tool()
def Gimp_ExportProcedure_get_support_profile(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.ExportProcedure.get_support_profile', args=[])

@mcp.tool()
def Gimp_ExportProcedure_get_support_thumbnail(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.ExportProcedure.get_support_thumbnail', args=[])

@mcp.tool()
def Gimp_ExportProcedure_get_support_xmp(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.ExportProcedure.get_support_xmp', args=[])

@mcp.tool()
def Gimp_ExportProcedure_set_capabilities(ctx: Context, capabilities: str, get_capabilities_func: str = None, get_capabilities_data: str = None, get_capabilities_data_destroy: str = None) -> str:
    """Sets default GimpExportCapabilities for image export.

    :param capabilities: A GimpExportCapabilities bitfield.
    :param get_capabilities_func: Callback function to update export options.
    :param get_capabilities_data: Data for get_capabilities_func.
    :param get_capabilities_data_destroy: Free function for get_capabilities_data, or NULL.
    """
    return call_api(ctx, 'Gimp.ExportProcedure.set_capabilities', args=[capabilities, get_capabilities_func, get_capabilities_data, get_capabilities_data_destroy])

@mcp.tool()
def Gimp_ExportProcedure_set_support_comment(ctx: Context, supports: bool) -> str:
    """Determine whether procedure supports exporting a comment. By default,
it won’t (so there is usually no reason to run this function with
FALSE).

    :param supports: Whether a comment can be stored.
    """
    return call_api(ctx, 'Gimp.ExportProcedure.set_support_comment', args=[supports])

@mcp.tool()
def Gimp_ExportProcedure_set_support_exif(ctx: Context, supports: bool) -> str:
    """Determine whether procedure supports exporting Exif data. By default,
it won’t (so there is usually no reason to run this function with
FALSE).

    :param supports: Whether Exif metadata are supported.
    """
    return call_api(ctx, 'Gimp.ExportProcedure.set_support_exif', args=[supports])

@mcp.tool()
def Gimp_ExportProcedure_set_support_iptc(ctx: Context, supports: bool) -> str:
    """Determine whether procedure supports exporting IPTC data. By default,
it won’t (so there is usually no reason to run this function with
FALSE).

    :param supports: Whether IPTC metadata are supported.
    """
    return call_api(ctx, 'Gimp.ExportProcedure.set_support_iptc', args=[supports])

@mcp.tool()
def Gimp_ExportProcedure_set_support_profile(ctx: Context, supports: bool) -> str:
    """Determine whether procedure supports exporting ICC color profiles. By
default, it won’t (so there is usually no reason to run this function
with FALSE).

    :param supports: Whether color profiles can be stored.
    """
    return call_api(ctx, 'Gimp.ExportProcedure.set_support_profile', args=[supports])

@mcp.tool()
def Gimp_ExportProcedure_set_support_thumbnail(ctx: Context, supports: bool) -> str:
    """Determine whether procedure supports exporting a thumbnail. By default,
it won’t (so there is usually no reason to run this function with
FALSE).

    :param supports: Whether a thumbnail can be stored.
    """
    return call_api(ctx, 'Gimp.ExportProcedure.set_support_thumbnail', args=[supports])

@mcp.tool()
def Gimp_ExportProcedure_set_support_xmp(ctx: Context, supports: bool) -> str:
    """Determine whether procedure supports exporting XMP data. By default,
it won’t (so there is usually no reason to run this function with
FALSE).

    :param supports: Whether XMP metadata are supported.
    """
    return call_api(ctx, 'Gimp.ExportProcedure.set_support_xmp', args=[supports])

@mcp.tool()
def Gimp_FileProcedure_get_extensions(ctx: Context) -> str:
    """Returns the procedure’s extensions as set with
gimp_file_procedure_set_extensions().

    """
    return call_api(ctx, 'Gimp.FileProcedure.get_extensions', args=[])

@mcp.tool()
def Gimp_FileProcedure_get_format_name(ctx: Context) -> str:
    """Returns the procedure’s format name, as set with
gimp_file_procedure_set_format_name().

    """
    return call_api(ctx, 'Gimp.FileProcedure.get_format_name', args=[])

@mcp.tool()
def Gimp_FileProcedure_get_handles_remote(ctx: Context) -> str:
    """Returns the procedure’s ‘handles remote’ flags as set with
gimp_file_procedure_set_handles_remote().

    """
    return call_api(ctx, 'Gimp.FileProcedure.get_handles_remote', args=[])

@mcp.tool()
def Gimp_FileProcedure_get_magics(ctx: Context) -> str:
    """Returns the procedure’s magics as set with gimp_file_procedure_set_magics().

    """
    return call_api(ctx, 'Gimp.FileProcedure.get_magics', args=[])

@mcp.tool()
def Gimp_FileProcedure_get_mime_types(ctx: Context) -> str:
    """Returns the procedure’s mime-type as set with
gimp_file_procedure_set_mime_types().

    """
    return call_api(ctx, 'Gimp.FileProcedure.get_mime_types', args=[])

@mcp.tool()
def Gimp_FileProcedure_get_prefixes(ctx: Context) -> str:
    """Returns the procedure’s prefixes as set with
gimp_file_procedure_set_prefixes().

    """
    return call_api(ctx, 'Gimp.FileProcedure.get_prefixes', args=[])

@mcp.tool()
def Gimp_FileProcedure_get_priority(ctx: Context) -> str:
    """Returns the procedure’s priority as set with
gimp_file_procedure_set_priority().

    """
    return call_api(ctx, 'Gimp.FileProcedure.get_priority', args=[])

@mcp.tool()
def Gimp_FileProcedure_set_extensions(ctx: Context, extensions: str) -> str:
    """Registers the given list of extensions as something this procedure can handle.

    :param extensions: A comma separated list of extensions this procedure can
             handle (i.e. “jpg,jpeg”).
    """
    return call_api(ctx, 'Gimp.FileProcedure.set_extensions', args=[extensions])

@mcp.tool()
def Gimp_FileProcedure_set_format_name(ctx: Context, format_name: str) -> str:
    """Associates a format name with a file handler procedure.

    :param format_name: A public-facing name for the format, e.g. “PNG”.
    """
    return call_api(ctx, 'Gimp.FileProcedure.set_format_name', args=[format_name])

@mcp.tool()
def Gimp_FileProcedure_set_handles_remote(ctx: Context, handles_remote: bool) -> str:
    """Registers a file procedure as capable of handling arbitrary remote
URIs via GIO.

    :param handles_remote: The procedure’s ‘handles remote’ flag.
    """
    return call_api(ctx, 'Gimp.FileProcedure.set_handles_remote', args=[handles_remote])

@mcp.tool()
def Gimp_FileProcedure_set_magics(ctx: Context, magics: str) -> str:
    """Registers the list of magic file information this procedure can handle.

    :param magics: A comma-separated list of magic file information (i.e. “0,string,GIF”).
    """
    return call_api(ctx, 'Gimp.FileProcedure.set_magics', args=[magics])

@mcp.tool()
def Gimp_FileProcedure_set_mime_types(ctx: Context, mime_types: str) -> str:
    """Associates MIME types with a file handler procedure.

    :param mime_types: A comma-separated list of MIME types, such as “image/jpeg”.
    """
    return call_api(ctx, 'Gimp.FileProcedure.set_mime_types', args=[mime_types])

@mcp.tool()
def Gimp_FileProcedure_set_prefixes(ctx: Context, prefixes: str) -> str:
    """It should almost never be necessary to register prefixes with file
procedures, because most sorts of URIs should be handled by GIO.

    :param prefixes: A comma separated list of prefixes this procedure can
            handle (i.e. “http:,ftp:”).
    """
    return call_api(ctx, 'Gimp.FileProcedure.set_prefixes', args=[prefixes])

@mcp.tool()
def Gimp_FileProcedure_set_priority(ctx: Context, priority: int) -> str:
    """Sets the priority of a file handler procedure.

    :param priority: The procedure’s priority.
    """
    return call_api(ctx, 'Gimp.FileProcedure.set_priority', args=[priority])

@mcp.tool()
def Gimp_Font_get_pango_font_description(ctx: Context) -> str:
    """Returns a PangoFontDescription representing font.

    """
    return call_api(ctx, 'Gimp.Font.get_pango_font_description', args=[])

@mcp.tool()
def Gimp_Gradient_get_custom_samples(ctx: Context, num_samples: int, positions: str, reverse: bool) -> str:
    """Sample the gradient in custom positions.

    :param num_samples: The number of samples to take.
    :param positions: The list of positions to sample along the gradient.
    :param reverse: Use the reverse gradient.
    """
    return call_api(ctx, 'Gimp.Gradient.get_custom_samples', args=[num_samples, positions, reverse])

@mcp.tool()
def Gimp_Gradient_get_number_of_segments(ctx: Context) -> str:
    """Gets the number of segments of the gradient

    """
    return call_api(ctx, 'Gimp.Gradient.get_number_of_segments', args=[])

@mcp.tool()
def Gimp_Gradient_get_uniform_samples(ctx: Context, num_samples: int, reverse: bool) -> str:
    """Sample the gradient in uniform parts.

    :param num_samples: The number of samples to take.
    :param reverse: Use the reverse gradient.
    """
    return call_api(ctx, 'Gimp.Gradient.get_uniform_samples', args=[num_samples, reverse])

@mcp.tool()
def Gimp_Gradient_segment_get_blending_function(ctx: Context, segment: int, blend_func: str) -> str:
    """Gets the gradient segment’s blending function

    :param segment: The index of a segment within the gradient.
    :param blend_func: The blending function of the segment.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_get_blending_function', args=[segment, blend_func])

@mcp.tool()
def Gimp_Gradient_segment_get_coloring_type(ctx: Context, segment: int, coloring_type: str) -> str:
    """Gets the gradient segment’s coloring type

    :param segment: The index of a segment within the gradient.
    :param coloring_type: The coloring type of the segment.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_get_coloring_type', args=[segment, coloring_type])

@mcp.tool()
def Gimp_Gradient_segment_get_left_color(ctx: Context, segment: int) -> str:
    """Gets the left endpoint color of the segment

    :param segment: The index of a segment within the gradient.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_get_left_color', args=[segment])

@mcp.tool()
def Gimp_Gradient_segment_get_left_pos(ctx: Context, segment: int, pos: float) -> str:
    """Gets the left endpoint position of a segment

    :param segment: The index of a segment within the gradient.
    :param pos: The return position.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_get_left_pos', args=[segment, pos])

@mcp.tool()
def Gimp_Gradient_segment_get_middle_pos(ctx: Context, segment: int, pos: float) -> str:
    """Gets the midpoint position of the segment

    :param segment: The index of a segment within the gradient.
    :param pos: The return position.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_get_middle_pos', args=[segment, pos])

@mcp.tool()
def Gimp_Gradient_segment_get_right_color(ctx: Context, segment: int) -> str:
    """Gets the right endpoint color of the segment

    :param segment: The index of a segment within the gradient.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_get_right_color', args=[segment])

@mcp.tool()
def Gimp_Gradient_segment_get_right_pos(ctx: Context, segment: int, pos: float) -> str:
    """Gets the right endpoint position of the segment

    :param segment: The index of a segment within the gradient.
    :param pos: The return position.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_get_right_pos', args=[segment, pos])

@mcp.tool()
def Gimp_Gradient_segment_range_blend_colors(ctx: Context, start_segment: int, end_segment: int) -> str:
    """Blend the colors of the segment range.

    :param start_segment: Index of the first segment to operate on.
    :param end_segment: Index of the last segment to operate on. If negative, the range will extend to the end segment.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_range_blend_colors', args=[start_segment, end_segment])

@mcp.tool()
def Gimp_Gradient_segment_range_blend_opacity(ctx: Context, start_segment: int, end_segment: int) -> str:
    """Blend the opacity of the segment range.

    :param start_segment: Index of the first segment to operate on.
    :param end_segment: Index of the last segment to operate on. If negative, the range will extend to the end segment.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_range_blend_opacity', args=[start_segment, end_segment])

@mcp.tool()
def Gimp_Gradient_segment_range_delete(ctx: Context, start_segment: int, end_segment: int) -> str:
    """Delete the segment range

    :param start_segment: Index of the first segment to operate on.
    :param end_segment: Index of the last segment to operate on. If negative, the range will extend to the end segment.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_range_delete', args=[start_segment, end_segment])

@mcp.tool()
def Gimp_Gradient_segment_range_flip(ctx: Context, start_segment: int, end_segment: int) -> str:
    """Flip the segment range

    :param start_segment: Index of the first segment to operate on.
    :param end_segment: Index of the last segment to operate on. If negative, the range will extend to the end segment.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_range_flip', args=[start_segment, end_segment])

@mcp.tool()
def Gimp_Gradient_segment_range_move(ctx: Context, start_segment: int, end_segment: int, delta: float, control_compress: bool) -> str:
    """Move the position of an entire segment range by a delta.

    :param start_segment: Index of the first segment to operate on.
    :param end_segment: Index of the last segment to operate on. If negative, the range will extend to the end segment.
    :param delta: The delta to move the segment range.
    :param control_compress: Whether or not to compress the neighboring segments.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_range_move', args=[start_segment, end_segment, delta, control_compress])

@mcp.tool()
def Gimp_Gradient_segment_range_redistribute_handles(ctx: Context, start_segment: int, end_segment: int) -> str:
    """Uniformly redistribute the segment range’s handles

    :param start_segment: Index of the first segment to operate on.
    :param end_segment: Index of the last segment to operate on. If negative, the range will extend to the end segment.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_range_redistribute_handles', args=[start_segment, end_segment])

@mcp.tool()
def Gimp_Gradient_segment_range_replicate(ctx: Context, start_segment: int, end_segment: int, replicate_times: int) -> str:
    """Replicate the segment range

    :param start_segment: Index of the first segment to operate on.
    :param end_segment: Index of the last segment to operate on. If negative, the range will extend to the end segment.
    :param replicate_times: The number of replicas for each segment.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_range_replicate', args=[start_segment, end_segment, replicate_times])

@mcp.tool()
def Gimp_Gradient_segment_range_set_blending_function(ctx: Context, start_segment: int, end_segment: int, blending_function: str) -> str:
    """Sets the blending function of a range of segments

    :param start_segment: Index of the first segment to operate on.
    :param end_segment: Index of the last segment to operate on. If negative, the range will extend to the end segment.
    :param blending_function: The blending function.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_range_set_blending_function', args=[start_segment, end_segment, blending_function])

@mcp.tool()
def Gimp_Gradient_segment_range_set_coloring_type(ctx: Context, start_segment: int, end_segment: int, coloring_type: str) -> str:
    """Sets the coloring type of a range of segments

    :param start_segment: Index of the first segment to operate on.
    :param end_segment: Index of the last segment to operate on. If negative, the range will extend to the end segment.
    :param coloring_type: The coloring type.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_range_set_coloring_type', args=[start_segment, end_segment, coloring_type])

@mcp.tool()
def Gimp_Gradient_segment_range_split_midpoint(ctx: Context, start_segment: int, end_segment: int) -> str:
    """Splits each segment in the segment range at midpoint

    :param start_segment: Index of the first segment to operate on.
    :param end_segment: Index of the last segment to operate on. If negative, the range will extend to the end segment.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_range_split_midpoint', args=[start_segment, end_segment])

@mcp.tool()
def Gimp_Gradient_segment_range_split_uniform(ctx: Context, start_segment: int, end_segment: int, split_parts: int) -> str:
    """Splits each segment in the segment range uniformly

    :param start_segment: Index of the first segment to operate on.
    :param end_segment: Index of the last segment to operate on. If negative, the range will extend to the end segment.
    :param split_parts: The number of uniform divisions to split each segment to.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_range_split_uniform', args=[start_segment, end_segment, split_parts])

@mcp.tool()
def Gimp_Gradient_segment_set_left_color(ctx: Context, segment: int, color: str) -> str:
    """Sets the left endpoint color of a segment

    :param segment: The index of a segment within the gradient.
    :param color: The color to set.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_set_left_color', args=[segment, color])

@mcp.tool()
def Gimp_Gradient_segment_set_left_pos(ctx: Context, segment: int, pos: float, final_pos: float) -> str:
    """Sets the left endpoint position of the segment

    :param segment: The index of a segment within the gradient.
    :param pos: The position to set the guidepoint to.
    :param final_pos: The return position.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_set_left_pos', args=[segment, pos, final_pos])

@mcp.tool()
def Gimp_Gradient_segment_set_middle_pos(ctx: Context, segment: int, pos: float, final_pos: float) -> str:
    """Sets the midpoint position of the segment

    :param segment: The index of a segment within the gradient.
    :param pos: The position to set the guidepoint to.
    :param final_pos: The return position.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_set_middle_pos', args=[segment, pos, final_pos])

@mcp.tool()
def Gimp_Gradient_segment_set_right_color(ctx: Context, segment: int, color: str) -> str:
    """Sets the right endpoint color of the segment

    :param segment: The index of a segment within the gradient.
    :param color: The color to set.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_set_right_color', args=[segment, color])

@mcp.tool()
def Gimp_Gradient_segment_set_right_pos(ctx: Context, segment: int, pos: float, final_pos: float) -> str:
    """Sets the right endpoint position of the segment

    :param segment: The index of a segment within the gradient.
    :param pos: The position to set the right endpoint to.
    :param final_pos: The return position.
    """
    return call_api(ctx, 'Gimp.Gradient.segment_set_right_pos', args=[segment, pos, final_pos])

@mcp.tool()
def Gimp_GroupLayer_merge(ctx: Context) -> str:
    """Merge the passed group layer’s layers into one normal layer.

    """
    return call_api(ctx, 'Gimp.GroupLayer.merge', args=[])

@mcp.tool()
def Gimp_Image_add_hguide(ctx: Context, yposition: int) -> str:
    """Add a horizontal guide to an image.

    :param yposition: The guide’s y-offset from top of image.
    """
    return call_api(ctx, 'Gimp.Image.add_hguide', args=[yposition])

@mcp.tool()
def Gimp_Image_add_sample_point(ctx: Context, position_x: int, position_y: int) -> str:
    """Add a sample point to an image.

    :param position_x: The sample point’s x-offset from left of image.
    :param position_y: The sample point’s y-offset from top of image.
    """
    return call_api(ctx, 'Gimp.Image.add_sample_point', args=[position_x, position_y])

@mcp.tool()
def Gimp_Image_add_vguide(ctx: Context, xposition: int) -> str:
    """Add a vertical guide to an image.

    :param xposition: The guide’s x-offset from left of image.
    """
    return call_api(ctx, 'Gimp.Image.add_vguide', args=[xposition])

@mcp.tool()
def Gimp_Image_attach_parasite(ctx: Context, parasite: str) -> str:
    """Add a parasite to an image.

    :param parasite: The parasite to attach to an image.
    """
    return call_api(ctx, 'Gimp.Image.attach_parasite', args=[parasite])

@mcp.tool()
def Gimp_Image_autocrop(ctx: Context, drawable: str = None) -> str:
    """Remove empty borders from the image

    :param drawable: Input drawable.
    """
    return call_api(ctx, 'Gimp.Image.autocrop', args=[drawable])

@mcp.tool()
def Gimp_Image_autocrop_selected_layers(ctx: Context, drawable: str = None) -> str:
    """Crop the selected layers based on empty borders of the input drawable

    :param drawable: Input drawable.
    """
    return call_api(ctx, 'Gimp.Image.autocrop_selected_layers', args=[drawable])

@mcp.tool()
def Gimp_Image_clean_all(ctx: Context) -> str:
    """Set the image dirty count to 0.

    """
    return call_api(ctx, 'Gimp.Image.clean_all', args=[])

@mcp.tool()
def Gimp_Image_convert_color_profile(ctx: Context, profile: str, intent: str, bpc: bool) -> str:
    """Convert the image’s layers to a color profile

    :param profile: The color profile to convert to.
    :param intent: Rendering intent.
    :param bpc: Black point compensation.
    """
    return call_api(ctx, 'Gimp.Image.convert_color_profile', args=[profile, intent, bpc])

@mcp.tool()
def Gimp_Image_convert_color_profile_from_file(ctx: Context, file: str, intent: str, bpc: bool) -> str:
    """Convert the image’s layers to a color profile

    :param file: The file containing the new color profile.
    :param intent: Rendering intent.
    :param bpc: Black point compensation.
    """
    return call_api(ctx, 'Gimp.Image.convert_color_profile_from_file', args=[file, intent, bpc])

@mcp.tool()
def Gimp_Image_convert_grayscale(ctx: Context) -> str:
    """Convert specified image to grayscale

    """
    return call_api(ctx, 'Gimp.Image.convert_grayscale', args=[])

@mcp.tool()
def Gimp_Image_convert_indexed(ctx: Context, dither_type: str, palette_type: str, num_cols: int, alpha_dither: bool, remove_unused: bool, palette: str) -> str:
    """Convert specified image to and Indexed image

    :param dither_type: The dither type to use.
    :param palette_type: The type of palette to use.
    :param num_cols: The number of colors to quantize to, ignored unless (palette_type == GIMP_CONVERT_PALETTE_GENERATE).
    :param alpha_dither: Dither transparency to fake partial opacity.
    :param remove_unused: Remove unused or duplicate color entries from final palette, ignored if (palette_type == GIMP_CONVERT_PALETTE_GENERATE).
    :param palette: The name of the custom palette to use, ignored unless (palette_type == GIMP_CONVERT_PALETTE_CUSTOM).
    """
    return call_api(ctx, 'Gimp.Image.convert_indexed', args=[dither_type, palette_type, num_cols, alpha_dither, remove_unused, palette])

@mcp.tool()
def Gimp_Image_convert_precision(ctx: Context, precision: str) -> str:
    """Convert the image to the specified precision

    :param precision: The new precision.
    """
    return call_api(ctx, 'Gimp.Image.convert_precision', args=[precision])

@mcp.tool()
def Gimp_Image_convert_rgb(ctx: Context) -> str:
    """Convert specified image to RGB color

    """
    return call_api(ctx, 'Gimp.Image.convert_rgb', args=[])

@mcp.tool()
def Gimp_Image_crop(ctx: Context, new_width: int, new_height: int, offx: int, offy: int) -> str:
    """Crop the image to the specified extents.

    :param new_width: New image width: (0 < new_width <= width).
    :param new_height: New image height: (0 < new_height <= height).
    :param offx: X offset: (0 <= offx <= (width - new_width)).
    :param offy: Y offset: (0 <= offy <= (height - new_height)).
    """
    return call_api(ctx, 'Gimp.Image.crop', args=[new_width, new_height, offx, offy])

@mcp.tool()
def Gimp_Image_delete(ctx: Context) -> str:
    """Delete the specified image.

    """
    return call_api(ctx, 'Gimp.Image.delete', args=[])

@mcp.tool()
def Gimp_Image_delete_guide(ctx: Context, guide: int) -> str:
    """Deletes a guide from an image.

    :param guide: The ID of the guide to be removed.
    """
    return call_api(ctx, 'Gimp.Image.delete_guide', args=[guide])

@mcp.tool()
def Gimp_Image_delete_sample_point(ctx: Context, sample_point: int) -> str:
    """Deletes a sample point from an image.

    :param sample_point: The ID of the sample point to be removed.
    """
    return call_api(ctx, 'Gimp.Image.delete_sample_point', args=[sample_point])

@mcp.tool()
def Gimp_Image_detach_parasite(ctx: Context, name: str) -> str:
    """Removes a parasite from an image.

    :param name: The name of the parasite to detach from an image.
    """
    return call_api(ctx, 'Gimp.Image.detach_parasite', args=[name])

@mcp.tool()
def Gimp_Image_duplicate(ctx: Context) -> str:
    """Duplicate the specified image

    """
    return call_api(ctx, 'Gimp.Image.duplicate', args=[])

@mcp.tool()
def Gimp_Image_export_path_to_file(ctx: Context, file: str, path: str = None) -> str:
    """Save a path as an SVG file.

    :param file: The SVG file to create.
    :param path: The path object to export, or NULL for all in the image.
    """
    return call_api(ctx, 'Gimp.Image.export_path_to_file', args=[file, path])

@mcp.tool()
def Gimp_Image_export_path_to_string(ctx: Context, path: str = None) -> str:
    """Save a path as an SVG string.

    :param path: The path object to export, or NULL for all in the image.
    """
    return call_api(ctx, 'Gimp.Image.export_path_to_string', args=[path])

@mcp.tool()
def Gimp_Image_find_next_guide(ctx: Context, guide: int) -> str:
    """Find next guide on an image.

    :param guide: The ID of the current guide (0 if first invocation).
    """
    return call_api(ctx, 'Gimp.Image.find_next_guide', args=[guide])

@mcp.tool()
def Gimp_Image_find_next_sample_point(ctx: Context, sample_point: int) -> str:
    """Find next sample point on an image.

    :param sample_point: The ID of the current sample point (0 if first invocation).
    """
    return call_api(ctx, 'Gimp.Image.find_next_sample_point', args=[sample_point])

@mcp.tool()
def Gimp_Image_flatten(ctx: Context) -> str:
    """Flatten all visible layers into a single layer. Discard all
invisible layers.

    """
    return call_api(ctx, 'Gimp.Image.flatten', args=[])

@mcp.tool()
def Gimp_Image_flip(ctx: Context, flip_type: str) -> str:
    """Flips the image horizontally or vertically.

    :param flip_type: Type of flip.
    """
    return call_api(ctx, 'Gimp.Image.flip', args=[flip_type])

@mcp.tool()
def Gimp_Image_floating_sel_attached_to(ctx: Context) -> str:
    """Return the drawable the floating selection is attached to.

    """
    return call_api(ctx, 'Gimp.Image.floating_sel_attached_to', args=[])

@mcp.tool()
def Gimp_Image_freeze_channels(ctx: Context) -> str:
    """Freeze the image’s channel list.

    """
    return call_api(ctx, 'Gimp.Image.freeze_channels', args=[])

@mcp.tool()
def Gimp_Image_freeze_layers(ctx: Context) -> str:
    """Freeze the image’s layer list.

    """
    return call_api(ctx, 'Gimp.Image.freeze_layers', args=[])

@mcp.tool()
def Gimp_Image_freeze_paths(ctx: Context) -> str:
    """Freeze the image’s path list.

    """
    return call_api(ctx, 'Gimp.Image.freeze_paths', args=[])

@mcp.tool()
def Gimp_Image_get_base_type(ctx: Context) -> str:
    """Get the base type of the image.

    """
    return call_api(ctx, 'Gimp.Image.get_base_type', args=[])

@mcp.tool()
def Gimp_Image_get_channel_by_name(ctx: Context, name: str) -> str:
    """Find a channel with a given name in an image.

    :param name: The name of the channel to find.
    """
    return call_api(ctx, 'Gimp.Image.get_channel_by_name', args=[name])

@mcp.tool()
def Gimp_Image_get_channel_by_tattoo(ctx: Context, tattoo: int) -> str:
    """Find a channel with a given tattoo in an image.

    :param tattoo: The tattoo of the channel to find.
    """
    return call_api(ctx, 'Gimp.Image.get_channel_by_tattoo', args=[tattoo])

@mcp.tool()
def Gimp_Image_get_channels(ctx: Context) -> str:
    """Returns the list of channels contained in the specified image.

    """
    return call_api(ctx, 'Gimp.Image.get_channels', args=[])

@mcp.tool()
def Gimp_Image_get_color_profile(ctx: Context) -> str:
    """Returns the image’s color profile

    """
    return call_api(ctx, 'Gimp.Image.get_color_profile', args=[])

@mcp.tool()
def Gimp_Image_get_component_active(ctx: Context, component: str) -> str:
    """Returns if the specified image’s image component is active.

    :param component: The image component.
    """
    return call_api(ctx, 'Gimp.Image.get_component_active', args=[component])

@mcp.tool()
def Gimp_Image_get_component_visible(ctx: Context, component: str) -> str:
    """Returns if the specified image’s image component is visible.

    :param component: The image component.
    """
    return call_api(ctx, 'Gimp.Image.get_component_visible', args=[component])

@mcp.tool()
def Gimp_Image_get_default_new_layer_mode(ctx: Context) -> str:
    """Get the default mode for newly created layers of this image.

    """
    return call_api(ctx, 'Gimp.Image.get_default_new_layer_mode', args=[])

@mcp.tool()
def Gimp_Image_get_effective_color_profile(ctx: Context) -> str:
    """Returns the color profile that is used for the image.

    """
    return call_api(ctx, 'Gimp.Image.get_effective_color_profile', args=[])

@mcp.tool()
def Gimp_Image_get_exported_file(ctx: Context) -> str:
    """Returns the exported file for the specified image.

    """
    return call_api(ctx, 'Gimp.Image.get_exported_file', args=[])

@mcp.tool()
def Gimp_Image_get_file(ctx: Context) -> str:
    """Returns the file for the specified image.

    """
    return call_api(ctx, 'Gimp.Image.get_file', args=[])

@mcp.tool()
def Gimp_Image_get_floating_sel(ctx: Context) -> str:
    """Return the floating selection of the image.

    """
    return call_api(ctx, 'Gimp.Image.get_floating_sel', args=[])

@mcp.tool()
def Gimp_Image_get_guide_orientation(ctx: Context, guide: int) -> str:
    """Get orientation of a guide on an image.

    :param guide: The guide.
    """
    return call_api(ctx, 'Gimp.Image.get_guide_orientation', args=[guide])

@mcp.tool()
def Gimp_Image_get_guide_position(ctx: Context, guide: int) -> str:
    """Get position of a guide on an image.

    :param guide: The guide.
    """
    return call_api(ctx, 'Gimp.Image.get_guide_position', args=[guide])

@mcp.tool()
def Gimp_Image_get_height(ctx: Context) -> str:
    """Return the height of the image

    """
    return call_api(ctx, 'Gimp.Image.get_height', args=[])

@mcp.tool()
def Gimp_Image_get_id(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.Image.get_id', args=[])

@mcp.tool()
def Gimp_Image_get_imported_file(ctx: Context) -> str:
    """Returns the imported file for the specified image.

    """
    return call_api(ctx, 'Gimp.Image.get_imported_file', args=[])

@mcp.tool()
def Gimp_Image_get_item_position(ctx: Context, item: str) -> str:
    """Returns the position of the item in its level of its item tree.

    :param item: The item.
    """
    return call_api(ctx, 'Gimp.Image.get_item_position', args=[item])

@mcp.tool()
def Gimp_Image_get_layer_by_name(ctx: Context, name: str) -> str:
    """Find a layer with a given name in an image.

    :param name: The name of the layer to find.
    """
    return call_api(ctx, 'Gimp.Image.get_layer_by_name', args=[name])

@mcp.tool()
def Gimp_Image_get_layer_by_tattoo(ctx: Context, tattoo: int) -> str:
    """Find a layer with a given tattoo in an image.

    :param tattoo: The tattoo of the layer to find.
    """
    return call_api(ctx, 'Gimp.Image.get_layer_by_tattoo', args=[tattoo])

@mcp.tool()
def Gimp_Image_get_layers(ctx: Context) -> str:
    """Returns the list of root layers contained in the specified image.

    """
    return call_api(ctx, 'Gimp.Image.get_layers', args=[])

@mcp.tool()
def Gimp_Image_get_metadata(ctx: Context) -> str:
    """Returns the image’s metadata.

    """
    return call_api(ctx, 'Gimp.Image.get_metadata', args=[])

@mcp.tool()
def Gimp_Image_get_name(ctx: Context) -> str:
    """Returns the specified image’s name.

    """
    return call_api(ctx, 'Gimp.Image.get_name', args=[])

@mcp.tool()
def Gimp_Image_get_palette(ctx: Context) -> str:
    """Returns the image’s colormap

    """
    return call_api(ctx, 'Gimp.Image.get_palette', args=[])

@mcp.tool()
def Gimp_Image_get_parasite(ctx: Context, name: str) -> str:
    """Look up a parasite in an image

    :param name: The name of the parasite to find.
    """
    return call_api(ctx, 'Gimp.Image.get_parasite', args=[name])

@mcp.tool()
def Gimp_Image_get_parasite_list(ctx: Context) -> str:
    """List all parasites.

    """
    return call_api(ctx, 'Gimp.Image.get_parasite_list', args=[])

@mcp.tool()
def Gimp_Image_get_path_by_name(ctx: Context, name: str) -> str:
    """Find a path with a given name in an image.

    :param name: The name of the path to find.
    """
    return call_api(ctx, 'Gimp.Image.get_path_by_name', args=[name])

@mcp.tool()
def Gimp_Image_get_path_by_tattoo(ctx: Context, tattoo: int) -> str:
    """Find a path with a given tattoo in an image.

    :param tattoo: The tattoo of the path to find.
    """
    return call_api(ctx, 'Gimp.Image.get_path_by_tattoo', args=[tattoo])

@mcp.tool()
def Gimp_Image_get_paths(ctx: Context) -> str:
    """Returns the list of paths contained in the specified image.

    """
    return call_api(ctx, 'Gimp.Image.get_paths', args=[])

@mcp.tool()
def Gimp_Image_get_precision(ctx: Context) -> str:
    """Get the precision of the image.

    """
    return call_api(ctx, 'Gimp.Image.get_precision', args=[])

@mcp.tool()
def Gimp_Image_get_resolution(ctx: Context, xresolution: float, yresolution: float) -> str:
    """Returns the specified image’s resolution.

    :param xresolution: The resolution in the x-axis, in dots per inch.
    :param yresolution: The resolution in the y-axis, in dots per inch.
    """
    return call_api(ctx, 'Gimp.Image.get_resolution', args=[xresolution, yresolution])

@mcp.tool()
def Gimp_Image_get_sample_point_position(ctx: Context, sample_point: int, position_y: int) -> str:
    """Get position of a sample point on an image.

    :param sample_point: The guide.
    :param position_y: The sample point’s y-offset relative to top of image.
    """
    return call_api(ctx, 'Gimp.Image.get_sample_point_position', args=[sample_point, position_y])

@mcp.tool()
def Gimp_Image_get_selected_channels(ctx: Context) -> str:
    """Returns the specified image’s selected channels.

    """
    return call_api(ctx, 'Gimp.Image.get_selected_channels', args=[])

@mcp.tool()
def Gimp_Image_get_selected_drawables(ctx: Context) -> str:
    """Get the image’s selected drawables

    """
    return call_api(ctx, 'Gimp.Image.get_selected_drawables', args=[])

@mcp.tool()
def Gimp_Image_get_selected_layers(ctx: Context) -> str:
    """Returns the specified image’s selected layers.

    """
    return call_api(ctx, 'Gimp.Image.get_selected_layers', args=[])

@mcp.tool()
def Gimp_Image_get_selected_paths(ctx: Context) -> str:
    """Returns the specified image’s selected paths.

    """
    return call_api(ctx, 'Gimp.Image.get_selected_paths', args=[])

@mcp.tool()
def Gimp_Image_get_selection(ctx: Context) -> str:
    """Returns the specified image’s selection.

    """
    return call_api(ctx, 'Gimp.Image.get_selection', args=[])

@mcp.tool()
def Gimp_Image_get_simulation_bpc(ctx: Context) -> str:
    """Returns whether the image has Black Point Compensation enabled for
its simulation

    """
    return call_api(ctx, 'Gimp.Image.get_simulation_bpc', args=[])

@mcp.tool()
def Gimp_Image_get_simulation_intent(ctx: Context) -> str:
    """Returns the image’s simulation rendering intent

    """
    return call_api(ctx, 'Gimp.Image.get_simulation_intent', args=[])

@mcp.tool()
def Gimp_Image_get_simulation_profile(ctx: Context) -> str:
    """Returns the image’s simulation color profile

    """
    return call_api(ctx, 'Gimp.Image.get_simulation_profile', args=[])

@mcp.tool()
def Gimp_Image_get_tattoo_state(ctx: Context) -> str:
    """Returns the tattoo state associated with the image.

    """
    return call_api(ctx, 'Gimp.Image.get_tattoo_state', args=[])

@mcp.tool()
def Gimp_Image_get_thumbnail(ctx: Context, width: int, height: int, alpha: str) -> str:
    """Retrieves a thumbnail pixbuf for image.
The thumbnail will be not larger than the requested size.

    :param width: The requested thumbnail width  (<= 1024 pixels)
    :param height: The requested thumbnail height (<= 1024 pixels)
    :param alpha: How to handle an alpha channel.
    """
    return call_api(ctx, 'Gimp.Image.get_thumbnail', args=[width, height, alpha])

@mcp.tool()
def Gimp_Image_get_thumbnail_data(ctx: Context, width: int, height: int, bpp: int) -> str:
    """Get a thumbnail of an image.

    :param width: The requested thumbnail width.
    :param height: The requested thumbnail height.
    :param bpp: The previews bpp.
    """
    return call_api(ctx, 'Gimp.Image.get_thumbnail_data', args=[width, height, bpp])

@mcp.tool()
def Gimp_Image_get_unit(ctx: Context) -> str:
    """Returns the specified image’s unit.

    """
    return call_api(ctx, 'Gimp.Image.get_unit', args=[])

@mcp.tool()
def Gimp_Image_get_width(ctx: Context) -> str:
    """Return the width of the image

    """
    return call_api(ctx, 'Gimp.Image.get_width', args=[])

@mcp.tool()
def Gimp_Image_get_xcf_file(ctx: Context) -> str:
    """Returns the XCF file for the specified image.

    """
    return call_api(ctx, 'Gimp.Image.get_xcf_file', args=[])

@mcp.tool()
def Gimp_Image_grid_get_background_color(ctx: Context) -> str:
    """Sets the background color of an image’s grid.

    """
    return call_api(ctx, 'Gimp.Image.grid_get_background_color', args=[])

@mcp.tool()
def Gimp_Image_grid_get_foreground_color(ctx: Context) -> str:
    """Sets the foreground color of an image’s grid.

    """
    return call_api(ctx, 'Gimp.Image.grid_get_foreground_color', args=[])

@mcp.tool()
def Gimp_Image_grid_get_offset(ctx: Context, xoffset: float, yoffset: float) -> str:
    """Gets the offset of an image’s grid.

    :param xoffset: The image’s grid horizontal offset.
    :param yoffset: The image’s grid vertical offset.
    """
    return call_api(ctx, 'Gimp.Image.grid_get_offset', args=[xoffset, yoffset])

@mcp.tool()
def Gimp_Image_grid_get_spacing(ctx: Context, xspacing: float, yspacing: float) -> str:
    """Gets the spacing of an image’s grid.

    :param xspacing: The image’s grid horizontal spacing.
    :param yspacing: The image’s grid vertical spacing.
    """
    return call_api(ctx, 'Gimp.Image.grid_get_spacing', args=[xspacing, yspacing])

@mcp.tool()
def Gimp_Image_grid_get_style(ctx: Context) -> str:
    """Gets the style of an image’s grid.

    """
    return call_api(ctx, 'Gimp.Image.grid_get_style', args=[])

@mcp.tool()
def Gimp_Image_grid_set_background_color(ctx: Context, bgcolor: str) -> str:
    """Gets the background color of an image’s grid.

    :param bgcolor: The new background color.
    """
    return call_api(ctx, 'Gimp.Image.grid_set_background_color', args=[bgcolor])

@mcp.tool()
def Gimp_Image_grid_set_foreground_color(ctx: Context, fgcolor: str) -> str:
    """Gets the foreground color of an image’s grid.

    :param fgcolor: The new foreground color.
    """
    return call_api(ctx, 'Gimp.Image.grid_set_foreground_color', args=[fgcolor])

@mcp.tool()
def Gimp_Image_grid_set_offset(ctx: Context, xoffset: float, yoffset: float) -> str:
    """Sets the offset of an image’s grid.

    :param xoffset: The image’s grid horizontal offset.
    :param yoffset: The image’s grid vertical offset.
    """
    return call_api(ctx, 'Gimp.Image.grid_set_offset', args=[xoffset, yoffset])

@mcp.tool()
def Gimp_Image_grid_set_spacing(ctx: Context, xspacing: float, yspacing: float) -> str:
    """Sets the spacing of an image’s grid.

    :param xspacing: The image’s grid horizontal spacing.
    :param yspacing: The image’s grid vertical spacing.
    """
    return call_api(ctx, 'Gimp.Image.grid_set_spacing', args=[xspacing, yspacing])

@mcp.tool()
def Gimp_Image_grid_set_style(ctx: Context, style: str) -> str:
    """Sets the style unit of an image’s grid.

    :param style: The image’s grid style.
    """
    return call_api(ctx, 'Gimp.Image.grid_set_style', args=[style])

@mcp.tool()
def Gimp_Image_import_paths_from_file(ctx: Context, file: str, merge: bool, scale: bool, paths: str = None) -> str:
    """Import paths from an SVG file.

    :param file: The SVG file to import.
    :param merge: Merge paths into a single path object.
    :param scale: Scale the SVG to image dimensions.
    :param paths: The list of newly created paths.
    """
    return call_api(ctx, 'Gimp.Image.import_paths_from_file', args=[file, merge, scale, paths])

@mcp.tool()
def Gimp_Image_import_paths_from_string(ctx: Context, string: str, length: int, merge: bool, scale: bool, paths: str = None) -> str:
    """Import paths from an SVG string.

    :param string: A string that must be a complete and valid SVG document.
    :param length: Number of bytes in string or -1 if the string is NULL terminated.
    :param merge: Merge paths into a single path object.
    :param scale: Scale the SVG to image dimensions.
    :param paths: The list of newly created paths.
    """
    return call_api(ctx, 'Gimp.Image.import_paths_from_string', args=[string, length, merge, scale, paths])

@mcp.tool()
def Gimp_Image_insert_channel(ctx: Context, channel: str, parent: str = None, position: int) -> str:
    """Add the specified channel to the image.

    :param channel: The channel.
    :param parent: The parent channel.
    :param position: The channel position.
    """
    return call_api(ctx, 'Gimp.Image.insert_channel', args=[channel, parent, position])

@mcp.tool()
def Gimp_Image_insert_layer(ctx: Context, layer: str, parent: str = None, position: int) -> str:
    """Add the specified layer to the image.

    :param layer: The layer.
    :param parent: The parent layer.
    :param position: The layer position.
    """
    return call_api(ctx, 'Gimp.Image.insert_layer', args=[layer, parent, position])

@mcp.tool()
def Gimp_Image_insert_path(ctx: Context, path: str, parent: str = None, position: int) -> str:
    """Add the specified path to the image.

    :param path: The path.
    :param parent: The parent path.
    :param position: The path position.
    """
    return call_api(ctx, 'Gimp.Image.insert_path', args=[path, parent, position])

@mcp.tool()
def Gimp_Image_is_dirty(ctx: Context) -> str:
    """Checks if the image has unsaved changes.

    """
    return call_api(ctx, 'Gimp.Image.is_dirty', args=[])

@mcp.tool()
def Gimp_Image_is_valid(ctx: Context) -> str:
    """Returns TRUE if the image is valid.

    """
    return call_api(ctx, 'Gimp.Image.is_valid', args=[])

@mcp.tool()
def Gimp_Image_list_channels(ctx: Context) -> str:
    """Returns the list of channels contained in the specified image.

    """
    return call_api(ctx, 'Gimp.Image.list_channels', args=[])

@mcp.tool()
def Gimp_Image_list_layers(ctx: Context) -> str:
    """Returns the list of layers contained in the specified image.

    """
    return call_api(ctx, 'Gimp.Image.list_layers', args=[])

@mcp.tool()
def Gimp_Image_list_paths(ctx: Context) -> str:
    """Returns the list of paths contained in the specified image.

    """
    return call_api(ctx, 'Gimp.Image.list_paths', args=[])

@mcp.tool()
def Gimp_Image_list_selected_channels(ctx: Context) -> str:
    """Returns the list of channels selected in the specified image.

    """
    return call_api(ctx, 'Gimp.Image.list_selected_channels', args=[])

@mcp.tool()
def Gimp_Image_list_selected_drawables(ctx: Context) -> str:
    """Returns the list of drawables selected in the specified image.

    """
    return call_api(ctx, 'Gimp.Image.list_selected_drawables', args=[])

@mcp.tool()
def Gimp_Image_list_selected_layers(ctx: Context) -> str:
    """Returns the list of layers selected in the specified image.

    """
    return call_api(ctx, 'Gimp.Image.list_selected_layers', args=[])

@mcp.tool()
def Gimp_Image_list_selected_paths(ctx: Context) -> str:
    """Returns the list of paths selected in the specified image.

    """
    return call_api(ctx, 'Gimp.Image.list_selected_paths', args=[])

@mcp.tool()
def Gimp_Image_lower_item(ctx: Context, item: str) -> str:
    """Lower the specified item in its level in its item tree

    :param item: The item to lower.
    """
    return call_api(ctx, 'Gimp.Image.lower_item', args=[item])

@mcp.tool()
def Gimp_Image_lower_item_to_bottom(ctx: Context, item: str) -> str:
    """Lower the specified item to the bottom of its level in its item tree

    :param item: The item to lower to bottom.
    """
    return call_api(ctx, 'Gimp.Image.lower_item_to_bottom', args=[item])

@mcp.tool()
def Gimp_Image_merge_down(ctx: Context, merge_layer: str, merge_type: str) -> str:
    """Merge the layer passed and the first visible layer below.

    :param merge_layer: The layer to merge down from.
    :param merge_type: The type of merge.
    """
    return call_api(ctx, 'Gimp.Image.merge_down', args=[merge_layer, merge_type])

@mcp.tool()
def Gimp_Image_merge_visible_layers(ctx: Context, merge_type: str) -> str:
    """Merge the visible image layers into one.

    :param merge_type: The type of merge.
    """
    return call_api(ctx, 'Gimp.Image.merge_visible_layers', args=[merge_type])

@mcp.tool()
def Gimp_Image_metadata_save_filter(ctx: Context, mime_type: str, metadata: str, flags: str, file: str, error: str = None) -> str:
    """Filters the metadata retrieved from the image with
gimp_image_metadata_save_prepare(), taking into account the
passed flags.

    :param mime_type: The saved file’s mime-type.
    :param metadata: The metadata to export.
    :param flags: Flags to specify what of the metadata to save.
    :param file: The file image was saved to or NULL if file was not saved yet.
    :param error: No description available.
    """
    return call_api(ctx, 'Gimp.Image.metadata_save_filter', args=[mime_type, metadata, flags, file, error])

@mcp.tool()
def Gimp_Image_metadata_save_prepare(ctx: Context, mime_type: str, suggested_flags: str) -> str:
    """Gets the image metadata for storing it in an exported file.

    :param mime_type: The saved file’s mime-type.
    :param suggested_flags: Suggested default values for the metadata to export.
    """
    return call_api(ctx, 'Gimp.Image.metadata_save_prepare', args=[mime_type, suggested_flags])

@mcp.tool()
def Gimp_Image_pick_color(ctx: Context, drawables: str = None, x: float, y: float, sample_merged: bool, sample_average: bool, average_radius: float, color: str) -> str:
    """Determine the color at the given coordinates

    :param drawables: The drawables to pick from.
    :param x: X coordinate of upper-left corner of rectangle.
    :param y: Y coordinate of upper-left corner of rectangle.
    :param sample_merged: Use the composite image, not the drawables.
    :param sample_average: Average the color of all the pixels in a specified radius.
    :param average_radius: The radius of pixels to average.
    :param color: The return color.
    """
    return call_api(ctx, 'Gimp.Image.pick_color', args=[drawables, x, y, sample_merged, sample_average, average_radius, color])

@mcp.tool()
def Gimp_Image_pick_correlate_layer(ctx: Context, x: int, y: int) -> str:
    """Find the layer visible at the specified coordinates.

    :param x: The x coordinate for the pick.
    :param y: The y coordinate for the pick.
    """
    return call_api(ctx, 'Gimp.Image.pick_correlate_layer', args=[x, y])

@mcp.tool()
def Gimp_Image_policy_color_profile(ctx: Context, interactive: bool) -> str:
    """Execute the color profile conversion policy.

    :param interactive: Querying the user through a dialog is a possibility.
    """
    return call_api(ctx, 'Gimp.Image.policy_color_profile', args=[interactive])

@mcp.tool()
def Gimp_Image_policy_rotate(ctx: Context, interactive: bool) -> str:
    """Execute the "Orientation" metadata policy.

    :param interactive: Querying the user through a dialog is a possibility.
    """
    return call_api(ctx, 'Gimp.Image.policy_rotate', args=[interactive])

@mcp.tool()
def Gimp_Image_raise_item(ctx: Context, item: str) -> str:
    """Raise the specified item in its level in its item tree

    :param item: The item to raise.
    """
    return call_api(ctx, 'Gimp.Image.raise_item', args=[item])

@mcp.tool()
def Gimp_Image_raise_item_to_top(ctx: Context, item: str) -> str:
    """Raise the specified item to the top of its level in its item tree

    :param item: The item to raise to top.
    """
    return call_api(ctx, 'Gimp.Image.raise_item_to_top', args=[item])

@mcp.tool()
def Gimp_Image_remove_channel(ctx: Context, channel: str) -> str:
    """Remove the specified channel from the image.

    :param channel: The channel.
    """
    return call_api(ctx, 'Gimp.Image.remove_channel', args=[channel])

@mcp.tool()
def Gimp_Image_remove_layer(ctx: Context, layer: str) -> str:
    """Remove the specified layer from the image.

    :param layer: The layer.
    """
    return call_api(ctx, 'Gimp.Image.remove_layer', args=[layer])

@mcp.tool()
def Gimp_Image_remove_path(ctx: Context, path: str) -> str:
    """Remove the specified path from the image.

    :param path: The path object.
    """
    return call_api(ctx, 'Gimp.Image.remove_path', args=[path])

@mcp.tool()
def Gimp_Image_reorder_item(ctx: Context, item: str, parent: str = None, position: int) -> str:
    """Reorder the specified item within its item tree

    :param item: The item to reorder.
    :param parent: The new parent item.
    :param position: The new position of the item.
    """
    return call_api(ctx, 'Gimp.Image.reorder_item', args=[item, parent, position])

@mcp.tool()
def Gimp_Image_resize(ctx: Context, new_width: int, new_height: int, offx: int, offy: int) -> str:
    """Resize the image to the specified extents.

    :param new_width: New image width.
    :param new_height: New image height.
    :param offx: X offset between upper left corner of old and new images: (new - old).
    :param offy: Y offset between upper left corner of old and new images: (new - old).
    """
    return call_api(ctx, 'Gimp.Image.resize', args=[new_width, new_height, offx, offy])

@mcp.tool()
def Gimp_Image_resize_to_layers(ctx: Context) -> str:
    """Resize the image to fit all layers.

    """
    return call_api(ctx, 'Gimp.Image.resize_to_layers', args=[])

@mcp.tool()
def Gimp_Image_rotate(ctx: Context, rotate_type: str) -> str:
    """Rotates the image by the specified degrees.

    :param rotate_type: Angle of rotation.
    """
    return call_api(ctx, 'Gimp.Image.rotate', args=[rotate_type])

@mcp.tool()
def Gimp_Image_scale(ctx: Context, new_width: int, new_height: int) -> str:
    """Scale the image using the default interpolation method.

    :param new_width: New image width.
    :param new_height: New image height.
    """
    return call_api(ctx, 'Gimp.Image.scale', args=[new_width, new_height])

@mcp.tool()
def Gimp_Image_select_color(ctx: Context, operation: str, drawable: str, color: str) -> str:
    """Create a selection by selecting all pixels (in the specified
drawable) with the same (or similar) color to that specified.

    :param operation: The selection operation.
    :param drawable: The affected drawable.
    :param color: The color to select.
    """
    return call_api(ctx, 'Gimp.Image.select_color', args=[operation, drawable, color])

@mcp.tool()
def Gimp_Image_select_contiguous_color(ctx: Context, operation: str, drawable: str, x: float, y: float) -> str:
    """Create a selection by selecting all pixels around specified
coordinates with the same (or similar) color to that at the coordinates.

    :param operation: The selection operation.
    :param drawable: The affected drawable.
    :param x: X coordinate of initial seed fill point: (image coordinates).
    :param y: Y coordinate of initial seed fill point: (image coordinates).
    """
    return call_api(ctx, 'Gimp.Image.select_contiguous_color', args=[operation, drawable, x, y])

@mcp.tool()
def Gimp_Image_select_ellipse(ctx: Context, operation: str, x: float, y: float, width: float, height: float) -> str:
    """Create an elliptical selection over the specified image.

    :param operation: The selection operation.
    :param x: X coordinate of upper-left corner of ellipse bounding box.
    :param y: Y coordinate of upper-left corner of ellipse bounding box.
    :param width: The width of the ellipse.
    :param height: The height of the ellipse.
    """
    return call_api(ctx, 'Gimp.Image.select_ellipse', args=[operation, x, y, width, height])

@mcp.tool()
def Gimp_Image_select_item(ctx: Context, operation: str, item: str) -> str:
    """Transforms the specified item into a selection

    :param operation: The desired operation with current selection.
    :param item: The item to render to the selection.
    """
    return call_api(ctx, 'Gimp.Image.select_item', args=[operation, item])

@mcp.tool()
def Gimp_Image_select_polygon(ctx: Context, operation: str, num_segs: int, segs: str) -> str:
    """Create a polygonal selection over the specified image.

    :param operation: The selection operation.
    :param num_segs: Number of points (count 1 coordinate as two points).
    :param segs: Array of points: { p1.x, p1.y, p2.x, p2.y, …, pn.x, pn.y}.
    """
    return call_api(ctx, 'Gimp.Image.select_polygon', args=[operation, num_segs, segs])

@mcp.tool()
def Gimp_Image_select_rectangle(ctx: Context, operation: str, x: float, y: float, width: float, height: float) -> str:
    """Create a rectangular selection over the specified image;

    :param operation: The selection operation.
    :param x: X coordinate of upper-left corner of rectangle.
    :param y: Y coordinate of upper-left corner of rectangle.
    :param width: The width of the rectangle.
    :param height: The height of the rectangle.
    """
    return call_api(ctx, 'Gimp.Image.select_rectangle', args=[operation, x, y, width, height])

@mcp.tool()
def Gimp_Image_select_round_rectangle(ctx: Context, operation: str, x: float, y: float, width: float, height: float, corner_radius_x: float, corner_radius_y: float) -> str:
    """Create a rectangular selection with round corners over the specified image;

    :param operation: The selection operation.
    :param x: X coordinate of upper-left corner of rectangle.
    :param y: Y coordinate of upper-left corner of rectangle.
    :param width: The width of the rectangle.
    :param height: The height of the rectangle.
    :param corner_radius_x: The corner radius in X direction.
    :param corner_radius_y: The corner radius in Y direction.
    """
    return call_api(ctx, 'Gimp.Image.select_round_rectangle', args=[operation, x, y, width, height, corner_radius_x, corner_radius_y])

@mcp.tool()
def Gimp_Image_set_color_profile(ctx: Context, profile: str = None) -> str:
    """Sets the image’s color profile

    :param profile: A GimpColorProfile, or NULL.
    """
    return call_api(ctx, 'Gimp.Image.set_color_profile', args=[profile])

@mcp.tool()
def Gimp_Image_set_color_profile_from_file(ctx: Context, file: str) -> str:
    """Sets the image’s color profile from an ICC file

    :param file: The file containing the new color profile.
    """
    return call_api(ctx, 'Gimp.Image.set_color_profile_from_file', args=[file])

@mcp.tool()
def Gimp_Image_set_component_active(ctx: Context, component: str, active: bool) -> str:
    """Sets if the specified image’s image component is active.

    :param component: The image component.
    :param active: Component is active.
    """
    return call_api(ctx, 'Gimp.Image.set_component_active', args=[component, active])

@mcp.tool()
def Gimp_Image_set_component_visible(ctx: Context, component: str, visible: bool) -> str:
    """Sets if the specified image’s image component is visible.

    :param component: The image component.
    :param visible: Component is visible.
    """
    return call_api(ctx, 'Gimp.Image.set_component_visible', args=[component, visible])

@mcp.tool()
def Gimp_Image_set_file(ctx: Context, file: str) -> str:
    """Sets the specified XCF image’s file.

    :param file: The new image file.
    """
    return call_api(ctx, 'Gimp.Image.set_file', args=[file])

@mcp.tool()
def Gimp_Image_set_metadata(ctx: Context, metadata: str) -> str:
    """Set the image’s metadata.

    :param metadata: The exif/ptc/xmp metadata.
    """
    return call_api(ctx, 'Gimp.Image.set_metadata', args=[metadata])

@mcp.tool()
def Gimp_Image_set_palette(ctx: Context, new_palette: str) -> str:
    """Set the image’s colormap to a copy of palette

    :param new_palette: The palette to copy from.
    """
    return call_api(ctx, 'Gimp.Image.set_palette', args=[new_palette])

@mcp.tool()
def Gimp_Image_set_resolution(ctx: Context, xresolution: float, yresolution: float) -> str:
    """Sets the specified image’s resolution.

    :param xresolution: The new image resolution in the x-axis, in dots per inch.
    :param yresolution: The new image resolution in the y-axis, in dots per inch.
    """
    return call_api(ctx, 'Gimp.Image.set_resolution', args=[xresolution, yresolution])

@mcp.tool()
def Gimp_Image_set_selected_channels(ctx: Context, channels: str = None) -> str:
    """Sets the specified image’s selected channels.

    :param channels: The list of channels to select.
    """
    return call_api(ctx, 'Gimp.Image.set_selected_channels', args=[channels])

@mcp.tool()
def Gimp_Image_set_selected_layers(ctx: Context, layers: str = None) -> str:
    """Sets the specified image’s selected layers.

    :param layers: The list of layers to select.
    """
    return call_api(ctx, 'Gimp.Image.set_selected_layers', args=[layers])

@mcp.tool()
def Gimp_Image_set_selected_paths(ctx: Context, paths: str = None) -> str:
    """Sets the specified image’s selected paths.

    :param paths: The list of paths to select.
    """
    return call_api(ctx, 'Gimp.Image.set_selected_paths', args=[paths])

@mcp.tool()
def Gimp_Image_set_simulation_bpc(ctx: Context, bpc: bool) -> str:
    """Sets whether the image has Black Point Compensation enabled for its simulation

    :param bpc: The Black Point Compensation status.
    """
    return call_api(ctx, 'Gimp.Image.set_simulation_bpc', args=[bpc])

@mcp.tool()
def Gimp_Image_set_simulation_intent(ctx: Context, intent: str) -> str:
    """Sets the image’s simulation rendering intent

    :param intent: A GimpColorRenderingIntent.
    """
    return call_api(ctx, 'Gimp.Image.set_simulation_intent', args=[intent])

@mcp.tool()
def Gimp_Image_set_simulation_profile(ctx: Context, profile: str = None) -> str:
    """Sets the image’s simulation color profile

    :param profile: A GimpColorProfile, or NULL.
    """
    return call_api(ctx, 'Gimp.Image.set_simulation_profile', args=[profile])

@mcp.tool()
def Gimp_Image_set_simulation_profile_from_file(ctx: Context, file: str) -> str:
    """Sets the image’s simulation color profile from an ICC file

    :param file: The file containing the new simulation color profile.
    """
    return call_api(ctx, 'Gimp.Image.set_simulation_profile_from_file', args=[file])

@mcp.tool()
def Gimp_Image_set_tattoo_state(ctx: Context, tattoo_state: int) -> str:
    """Set the tattoo state associated with the image.

    :param tattoo_state: The new image tattoo state.
    """
    return call_api(ctx, 'Gimp.Image.set_tattoo_state', args=[tattoo_state])

@mcp.tool()
def Gimp_Image_set_unit(ctx: Context, unit: str) -> str:
    """Sets the specified image’s unit.

    :param unit: The new image unit.
    """
    return call_api(ctx, 'Gimp.Image.set_unit', args=[unit])

@mcp.tool()
def Gimp_Image_take_selected_channels(ctx: Context, channels: str) -> str:
    """The channels are set as the selected channels in the image. Any previous
selected layers or channels are unselected. An exception is a previously
existing floating selection, in which case this procedure will return an
execution error.

    :param channels: The list of channels to select.
    """
    return call_api(ctx, 'Gimp.Image.take_selected_channels', args=[channels])

@mcp.tool()
def Gimp_Image_take_selected_layers(ctx: Context, layers: str) -> str:
    """The layers are set as the selected layers in the image. Any previous
selected layers or channels are unselected. An exception is a previously
existing floating selection, in which case this procedure will return an
execution error.

    :param layers: The list of layers to select.
    """
    return call_api(ctx, 'Gimp.Image.take_selected_layers', args=[layers])

@mcp.tool()
def Gimp_Image_take_selected_paths(ctx: Context, paths: str) -> str:
    """The paths are set as the selected paths in the image. Any previous
selected paths are unselected.

    :param paths: The list of paths to select.
    """
    return call_api(ctx, 'Gimp.Image.take_selected_paths', args=[paths])

@mcp.tool()
def Gimp_Image_thaw_channels(ctx: Context) -> str:
    """Thaw the image’s channel list.

    """
    return call_api(ctx, 'Gimp.Image.thaw_channels', args=[])

@mcp.tool()
def Gimp_Image_thaw_layers(ctx: Context) -> str:
    """Thaw the image’s layer list.

    """
    return call_api(ctx, 'Gimp.Image.thaw_layers', args=[])

@mcp.tool()
def Gimp_Image_thaw_paths(ctx: Context) -> str:
    """Thaw the image’s path list.

    """
    return call_api(ctx, 'Gimp.Image.thaw_paths', args=[])

@mcp.tool()
def Gimp_Image_undo_disable(ctx: Context) -> str:
    """Disable the image’s undo stack.

    """
    return call_api(ctx, 'Gimp.Image.undo_disable', args=[])

@mcp.tool()
def Gimp_Image_undo_enable(ctx: Context) -> str:
    """Enable the image’s undo stack.

    """
    return call_api(ctx, 'Gimp.Image.undo_enable', args=[])

@mcp.tool()
def Gimp_Image_undo_freeze(ctx: Context) -> str:
    """Freeze the image’s undo stack.

    """
    return call_api(ctx, 'Gimp.Image.undo_freeze', args=[])

@mcp.tool()
def Gimp_Image_undo_group_end(ctx: Context) -> str:
    """Finish a group undo.

    """
    return call_api(ctx, 'Gimp.Image.undo_group_end', args=[])

@mcp.tool()
def Gimp_Image_undo_group_start(ctx: Context) -> str:
    """Starts a group undo.

    """
    return call_api(ctx, 'Gimp.Image.undo_group_start', args=[])

@mcp.tool()
def Gimp_Image_undo_is_enabled(ctx: Context) -> str:
    """Check if the image’s undo stack is enabled.

    """
    return call_api(ctx, 'Gimp.Image.undo_is_enabled', args=[])

@mcp.tool()
def Gimp_Image_undo_thaw(ctx: Context) -> str:
    """Thaw the image’s undo stack.

    """
    return call_api(ctx, 'Gimp.Image.undo_thaw', args=[])

@mcp.tool()
def Gimp_Image_unset_active_channel(ctx: Context) -> str:
    """Unsets the active channel in the specified image.

    """
    return call_api(ctx, 'Gimp.Image.unset_active_channel', args=[])

@mcp.tool()
def Gimp_Item_attach_parasite(ctx: Context, parasite: str) -> str:
    """Add a parasite to an item.

    :param parasite: The parasite to attach to the item.
    """
    return call_api(ctx, 'Gimp.Item.attach_parasite', args=[parasite])

@mcp.tool()
def Gimp_Item_delete(ctx: Context) -> str:
    """Delete a item.

    """
    return call_api(ctx, 'Gimp.Item.delete', args=[])

@mcp.tool()
def Gimp_Item_detach_parasite(ctx: Context, name: str) -> str:
    """Removes a parasite from an item.

    :param name: The name of the parasite to detach from the item.
    """
    return call_api(ctx, 'Gimp.Item.detach_parasite', args=[name])

@mcp.tool()
def Gimp_Item_get_children(ctx: Context) -> str:
    """Returns the item’s list of children.

    """
    return call_api(ctx, 'Gimp.Item.get_children', args=[])

@mcp.tool()
def Gimp_Item_get_color_tag(ctx: Context) -> str:
    """Get the color tag of the specified item.

    """
    return call_api(ctx, 'Gimp.Item.get_color_tag', args=[])

@mcp.tool()
def Gimp_Item_get_expanded(ctx: Context) -> str:
    """Returns whether the item is expanded.

    """
    return call_api(ctx, 'Gimp.Item.get_expanded', args=[])

@mcp.tool()
def Gimp_Item_get_id(ctx: Context) -> str:
    """mostly internal data and not reusable across sessions.

    """
    return call_api(ctx, 'Gimp.Item.get_id', args=[])

@mcp.tool()
def Gimp_Item_get_image(ctx: Context) -> str:
    """Returns the item’s image.

    """
    return call_api(ctx, 'Gimp.Item.get_image', args=[])

@mcp.tool()
def Gimp_Item_get_lock_content(ctx: Context) -> str:
    """Get the ‘lock content’ state of the specified item.

    """
    return call_api(ctx, 'Gimp.Item.get_lock_content', args=[])

@mcp.tool()
def Gimp_Item_get_lock_position(ctx: Context) -> str:
    """Get the ‘lock position’ state of the specified item.

    """
    return call_api(ctx, 'Gimp.Item.get_lock_position', args=[])

@mcp.tool()
def Gimp_Item_get_lock_visibility(ctx: Context) -> str:
    """Get the ‘lock visibility’ state of the specified item.

    """
    return call_api(ctx, 'Gimp.Item.get_lock_visibility', args=[])

@mcp.tool()
def Gimp_Item_get_name(ctx: Context) -> str:
    """Get the name of the specified item.

    """
    return call_api(ctx, 'Gimp.Item.get_name', args=[])

@mcp.tool()
def Gimp_Item_get_parasite(ctx: Context, name: str) -> str:
    """Look up a parasite in an item

    :param name: The name of the parasite to find.
    """
    return call_api(ctx, 'Gimp.Item.get_parasite', args=[name])

@mcp.tool()
def Gimp_Item_get_parasite_list(ctx: Context) -> str:
    """List all parasites.

    """
    return call_api(ctx, 'Gimp.Item.get_parasite_list', args=[])

@mcp.tool()
def Gimp_Item_get_parent(ctx: Context) -> str:
    """Returns the item’s parent item.

    """
    return call_api(ctx, 'Gimp.Item.get_parent', args=[])

@mcp.tool()
def Gimp_Item_get_tattoo(ctx: Context) -> str:
    """Get the tattoo of the specified item.

    """
    return call_api(ctx, 'Gimp.Item.get_tattoo', args=[])

@mcp.tool()
def Gimp_Item_get_visible(ctx: Context) -> str:
    """Get the visibility of the specified item.

    """
    return call_api(ctx, 'Gimp.Item.get_visible', args=[])

@mcp.tool()
def Gimp_Item_is_channel(ctx: Context) -> str:
    """Returns whether the item is a channel.

    """
    return call_api(ctx, 'Gimp.Item.is_channel', args=[])

@mcp.tool()
def Gimp_Item_is_drawable(ctx: Context) -> str:
    """Returns whether the item is a drawable.

    """
    return call_api(ctx, 'Gimp.Item.is_drawable', args=[])

@mcp.tool()
def Gimp_Item_is_group(ctx: Context) -> str:
    """Returns whether the item is a group item.

    """
    return call_api(ctx, 'Gimp.Item.is_group', args=[])

@mcp.tool()
def Gimp_Item_is_group_layer(ctx: Context) -> str:
    """Returns whether the item is a group layer.

    """
    return call_api(ctx, 'Gimp.Item.is_group_layer', args=[])

@mcp.tool()
def Gimp_Item_is_layer(ctx: Context) -> str:
    """Returns whether the item is a layer.

    """
    return call_api(ctx, 'Gimp.Item.is_layer', args=[])

@mcp.tool()
def Gimp_Item_is_layer_mask(ctx: Context) -> str:
    """Returns whether the item is a layer mask.

    """
    return call_api(ctx, 'Gimp.Item.is_layer_mask', args=[])

@mcp.tool()
def Gimp_Item_is_path(ctx: Context) -> str:
    """Returns whether the item is a path.

    """
    return call_api(ctx, 'Gimp.Item.is_path', args=[])

@mcp.tool()
def Gimp_Item_is_selection(ctx: Context) -> str:
    """Returns whether the item is a selection.

    """
    return call_api(ctx, 'Gimp.Item.is_selection', args=[])

@mcp.tool()
def Gimp_Item_is_text_layer(ctx: Context) -> str:
    """Returns whether the item is a text layer.

    """
    return call_api(ctx, 'Gimp.Item.is_text_layer', args=[])

@mcp.tool()
def Gimp_Item_is_valid(ctx: Context) -> str:
    """Returns TRUE if the item is valid.

    """
    return call_api(ctx, 'Gimp.Item.is_valid', args=[])

@mcp.tool()
def Gimp_Item_list_children(ctx: Context) -> str:
    """Returns the item’s list of children.

    """
    return call_api(ctx, 'Gimp.Item.list_children', args=[])

@mcp.tool()
def Gimp_Item_set_color_tag(ctx: Context, color_tag: str) -> str:
    """Set the color tag of the specified item.

    :param color_tag: The new item color tag.
    """
    return call_api(ctx, 'Gimp.Item.set_color_tag', args=[color_tag])

@mcp.tool()
def Gimp_Item_set_expanded(ctx: Context, expanded: bool) -> str:
    """Sets the expanded state of the item.

    :param expanded: TRUE to expand the item, FALSE to collapse the item.
    """
    return call_api(ctx, 'Gimp.Item.set_expanded', args=[expanded])

@mcp.tool()
def Gimp_Item_set_lock_content(ctx: Context, lock_content: bool) -> str:
    """Set the ‘lock content’ state of the specified item.

    :param lock_content: The new item ‘lock content’ state.
    """
    return call_api(ctx, 'Gimp.Item.set_lock_content', args=[lock_content])

@mcp.tool()
def Gimp_Item_set_lock_position(ctx: Context, lock_position: bool) -> str:
    """Set the ‘lock position’ state of the specified item.

    :param lock_position: The new item ‘lock position’ state.
    """
    return call_api(ctx, 'Gimp.Item.set_lock_position', args=[lock_position])

@mcp.tool()
def Gimp_Item_set_lock_visibility(ctx: Context, lock_visibility: bool) -> str:
    """Set the ‘lock visibility’ state of the specified item.

    :param lock_visibility: The new item ‘lock visibility’ state.
    """
    return call_api(ctx, 'Gimp.Item.set_lock_visibility', args=[lock_visibility])

@mcp.tool()
def Gimp_Item_set_name(ctx: Context, name: str) -> str:
    """Set the name of the specified item.

    :param name: The new item name.
    """
    return call_api(ctx, 'Gimp.Item.set_name', args=[name])

@mcp.tool()
def Gimp_Item_set_tattoo(ctx: Context, tattoo: int) -> str:
    """Set the tattoo of the specified item.

    :param tattoo: The new item tattoo.
    """
    return call_api(ctx, 'Gimp.Item.set_tattoo', args=[tattoo])

@mcp.tool()
def Gimp_Item_set_visible(ctx: Context, visible: bool) -> str:
    """Set the visibility of the specified item.

    :param visible: The new item visibility.
    """
    return call_api(ctx, 'Gimp.Item.set_visible', args=[visible])

@mcp.tool()
def Gimp_Item_transform_2d(ctx: Context, source_x: float, source_y: float, scale_x: float, scale_y: float, angle: float, dest_x: float, dest_y: float) -> str:
    """Transform the specified item in 2d.

    :param source_x: X coordinate of the transformation center.
    :param source_y: Y coordinate of the transformation center.
    :param scale_x: Amount to scale in x direction.
    :param scale_y: Amount to scale in y direction.
    :param angle: The angle of rotation (radians).
    :param dest_x: X coordinate of where the center goes.
    :param dest_y: Y coordinate of where the center goes.
    """
    return call_api(ctx, 'Gimp.Item.transform_2d', args=[source_x, source_y, scale_x, scale_y, angle, dest_x, dest_y])

@mcp.tool()
def Gimp_Item_transform_flip(ctx: Context, x0: float, y0: float, x1: float, y1: float) -> str:
    """Flip the specified item around a given line.

    :param x0: Horz. coord. of one end of axis.
    :param y0: Vert. coord. of one end of axis.
    :param x1: Horz. coord. of other end of axis.
    :param y1: Vert. coord. of other end of axis.
    """
    return call_api(ctx, 'Gimp.Item.transform_flip', args=[x0, y0, x1, y1])

@mcp.tool()
def Gimp_Item_transform_flip_simple(ctx: Context, flip_type: str, auto_center: bool, axis: float) -> str:
    """Flip the specified item either vertically or horizontally.

    :param flip_type: Type of flip.
    :param auto_center: Whether to automatically position the axis in the selection center.
    :param axis: Coord. of flip axis.
    """
    return call_api(ctx, 'Gimp.Item.transform_flip_simple', args=[flip_type, auto_center, axis])

@mcp.tool()
def Gimp_Item_transform_matrix(ctx: Context, coeff_0_0: float, coeff_0_1: float, coeff_0_2: float, coeff_1_0: float, coeff_1_1: float, coeff_1_2: float, coeff_2_0: float, coeff_2_1: float, coeff_2_2: float) -> str:
    """Transform the specified item in 2d.

    :param coeff_0_0: Coefficient (0,0) of the transformation matrix.
    :param coeff_0_1: Coefficient (0,1) of the transformation matrix.
    :param coeff_0_2: Coefficient (0,2) of the transformation matrix.
    :param coeff_1_0: Coefficient (1,0) of the transformation matrix.
    :param coeff_1_1: Coefficient (1,1) of the transformation matrix.
    :param coeff_1_2: Coefficient (1,2) of the transformation matrix.
    :param coeff_2_0: Coefficient (2,0) of the transformation matrix.
    :param coeff_2_1: Coefficient (2,1) of the transformation matrix.
    :param coeff_2_2: Coefficient (2,2) of the transformation matrix.
    """
    return call_api(ctx, 'Gimp.Item.transform_matrix', args=[coeff_0_0, coeff_0_1, coeff_0_2, coeff_1_0, coeff_1_1, coeff_1_2, coeff_2_0, coeff_2_1, coeff_2_2])

@mcp.tool()
def Gimp_Item_transform_perspective(ctx: Context, x0: float, y0: float, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float) -> str:
    """Perform a possibly non-affine transformation on the specified item.

    :param x0: The new x coordinate of upper-left corner of original bounding box.
    :param y0: The new y coordinate of upper-left corner of original bounding box.
    :param x1: The new x coordinate of upper-right corner of original bounding box.
    :param y1: The new y coordinate of upper-right corner of original bounding box.
    :param x2: The new x coordinate of lower-left corner of original bounding box.
    :param y2: The new y coordinate of lower-left corner of original bounding box.
    :param x3: The new x coordinate of lower-right corner of original bounding box.
    :param y3: The new y coordinate of lower-right corner of original bounding box.
    """
    return call_api(ctx, 'Gimp.Item.transform_perspective', args=[x0, y0, x1, y1, x2, y2, x3, y3])

@mcp.tool()
def Gimp_Item_transform_rotate(ctx: Context, angle: float, auto_center: bool, center_x: float, center_y: float) -> str:
    """Rotate the specified item about given coordinates through the
specified angle.

    :param angle: The angle of rotation (radians).
    :param auto_center: Whether to automatically rotate around the selection center.
    :param center_x: The hor. coordinate of the center of rotation.
    :param center_y: The vert. coordinate of the center of rotation.
    """
    return call_api(ctx, 'Gimp.Item.transform_rotate', args=[angle, auto_center, center_x, center_y])

@mcp.tool()
def Gimp_Item_transform_rotate_simple(ctx: Context, rotate_type: str, auto_center: bool, center_x: float, center_y: float) -> str:
    """Rotate the specified item about given coordinates through the
specified angle.

    :param rotate_type: Type of rotation.
    :param auto_center: Whether to automatically rotate around the selection center.
    :param center_x: The hor. coordinate of the center of rotation.
    :param center_y: The vert. coordinate of the center of rotation.
    """
    return call_api(ctx, 'Gimp.Item.transform_rotate_simple', args=[rotate_type, auto_center, center_x, center_y])

@mcp.tool()
def Gimp_Item_transform_scale(ctx: Context, x0: float, y0: float, x1: float, y1: float) -> str:
    """Scale the specified item.

    :param x0: The new x coordinate of the upper-left corner of the scaled region.
    :param y0: The new y coordinate of the upper-left corner of the scaled region.
    :param x1: The new x coordinate of the lower-right corner of the scaled region.
    :param y1: The new y coordinate of the lower-right corner of the scaled region.
    """
    return call_api(ctx, 'Gimp.Item.transform_scale', args=[x0, y0, x1, y1])

@mcp.tool()
def Gimp_Item_transform_shear(ctx: Context, shear_type: str, magnitude: float) -> str:
    """Shear the specified item about its center by the specified magnitude.

    :param shear_type: Type of shear.
    :param magnitude: The magnitude of the shear.
    """
    return call_api(ctx, 'Gimp.Item.transform_shear', args=[shear_type, magnitude])

@mcp.tool()
def Gimp_Item_transform_translate(ctx: Context, off_x: float, off_y: float) -> str:
    """Translate the item by the specified offsets.

    :param off_x: Offset in x direction.
    :param off_y: Offset in y direction.
    """
    return call_api(ctx, 'Gimp.Item.transform_translate', args=[off_x, off_y])

@mcp.tool()
def Gimp_Layer_add_alpha(ctx: Context) -> str:
    """Add an alpha channel to the layer if it doesn’t already have one.

    """
    return call_api(ctx, 'Gimp.Layer.add_alpha', args=[])

@mcp.tool()
def Gimp_Layer_add_mask(ctx: Context, mask: str) -> str:
    """Add a layer mask to the specified layer.

    :param mask: The mask to add to the layer.
    """
    return call_api(ctx, 'Gimp.Layer.add_mask', args=[mask])

@mcp.tool()
def Gimp_Layer_copy(ctx: Context) -> str:
    """Copy a layer.

    """
    return call_api(ctx, 'Gimp.Layer.copy', args=[])

@mcp.tool()
def Gimp_Layer_create_mask(ctx: Context, mask_type: str) -> str:
    """Create a layer mask for the specified layer.

    :param mask_type: The type of mask.
    """
    return call_api(ctx, 'Gimp.Layer.create_mask', args=[mask_type])

@mcp.tool()
def Gimp_Layer_flatten(ctx: Context) -> str:
    """Remove the alpha channel from the layer if it has one.

    """
    return call_api(ctx, 'Gimp.Layer.flatten', args=[])

@mcp.tool()
def Gimp_Layer_get_apply_mask(ctx: Context) -> str:
    """Get the apply mask setting of the specified layer.

    """
    return call_api(ctx, 'Gimp.Layer.get_apply_mask', args=[])

@mcp.tool()
def Gimp_Layer_get_blend_space(ctx: Context) -> str:
    """Get the blend space of the specified layer.

    """
    return call_api(ctx, 'Gimp.Layer.get_blend_space', args=[])

@mcp.tool()
def Gimp_Layer_get_composite_mode(ctx: Context) -> str:
    """Get the composite mode of the specified layer.

    """
    return call_api(ctx, 'Gimp.Layer.get_composite_mode', args=[])

@mcp.tool()
def Gimp_Layer_get_composite_space(ctx: Context) -> str:
    """Get the composite space of the specified layer.

    """
    return call_api(ctx, 'Gimp.Layer.get_composite_space', args=[])

@mcp.tool()
def Gimp_Layer_get_edit_mask(ctx: Context) -> str:
    """Get the edit mask setting of the specified layer.

    """
    return call_api(ctx, 'Gimp.Layer.get_edit_mask', args=[])

@mcp.tool()
def Gimp_Layer_get_lock_alpha(ctx: Context) -> str:
    """Get the lock alpha channel setting of the specified layer.

    """
    return call_api(ctx, 'Gimp.Layer.get_lock_alpha', args=[])

@mcp.tool()
def Gimp_Layer_get_mask(ctx: Context) -> str:
    """Get the specified layer’s mask if it exists.

    """
    return call_api(ctx, 'Gimp.Layer.get_mask', args=[])

@mcp.tool()
def Gimp_Layer_get_mode(ctx: Context) -> str:
    """Get the combination mode of the specified layer.

    """
    return call_api(ctx, 'Gimp.Layer.get_mode', args=[])

@mcp.tool()
def Gimp_Layer_get_opacity(ctx: Context) -> str:
    """Get the opacity of the specified layer.

    """
    return call_api(ctx, 'Gimp.Layer.get_opacity', args=[])

@mcp.tool()
def Gimp_Layer_get_show_mask(ctx: Context) -> str:
    """Get the show mask setting of the specified layer.

    """
    return call_api(ctx, 'Gimp.Layer.get_show_mask', args=[])

@mcp.tool()
def Gimp_Layer_is_floating_sel(ctx: Context) -> str:
    """Is the specified layer a floating selection?

    """
    return call_api(ctx, 'Gimp.Layer.is_floating_sel', args=[])

@mcp.tool()
def Gimp_Layer_remove_mask(ctx: Context, mode: str) -> str:
    """Remove the specified layer mask from the layer.

    :param mode: Removal mode.
    """
    return call_api(ctx, 'Gimp.Layer.remove_mask', args=[mode])

@mcp.tool()
def Gimp_Layer_resize(ctx: Context, new_width: int, new_height: int, offx: int, offy: int) -> str:
    """Resize the layer to the specified extents.

    :param new_width: New layer width.
    :param new_height: New layer height.
    :param offx: X offset between upper left corner of old and new layers: (old - new).
    :param offy: Y offset between upper left corner of old and new layers: (old - new).
    """
    return call_api(ctx, 'Gimp.Layer.resize', args=[new_width, new_height, offx, offy])

@mcp.tool()
def Gimp_Layer_resize_to_image_size(ctx: Context) -> str:
    """Resize a layer to the image size.

    """
    return call_api(ctx, 'Gimp.Layer.resize_to_image_size', args=[])

@mcp.tool()
def Gimp_Layer_scale(ctx: Context, new_width: int, new_height: int, local_origin: bool) -> str:
    """Scale the layer using the default interpolation method.

    :param new_width: New layer width.
    :param new_height: New layer height.
    :param local_origin: Use a local origin (as opposed to the image origin).
    """
    return call_api(ctx, 'Gimp.Layer.scale', args=[new_width, new_height, local_origin])

@mcp.tool()
def Gimp_Layer_set_apply_mask(ctx: Context, apply_mask: bool) -> str:
    """Set the apply mask setting of the specified layer.

    :param apply_mask: The new layer’s apply mask setting.
    """
    return call_api(ctx, 'Gimp.Layer.set_apply_mask', args=[apply_mask])

@mcp.tool()
def Gimp_Layer_set_blend_space(ctx: Context, blend_space: str) -> str:
    """Set the blend space of the specified layer.

    :param blend_space: The new layer blend space.
    """
    return call_api(ctx, 'Gimp.Layer.set_blend_space', args=[blend_space])

@mcp.tool()
def Gimp_Layer_set_composite_mode(ctx: Context, composite_mode: str) -> str:
    """Set the composite mode of the specified layer.

    :param composite_mode: The new layer composite mode.
    """
    return call_api(ctx, 'Gimp.Layer.set_composite_mode', args=[composite_mode])

@mcp.tool()
def Gimp_Layer_set_composite_space(ctx: Context, composite_space: str) -> str:
    """Set the composite space of the specified layer.

    :param composite_space: The new layer composite space.
    """
    return call_api(ctx, 'Gimp.Layer.set_composite_space', args=[composite_space])

@mcp.tool()
def Gimp_Layer_set_edit_mask(ctx: Context, edit_mask: bool) -> str:
    """Set the edit mask setting of the specified layer.

    :param edit_mask: The new layer’s edit mask setting.
    """
    return call_api(ctx, 'Gimp.Layer.set_edit_mask', args=[edit_mask])

@mcp.tool()
def Gimp_Layer_set_lock_alpha(ctx: Context, lock_alpha: bool) -> str:
    """Set the lock alpha channel setting of the specified layer.

    :param lock_alpha: The new layer’s lock alpha channel setting.
    """
    return call_api(ctx, 'Gimp.Layer.set_lock_alpha', args=[lock_alpha])

@mcp.tool()
def Gimp_Layer_set_mode(ctx: Context, mode: str) -> str:
    """Set the combination mode of the specified layer.

    :param mode: The new layer combination mode.
    """
    return call_api(ctx, 'Gimp.Layer.set_mode', args=[mode])

@mcp.tool()
def Gimp_Layer_set_offsets(ctx: Context, offx: int, offy: int) -> str:
    """Set the layer offsets.

    :param offx: Offset in x direction.
    :param offy: Offset in y direction.
    """
    return call_api(ctx, 'Gimp.Layer.set_offsets', args=[offx, offy])

@mcp.tool()
def Gimp_Layer_set_opacity(ctx: Context, opacity: float) -> str:
    """Set the opacity of the specified layer.

    :param opacity: The new layer opacity.
    """
    return call_api(ctx, 'Gimp.Layer.set_opacity', args=[opacity])

@mcp.tool()
def Gimp_Layer_set_show_mask(ctx: Context, show_mask: bool) -> str:
    """Set the show mask setting of the specified layer.

    :param show_mask: The new layer’s show mask setting.
    """
    return call_api(ctx, 'Gimp.Layer.set_show_mask', args=[show_mask])

@mcp.tool()
def Gimp_LoadProcedure_get_handles_raw(ctx: Context) -> str:
    """Returns the procedure’s ‘handles raw’ flag as set with
gimp_load_procedure_set_handles_raw().

    """
    return call_api(ctx, 'Gimp.LoadProcedure.get_handles_raw', args=[])

@mcp.tool()
def Gimp_LoadProcedure_get_thumbnail_loader(ctx: Context) -> str:
    """Returns the procedure’s thumbnail loader procedure as set with
gimp_load_procedure_set_thumbnail_loader().

    """
    return call_api(ctx, 'Gimp.LoadProcedure.get_thumbnail_loader', args=[])

@mcp.tool()
def Gimp_LoadProcedure_set_handles_raw(ctx: Context, handles_raw: bool) -> str:
    """Registers a load procedure as capable of handling raw digital camera loads.

    :param handles_raw: The procedure’s handles raw flag.
    """
    return call_api(ctx, 'Gimp.LoadProcedure.set_handles_raw', args=[handles_raw])

@mcp.tool()
def Gimp_LoadProcedure_set_thumbnail_loader(ctx: Context, thumbnail_proc: str) -> str:
    """Associates a thumbnail loader with a file load procedure.

    :param thumbnail_proc: The name of the thumbnail load procedure.
    """
    return call_api(ctx, 'Gimp.LoadProcedure.set_thumbnail_loader', args=[thumbnail_proc])

@mcp.tool()
def Gimp_Metadata_add_xmp_history(ctx: Context, state_status: str) -> str:
    """Type: gchar*

    :param state_status: No description available.
    """
    return call_api(ctx, 'Gimp.Metadata.add_xmp_history', args=[state_status])

@mcp.tool()
def Gimp_Metadata_duplicate(ctx: Context) -> str:
    """Duplicates a GimpMetadata instance.

    """
    return call_api(ctx, 'Gimp.Metadata.duplicate', args=[])

@mcp.tool()
def Gimp_Metadata_get_colorspace(ctx: Context) -> str:
    """Returns values based on Exif.Photo.ColorSpace, Xmp.exif.ColorSpace,
Exif.Iop.InteroperabilityIndex, Exif.Nikon3.ColorSpace,
Exif.Canon.ColorSpace of metadata.

    """
    return call_api(ctx, 'Gimp.Metadata.get_colorspace', args=[])

@mcp.tool()
def Gimp_Metadata_get_resolution(ctx: Context, xres: float = None, yres: float = None, unit: str = None) -> str:
    """Returns values based on Exif.Image.XResolution,
Exif.Image.YResolution and Exif.Image.ResolutionUnit of metadata.

    :param xres: Return location for the X Resolution, in ppi.
    :param yres: Return location for the Y Resolution, in ppi.
    :param unit: Return location for the unit unit.
    """
    return call_api(ctx, 'Gimp.Metadata.get_resolution', args=[xres, yres, unit])

@mcp.tool()
def Gimp_Metadata_save_to_file(ctx: Context, file: str, error: str = None) -> str:
    """Saves metadata to file.

    :param file: The file to save the metadata to.
    :param error: No description available.
    """
    return call_api(ctx, 'Gimp.Metadata.save_to_file', args=[file, error])

@mcp.tool()
def Gimp_Metadata_serialize(ctx: Context) -> str:
    """Serializes metadata into an XML string that can later be deserialized
using gimp_metadata_deserialize().

    """
    return call_api(ctx, 'Gimp.Metadata.serialize', args=[])

@mcp.tool()
def Gimp_Metadata_set_bits_per_sample(ctx: Context, bits_per_sample: int) -> str:
    """Sets Exif.Image.BitsPerSample on metadata.

    :param bits_per_sample: Bits per pixel, per component.
    """
    return call_api(ctx, 'Gimp.Metadata.set_bits_per_sample', args=[bits_per_sample])

@mcp.tool()
def Gimp_Metadata_set_colorspace(ctx: Context, colorspace: str) -> str:
    """Sets Exif.Photo.ColorSpace, Xmp.exif.ColorSpace,
Exif.Iop.InteroperabilityIndex, Exif.Nikon3.ColorSpace,
Exif.Canon.ColorSpace of metadata.

    :param colorspace: The color space.
    """
    return call_api(ctx, 'Gimp.Metadata.set_colorspace', args=[colorspace])

@mcp.tool()
def Gimp_Metadata_set_creation_date(ctx: Context, datetime: str) -> str:
    """Sets Iptc.Application2.DateCreated, Iptc.Application2.TimeCreated,
Exif.Image.DateTime, Exif.Image.DateTimeOriginal,
Exif.Photo.DateTimeOriginal, Exif.Photo.DateTimeDigitized,
Exif.Photo.OffsetTime, Exif.Photo.OffsetTimeOriginal,
Exif.Photo.OffsetTimeDigitized, Xmp.xmp.CreateDate, Xmp.xmp.ModifyDate,
Xmp.xmp.MetadataDate, Xmp.photoshop.DateCreated of metadata.

    :param datetime: A GDateTime value.
    """
    return call_api(ctx, 'Gimp.Metadata.set_creation_date', args=[datetime])

@mcp.tool()
def Gimp_Metadata_set_from_exif(ctx: Context, exif_data: str, exif_data_length: int, error: str = None) -> str:
    """Sets the tags from a piece of Exif data on metadata.

    :param exif_data: The blob of Exif data to set.
    :param exif_data_length: Length of exif_data, in bytes.
    :param error: No description available.
    """
    return call_api(ctx, 'Gimp.Metadata.set_from_exif', args=[exif_data, exif_data_length, error])

@mcp.tool()
def Gimp_Metadata_set_from_iptc(ctx: Context, iptc_data: str, iptc_data_length: int, error: str = None) -> str:
    """Sets the tags from a piece of IPTC data on metadata.

    :param iptc_data: The blob of Iptc data to set.
    :param iptc_data_length: Length of iptc_data, in bytes.
    :param error: No description available.
    """
    return call_api(ctx, 'Gimp.Metadata.set_from_iptc', args=[iptc_data, iptc_data_length, error])

@mcp.tool()
def Gimp_Metadata_set_from_xmp(ctx: Context, xmp_data: str, xmp_data_length: int, error: str = None) -> str:
    """Sets the tags from a piece of XMP data on metadata.

    :param xmp_data: The blob of XMP data to set.
    :param xmp_data_length: Length of xmp_data, in bytes.
    :param error: No description available.
    """
    return call_api(ctx, 'Gimp.Metadata.set_from_xmp', args=[xmp_data, xmp_data_length, error])

@mcp.tool()
def Gimp_Metadata_set_pixel_size(ctx: Context, width: int, height: int) -> str:
    """Sets Exif.Image.ImageWidth and Exif.Image.ImageLength on metadata.
If already present, also sets Exif.Photo.PixelXDimension and Exif.Photo.PixelYDimension.

    :param width: Width in pixels.
    :param height: Height in pixels.
    """
    return call_api(ctx, 'Gimp.Metadata.set_pixel_size', args=[width, height])

@mcp.tool()
def Gimp_Metadata_set_resolution(ctx: Context, xres: float, yres: float, unit: str) -> str:
    """Sets Exif.Image.XResolution, Exif.Image.YResolution and
Exif.Image.ResolutionUnit of metadata.

    :param xres: The image’s X Resolution, in ppi.
    :param yres: The image’s Y Resolution, in ppi.
    :param unit: The image’s unit.
    """
    return call_api(ctx, 'Gimp.Metadata.set_resolution', args=[xres, yres, unit])

@mcp.tool()
def Gimp_Module_get_auto_load(ctx: Context) -> str:
    """Returns whether this module in automatically loaded at startup.

    """
    return call_api(ctx, 'Gimp.Module.get_auto_load', args=[])

@mcp.tool()
def Gimp_Module_get_file(ctx: Context) -> str:
    """Returns GFile of the module,

    """
    return call_api(ctx, 'Gimp.Module.get_file', args=[])

@mcp.tool()
def Gimp_Module_get_info(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.Module.get_info', args=[])

@mcp.tool()
def Gimp_Module_get_last_error(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.Module.get_last_error', args=[])

@mcp.tool()
def Gimp_Module_get_state(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.Module.get_state', args=[])

@mcp.tool()
def Gimp_Module_is_loaded(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.Module.is_loaded', args=[])

@mcp.tool()
def Gimp_Module_is_on_disk(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.Module.is_on_disk', args=[])

@mcp.tool()
def Gimp_Module_query_module(ctx: Context) -> str:
    """Queries the module without actually registering any of the types it
may implement. After successful query, gimp_module_get_info() can be
used to get further about the module.

    """
    return call_api(ctx, 'Gimp.Module.query_module', args=[])

@mcp.tool()
def Gimp_Module_set_auto_load(ctx: Context, auto_load: bool) -> str:
    """Sets the auto_load property of the module.

    :param auto_load: Pass FALSE to exclude this module from auto-loading.
    """
    return call_api(ctx, 'Gimp.Module.set_auto_load', args=[auto_load])

@mcp.tool()
def Gimp_ModuleDB_get_load_inhibit(ctx: Context) -> str:
    """Return the #G_SEARCHPATH_SEPARATOR delimited list of module filenames
which are excluded from auto-loading.

    """
    return call_api(ctx, 'Gimp.ModuleDB.get_load_inhibit', args=[])

@mcp.tool()
def Gimp_ModuleDB_get_verbose(ctx: Context) -> str:
    """Returns the ‘verbose’ setting of db.

    """
    return call_api(ctx, 'Gimp.ModuleDB.get_verbose', args=[])

@mcp.tool()
def Gimp_ModuleDB_load(ctx: Context, module_path: str) -> str:
    """Scans the directories contained in module_path and creates a
GimpModule instance for every loadable module contained in the directories.

    :param module_path: A #G_SEARCHPATH_SEPARATOR delimited list of directories
              to load modules from.
    """
    return call_api(ctx, 'Gimp.ModuleDB.load', args=[module_path])

@mcp.tool()
def Gimp_ModuleDB_refresh(ctx: Context, module_path: str) -> str:
    """Does the same as gimp_module_db_load(), plus removes all GimpModule
instances whose modules have been deleted from disk.

    :param module_path: A #G_SEARCHPATH_SEPARATOR delimited list of directories
              to load modules from.
    """
    return call_api(ctx, 'Gimp.ModuleDB.refresh', args=[module_path])

@mcp.tool()
def Gimp_ModuleDB_set_load_inhibit(ctx: Context, load_inhibit: str) -> str:
    """Sets the load_inhibit flag for all GimpModule‘s which are kept
by db (using gimp_module_set_load_inhibit()).

    :param load_inhibit: A #G_SEARCHPATH_SEPARATOR delimited list of module
               filenames to exclude from auto-loading.
    """
    return call_api(ctx, 'Gimp.ModuleDB.set_load_inhibit', args=[load_inhibit])

@mcp.tool()
def Gimp_ModuleDB_set_verbose(ctx: Context, verbose: bool) -> str:
    """Sets the ‘verbose’ setting of db.

    :param verbose: The new ‘verbose’ setting.
    """
    return call_api(ctx, 'Gimp.ModuleDB.set_verbose', args=[verbose])

@mcp.tool()
def Gimp_PDB_dump_to_file(ctx: Context, file: str) -> str:
    """Dumps the current contents of the procedural database

    :param file: The dump file.
    """
    return call_api(ctx, 'Gimp.PDB.dump_to_file', args=[file])

@mcp.tool()
def Gimp_PDB_get_last_error(ctx: Context) -> str:
    """Retrieves the error message from the last procedure call.

    """
    return call_api(ctx, 'Gimp.PDB.get_last_error', args=[])

@mcp.tool()
def Gimp_PDB_get_last_status(ctx: Context) -> str:
    """Retrieves the status from the last procedure call.

    """
    return call_api(ctx, 'Gimp.PDB.get_last_status', args=[])

@mcp.tool()
def Gimp_PDB_lookup_procedure(ctx: Context, procedure_name: str) -> str:
    """This function returns the GimpProcedure which is registered
with procedure_name if it exists, or returns NULL otherwise.

    :param procedure_name: A procedure name.
    """
    return call_api(ctx, 'Gimp.PDB.lookup_procedure', args=[procedure_name])

@mcp.tool()
def Gimp_PDB_procedure_exists(ctx: Context, procedure_name: str) -> str:
    """This function checks if a procedure exists in the procedural database.

    :param procedure_name: A procedure name.
    """
    return call_api(ctx, 'Gimp.PDB.procedure_exists', args=[procedure_name])

@mcp.tool()
def Gimp_PDB_query_procedures(ctx: Context, name: str, blurb: str, help: str, help_id: str, authors: str, copyright: str, date: str, proc_type: str) -> str:
    """Queries the procedural database for its contents using regular
expression matching.

    :param name: The regex for procedure name.
    :param blurb: The regex for procedure blurb.
    :param help: The regex for procedure help.
    :param help_id: The regex for procedure help-id.
    :param authors: The regex for procedure authors.
    :param copyright: The regex for procedure copyright.
    :param date: The regex for procedure date.
    :param proc_type: The regex for procedure type: { ‘Internal GIMP procedure’, ‘GIMP Plug-in’, ‘GIMP Extension’, ‘Temporary Procedure’ }.
    """
    return call_api(ctx, 'Gimp.PDB.query_procedures', args=[name, blurb, help, help_id, authors, copyright, date, proc_type])

@mcp.tool()
def Gimp_PDB_temp_procedure_name(ctx: Context) -> str:
    """Generates a unique temporary PDB name.

    """
    return call_api(ctx, 'Gimp.PDB.temp_procedure_name', args=[])

@mcp.tool()
def Gimp_Palette_add_entry(ctx: Context, entry_name: str = None, color: str, entry_num: int) -> str:
    """Appends an entry to the palette.

    :param entry_name: A name for the entry.
    :param color: The color for the added entry.
    :param entry_num: The index of the added entry.
    """
    return call_api(ctx, 'Gimp.Palette.add_entry', args=[entry_name, color, entry_num])

@mcp.tool()
def Gimp_Palette_delete_entry(ctx: Context, entry_num: int) -> str:
    """Deletes an entry from the palette.

    :param entry_num: The index of the entry to delete.
    """
    return call_api(ctx, 'Gimp.Palette.delete_entry', args=[entry_num])

@mcp.tool()
def Gimp_Palette_get_color_count(ctx: Context) -> str:
    """Get the count of colors in the palette.

    """
    return call_api(ctx, 'Gimp.Palette.get_color_count', args=[])

@mcp.tool()
def Gimp_Palette_get_colormap(ctx: Context, format: str, num_colors: int = None, num_bytes: int = None) -> str:
    """This procedure returns a palette’s colormap as an array of bytes with
all colors converted to a given Babl format.

    :param format: The desired color format.
    :param num_colors: The number of colors in the palette.
    :param num_bytes: The byte-size of the returned value.
    """
    return call_api(ctx, 'Gimp.Palette.get_colormap', args=[format, num_colors, num_bytes])

@mcp.tool()
def Gimp_Palette_get_colors(ctx: Context) -> str:
    """Gets colors in the palette.

    """
    return call_api(ctx, 'Gimp.Palette.get_colors', args=[])

@mcp.tool()
def Gimp_Palette_get_columns(ctx: Context) -> str:
    """Gets the number of columns used to display the palette

    """
    return call_api(ctx, 'Gimp.Palette.get_columns', args=[])

@mcp.tool()
def Gimp_Palette_get_entry_color(ctx: Context, entry_num: int) -> str:
    """Gets the color of an entry in the palette.

    :param entry_num: The index of the entry to get the color of.
    """
    return call_api(ctx, 'Gimp.Palette.get_entry_color', args=[entry_num])

@mcp.tool()
def Gimp_Palette_get_entry_name(ctx: Context, entry_num: int, entry_name: str) -> str:
    """Gets the name of an entry in the palette.

    :param entry_num: The entry to get.
    :param entry_name: The name of the entry.
    """
    return call_api(ctx, 'Gimp.Palette.get_entry_name', args=[entry_num, entry_name])

@mcp.tool()
def Gimp_Palette_set_colormap(ctx: Context, format: str, colormap: int, num_bytes: int) -> str:
    """This procedure sets the entries in the specified palette in one go,
though they must all be in the same format.

    :param format: The desired color format.
colormap (array length=num_bytes): The new colormap values.
    :param colormap: No description available.
    :param num_bytes: The byte-size of colormap.
    """
    return call_api(ctx, 'Gimp.Palette.set_colormap', args=[format, colormap, num_bytes])

@mcp.tool()
def Gimp_Palette_set_columns(ctx: Context, columns: int) -> str:
    """Sets the number of columns used to display the palette

    :param columns: The new number of columns.
    """
    return call_api(ctx, 'Gimp.Palette.set_columns', args=[columns])

@mcp.tool()
def Gimp_Palette_set_entry_color(ctx: Context, entry_num: int, color: str) -> str:
    """Sets the color of an entry in the palette.

    :param entry_num: The entry to get.
    :param color: The new color.
    """
    return call_api(ctx, 'Gimp.Palette.set_entry_color', args=[entry_num, color])

@mcp.tool()
def Gimp_Palette_set_entry_name(ctx: Context, entry_num: int, entry_name: str = None) -> str:
    """Sets the name of an entry in the palette.

    :param entry_num: The entry to get.
    :param entry_name: The new name.
    """
    return call_api(ctx, 'Gimp.Palette.set_entry_name', args=[entry_num, entry_name])

@mcp.tool()
def Gimp_Path_bezier_stroke_conicto(ctx: Context, stroke_id: int, x0: float, y0: float, x1: float, y1: float) -> str:
    """Extends a bezier stroke with a conic bezier spline.

    :param stroke_id: The stroke ID.
    :param x0: The x-coordinate of the control point.
    :param y0: The y-coordinate of the control point.
    :param x1: The x-coordinate of the end point.
    :param y1: The y-coordinate of the end point.
    """
    return call_api(ctx, 'Gimp.Path.bezier_stroke_conicto', args=[stroke_id, x0, y0, x1, y1])

@mcp.tool()
def Gimp_Path_bezier_stroke_cubicto(ctx: Context, stroke_id: int, x0: float, y0: float, x1: float, y1: float, x2: float, y2: float) -> str:
    """Extends a bezier stroke with a cubic bezier spline.

    :param stroke_id: The stroke ID.
    :param x0: The x-coordinate of the first control point.
    :param y0: The y-coordinate of the first control point.
    :param x1: The x-coordinate of the second control point.
    :param y1: The y-coordinate of the second control point.
    :param x2: The x-coordinate of the end point.
    :param y2: The y-coordinate of the end point.
    """
    return call_api(ctx, 'Gimp.Path.bezier_stroke_cubicto', args=[stroke_id, x0, y0, x1, y1, x2, y2])

@mcp.tool()
def Gimp_Path_bezier_stroke_lineto(ctx: Context, stroke_id: int, x0: float, y0: float) -> str:
    """Extends a bezier stroke with a lineto.

    :param stroke_id: The stroke ID.
    :param x0: The x-coordinate of the lineto.
    :param y0: The y-coordinate of the lineto.
    """
    return call_api(ctx, 'Gimp.Path.bezier_stroke_lineto', args=[stroke_id, x0, y0])

@mcp.tool()
def Gimp_Path_bezier_stroke_new_ellipse(ctx: Context, x0: float, y0: float, radius_x: float, radius_y: float, angle: float) -> str:
    """Adds a bezier stroke describing an ellipse the path object.

    :param x0: The x-coordinate of the center.
    :param y0: The y-coordinate of the center.
    :param radius_x: The radius in x direction.
    :param radius_y: The radius in y direction.
    :param angle: The angle the x-axis of the ellipse (radians, counterclockwise).
    """
    return call_api(ctx, 'Gimp.Path.bezier_stroke_new_ellipse', args=[x0, y0, radius_x, radius_y, angle])

@mcp.tool()
def Gimp_Path_bezier_stroke_new_moveto(ctx: Context, x0: float, y0: float) -> str:
    """Adds a bezier stroke with a single moveto to the path object.

    :param x0: The x-coordinate of the moveto.
    :param y0: The y-coordinate of the moveto.
    """
    return call_api(ctx, 'Gimp.Path.bezier_stroke_new_moveto', args=[x0, y0])

@mcp.tool()
def Gimp_Path_copy(ctx: Context) -> str:
    """Copy a path object.

    """
    return call_api(ctx, 'Gimp.Path.copy', args=[])

@mcp.tool()
def Gimp_Path_get_strokes(ctx: Context, num_strokes: int) -> str:
    """List the strokes associated with the passed path.

    :param num_strokes: The number of strokes returned.
    """
    return call_api(ctx, 'Gimp.Path.get_strokes', args=[num_strokes])

@mcp.tool()
def Gimp_Path_remove_stroke(ctx: Context, stroke_id: int) -> str:
    """Remove the stroke from a path object.

    :param stroke_id: The stroke ID.
    """
    return call_api(ctx, 'Gimp.Path.remove_stroke', args=[stroke_id])

@mcp.tool()
def Gimp_Path_stroke_close(ctx: Context, stroke_id: int) -> str:
    """Closes the specified stroke.

    :param stroke_id: The stroke ID.
    """
    return call_api(ctx, 'Gimp.Path.stroke_close', args=[stroke_id])

@mcp.tool()
def Gimp_Path_stroke_flip(ctx: Context, stroke_id: int, flip_type: str, axis: float) -> str:
    """Flips the given stroke.

    :param stroke_id: The stroke ID.
    :param flip_type: Flip orientation, either vertical or horizontal.
    :param axis: Axis coordinate about which to flip, in pixels.
    """
    return call_api(ctx, 'Gimp.Path.stroke_flip', args=[stroke_id, flip_type, axis])

@mcp.tool()
def Gimp_Path_stroke_flip_free(ctx: Context, stroke_id: int, x1: float, y1: float, x2: float, y2: float) -> str:
    """Flips the given stroke about an arbitrary axis.

    :param stroke_id: The stroke ID.
    :param x1: X coordinate of the first point of the flipping axis.
    :param y1: Y coordinate of the first point of the flipping axis.
    :param x2: X coordinate of the second point of the flipping axis.
    :param y2: Y coordinate of the second point of the flipping axis.
    """
    return call_api(ctx, 'Gimp.Path.stroke_flip_free', args=[stroke_id, x1, y1, x2, y2])

@mcp.tool()
def Gimp_Path_stroke_get_length(ctx: Context, stroke_id: int, precision: float) -> str:
    """Measure the length of the given stroke.

    :param stroke_id: The stroke ID.
    :param precision: The precision used for approximating straight portions of the stroke.
    """
    return call_api(ctx, 'Gimp.Path.stroke_get_length', args=[stroke_id, precision])

@mcp.tool()
def Gimp_Path_stroke_get_point_at_dist(ctx: Context, stroke_id: int, dist: float, precision: float, x_point: float, y_point: float, slope: float, valid: bool) -> str:
    """Get point at a specified distance along the stroke.

    :param stroke_id: The stroke ID.
    :param dist: The given distance.
    :param precision: The precision used for the approximation.
    :param x_point: The x position of the point.
    :param y_point: The y position of the point.
    :param slope: The slope (dy / dx) at the specified point.
    :param valid: Indicator for the validity of the returned data.
    """
    return call_api(ctx, 'Gimp.Path.stroke_get_point_at_dist', args=[stroke_id, dist, precision, x_point, y_point, slope, valid])

@mcp.tool()
def Gimp_Path_stroke_get_points(ctx: Context, stroke_id: int, num_points: int, controlpoints: str, closed: bool) -> str:
    """Returns the control points of a stroke.

    :param stroke_id: The stroke ID.
    :param num_points: The number of floats returned.
    :param controlpoints: List of the control points for the stroke (x0, y0, x1, y1, …).
    :param closed: Whether the stroke is closed or not.
    """
    return call_api(ctx, 'Gimp.Path.stroke_get_points', args=[stroke_id, num_points, controlpoints, closed])

@mcp.tool()
def Gimp_Path_stroke_interpolate(ctx: Context, stroke_id: int, precision: float, num_coords: int, closed: bool) -> str:
    """Returns polygonal approximation of the stroke.

    :param stroke_id: The stroke ID.
    :param precision: The precision used for the approximation.
    :param num_coords: The number of floats returned.
    :param closed: Whether the stroke is closed or not.
    """
    return call_api(ctx, 'Gimp.Path.stroke_interpolate', args=[stroke_id, precision, num_coords, closed])

@mcp.tool()
def Gimp_Path_stroke_new_from_points(ctx: Context, type: str, num_points: int, controlpoints: str, closed: bool) -> str:
    """Adds a stroke of a given type to the path object.

    :param type: Type of the stroke (always GIMP_PATH_STROKE_TYPE_BEZIER for now).
    :param num_points: The number of elements in the array, i.e. the number of controlpoints in the stroke * 2 (x- and y-coordinate).
    :param controlpoints: List of the x- and y-coordinates of the control points.
    :param closed: Whether the stroke is to be closed or not.
    """
    return call_api(ctx, 'Gimp.Path.stroke_new_from_points', args=[type, num_points, controlpoints, closed])

@mcp.tool()
def Gimp_Path_stroke_reverse(ctx: Context, stroke_id: int) -> str:
    """Reverses the specified stroke.

    :param stroke_id: The stroke ID.
    """
    return call_api(ctx, 'Gimp.Path.stroke_reverse', args=[stroke_id])

@mcp.tool()
def Gimp_Path_stroke_rotate(ctx: Context, stroke_id: int, center_x: float, center_y: float, angle: float) -> str:
    """Rotates the given stroke.

    :param stroke_id: The stroke ID.
    :param center_x: X coordinate of the rotation center.
    :param center_y: Y coordinate of the rotation center.
    :param angle: Angle to rotate about.
    """
    return call_api(ctx, 'Gimp.Path.stroke_rotate', args=[stroke_id, center_x, center_y, angle])

@mcp.tool()
def Gimp_Path_stroke_scale(ctx: Context, stroke_id: int, scale_x: float, scale_y: float) -> str:
    """Scales the given stroke.

    :param stroke_id: The stroke ID.
    :param scale_x: Scale factor in x direction.
    :param scale_y: Scale factor in y direction.
    """
    return call_api(ctx, 'Gimp.Path.stroke_scale', args=[stroke_id, scale_x, scale_y])

@mcp.tool()
def Gimp_Path_stroke_translate(ctx: Context, stroke_id: int, off_x: float, off_y: float) -> str:
    """Translate the given stroke.

    :param stroke_id: The stroke ID.
    :param off_x: Offset in x direction.
    :param off_y: Offset in y direction.
    """
    return call_api(ctx, 'Gimp.Path.stroke_translate', args=[stroke_id, off_x, off_y])

@mcp.tool()
def Gimp_Pattern_get_buffer(ctx: Context, max_width: int, max_height: int, format: str) -> str:
    """Gets pixel data of the pattern within the bounding box specified by max_width
and max_height. The data will be scaled down so that it fits within this
size without changing its ratio. If the pattern is smaller than this size to
begin with, it will not be scaled up.

    :param max_width: A maximum width for the returned buffer.
    :param max_height: A maximum height for the returned buffer.
    :param format: An optional Babl format.
    """
    return call_api(ctx, 'Gimp.Pattern.get_buffer', args=[max_width, max_height, format])

@mcp.tool()
def Gimp_Pattern_get_info(ctx: Context, width: int, height: int, bpp: int) -> str:
    """Gets information about the pattern.

    :param width: The pattern width.
    :param height: The pattern height.
    :param bpp: The pattern bpp.
    """
    return call_api(ctx, 'Gimp.Pattern.get_info', args=[width, height, bpp])

@mcp.tool()
def Gimp_PlugIn_add_menu_branch(ctx: Context, menu_path: str, menu_label: str) -> str:
    """Add a new sub-menu to the GIMP menus.

    :param menu_path: The sub-menu’s menu path.
    :param menu_label: The menu label of the sub-menu.
    """
    return call_api(ctx, 'Gimp.PlugIn.add_menu_branch', args=[menu_path, menu_label])

@mcp.tool()
def Gimp_PlugIn_add_temp_procedure(ctx: Context, procedure: str) -> str:
    """This function adds a temporary procedure to plug_in. It is usually
called from a GIMP_PDB_PROC_TYPE_PERSISTENT procedure’s
Gimp.ProcedureClass.run.

    :param procedure: A GimpProcedure of type GIMP_PDB_PROC_TYPE_TEMPORARY.
    """
    return call_api(ctx, 'Gimp.PlugIn.add_temp_procedure', args=[procedure])

@mcp.tool()
def Gimp_PlugIn_get_pdb_error_handler(ctx: Context) -> str:
    """Retrieves the active error handler for procedure calls.

    """
    return call_api(ctx, 'Gimp.PlugIn.get_pdb_error_handler', args=[])

@mcp.tool()
def Gimp_PlugIn_get_temp_procedure(ctx: Context, procedure_name: str) -> str:
    """This function retrieves a temporary procedure from plug_in by the
procedure’s procedure_name.

    :param procedure_name: The name of a GimpProcedure added to plug_in.
    """
    return call_api(ctx, 'Gimp.PlugIn.get_temp_procedure', args=[procedure_name])

@mcp.tool()
def Gimp_PlugIn_get_temp_procedures(ctx: Context) -> str:
    """This function retrieves the list of temporary procedure of plug_in as
added with gimp_plug_in_add_temp_procedure().

    """
    return call_api(ctx, 'Gimp.PlugIn.get_temp_procedures', args=[])

@mcp.tool()
def Gimp_PlugIn_persistent_enable(ctx: Context) -> str:
    """Enables asynchronous processing of messages from the main GIMP application.

    """
    return call_api(ctx, 'Gimp.PlugIn.persistent_enable', args=[])

@mcp.tool()
def Gimp_PlugIn_persistent_process(ctx: Context, timeout: int) -> str:
    """Processes one message sent by GIMP and returns.

    :param timeout: The timeout (in ms) to use for the select() call.
    """
    return call_api(ctx, 'Gimp.PlugIn.persistent_process', args=[timeout])

@mcp.tool()
def Gimp_PlugIn_remove_temp_procedure(ctx: Context, procedure_name: str) -> str:
    """This function removes a temporary procedure from plug_in by the
procedure’s procedure_name.

    :param procedure_name: The name of a GimpProcedure added to plug_in.
    """
    return call_api(ctx, 'Gimp.PlugIn.remove_temp_procedure', args=[procedure_name])

@mcp.tool()
def Gimp_PlugIn_set_help_domain(ctx: Context, domain_name: str, domain_uri: str) -> str:
    """Set a help domain and path for the plug_in.

    :param domain_name: The XML namespace of the plug-in’s help pages.
    :param domain_uri: The root URI of the plug-in’s help pages.
    """
    return call_api(ctx, 'Gimp.PlugIn.set_help_domain', args=[domain_name, domain_uri])

@mcp.tool()
def Gimp_PlugIn_set_pdb_error_handler(ctx: Context, handler: str) -> str:
    """Sets an error handler for procedure calls.

    :param handler: Who is responsible for handling procedure call errors.
    """
    return call_api(ctx, 'Gimp.PlugIn.set_pdb_error_handler', args=[handler])

@mcp.tool()
def Gimp_Procedure_add_boolean_argument(ctx: Context, name: str, nick: str, blurb: str = None, value: bool, flags: str) -> str:
    """Add a new boolean argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param value: The default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_boolean_argument', args=[name, nick, blurb, value, flags])

@mcp.tool()
def Gimp_Procedure_add_boolean_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, value: bool, flags: str) -> str:
    """Add a new boolean auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param value: The default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_boolean_aux_argument', args=[name, nick, blurb, value, flags])

@mcp.tool()
def Gimp_Procedure_add_boolean_return_value(ctx: Context, name: str, nick: str, blurb: str = None, value: bool, flags: str) -> str:
    """Add a new boolean return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param value: The default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_boolean_return_value', args=[name, nick, blurb, value, flags])

@mcp.tool()
def Gimp_Procedure_add_brush_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool = None, default_value: str = None, default_to_context: bool, flags: str) -> str:
    """Add a new GimpBrush argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether NULL is a valid value.
    :param default_value: Default value.
    :param default_to_context: Use the context’s brush as default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_brush_argument', args=[name, nick, blurb, none_ok, default_value, default_to_context, flags])

@mcp.tool()
def Gimp_Procedure_add_brush_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, default_value: str = None, default_to_context: bool, flags: str) -> str:
    """Add a new GimpBrush auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param default_value: Default value.
    :param default_to_context: Use the context’s brush as default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_brush_aux_argument', args=[name, nick, blurb, default_value, default_to_context, flags])

@mcp.tool()
def Gimp_Procedure_add_brush_return_value(ctx: Context, name: str, nick: str, blurb: str = None, flags: str) -> str:
    """Add a new GimpBrush return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_brush_return_value', args=[name, nick, blurb, flags])

@mcp.tool()
def Gimp_Procedure_add_bytes_argument(ctx: Context, name: str, nick: str, blurb: str = None, flags: str) -> str:
    """Add a new GBytes argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_bytes_argument', args=[name, nick, blurb, flags])

@mcp.tool()
def Gimp_Procedure_add_bytes_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, flags: str) -> str:
    """Add a new GBytes auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_bytes_aux_argument', args=[name, nick, blurb, flags])

@mcp.tool()
def Gimp_Procedure_add_bytes_return_value(ctx: Context, name: str, nick: str, blurb: str = None, flags: str) -> str:
    """Add a new GBytes return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_bytes_return_value', args=[name, nick, blurb, flags])

@mcp.tool()
def Gimp_Procedure_add_channel_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpChannel argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_channel_argument', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_channel_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpChannel auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_channel_aux_argument', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_channel_return_value(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpChannel return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_channel_return_value', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_choice_argument(ctx: Context, name: str, nick: str, blurb: str = None, choice: str, value: str, flags: str) -> str:
    """Add a new GimpChoice argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param choice: The GimpChoice.
    :param value: The default value for GimpChoice.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_choice_argument', args=[name, nick, blurb, choice, value, flags])

@mcp.tool()
def Gimp_Procedure_add_choice_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, choice: str, value: str, flags: str) -> str:
    """Add a new GimpChoice auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param choice: The GimpChoice.
    :param value: The default value for GimpChoice.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_choice_aux_argument', args=[name, nick, blurb, choice, value, flags])

@mcp.tool()
def Gimp_Procedure_add_choice_return_value(ctx: Context, name: str, nick: str, blurb: str = None, choice: str, value: str, flags: str) -> str:
    """Add a new GimpChoice return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param choice: The GimpChoice.
    :param value: The default value for GimpChoice.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_choice_return_value', args=[name, nick, blurb, choice, value, flags])

@mcp.tool()
def Gimp_Procedure_add_color_argument(ctx: Context, name: str, nick: str, blurb: str = None, has_alpha: bool, value: str, flags: str) -> str:
    """Add a new GeglColor argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param has_alpha: Whether the argument has transparency.
    :param value: The default GeglColor value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_color_argument', args=[name, nick, blurb, has_alpha, value, flags])

@mcp.tool()
def Gimp_Procedure_add_color_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, has_alpha: bool, value: str, flags: str) -> str:
    """Add a new GeglColor auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param has_alpha: Whether the argument has transparency.
    :param value: The default GeglColor value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_color_aux_argument', args=[name, nick, blurb, has_alpha, value, flags])

@mcp.tool()
def Gimp_Procedure_add_color_from_string_argument(ctx: Context, name: str, nick: str, blurb: str = None, has_alpha: bool, value: str, flags: str) -> str:
    """Add a new GeglColor argument to procedure from a string representation.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param has_alpha: Whether the argument has transparency.
    :param value: The default GeglColor value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_color_from_string_argument', args=[name, nick, blurb, has_alpha, value, flags])

@mcp.tool()
def Gimp_Procedure_add_color_from_string_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, has_alpha: bool, value: str, flags: str) -> str:
    """Add a new GeglColor auxiliary argument to procedure from a string representation.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param has_alpha: Whether the argument has transparency.
    :param value: The default GeglColor value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_color_from_string_aux_argument', args=[name, nick, blurb, has_alpha, value, flags])

@mcp.tool()
def Gimp_Procedure_add_color_from_string_return_value(ctx: Context, name: str, nick: str, blurb: str = None, has_alpha: bool, value: str, flags: str) -> str:
    """Add a new GeglColor return value to procedure from a string representation.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param has_alpha: Whether the argument has transparency.
    :param value: The default GeglColor value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_color_from_string_return_value', args=[name, nick, blurb, has_alpha, value, flags])

@mcp.tool()
def Gimp_Procedure_add_color_return_value(ctx: Context, name: str, nick: str, blurb: str = None, has_alpha: bool, value: str, flags: str) -> str:
    """Add a new GeglColor return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param has_alpha: Whether the argument has transparency.
    :param value: The default GeglColor value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_color_return_value', args=[name, nick, blurb, has_alpha, value, flags])

@mcp.tool()
def Gimp_Procedure_add_core_object_array_argument(ctx: Context, name: str, nick: str, blurb: str = None, object_type: str, flags: str) -> str:
    """Add a new object array argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
object_type  the type of object stored in the array.
    :param object_type: No description available.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_core_object_array_argument', args=[name, nick, blurb, object_type, flags])

@mcp.tool()
def Gimp_Procedure_add_core_object_array_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, object_type: str, flags: str) -> str:
    """Add a new object array auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
object_type  the type of object stored in the array.
    :param object_type: No description available.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_core_object_array_aux_argument', args=[name, nick, blurb, object_type, flags])

@mcp.tool()
def Gimp_Procedure_add_core_object_array_return_value(ctx: Context, name: str, nick: str, blurb: str = None, object_type: str, flags: str) -> str:
    """Add a new object array return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
object_type  the type of object stored in the array.
    :param object_type: No description available.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_core_object_array_return_value', args=[name, nick, blurb, object_type, flags])

@mcp.tool()
def Gimp_Procedure_add_display_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpDisplay argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_display_argument', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_display_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpDisplay auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_display_aux_argument', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_display_return_value(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpDisplay return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_display_return_value', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_double_argument(ctx: Context, name: str, nick: str, blurb: str = None, min: float, max: float, value: float, flags: str) -> str:
    """Add a new floating-point in double precision argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param min: The minimum value for this argument.
    :param max: The maximum value for this argument.
    :param value: The default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_double_argument', args=[name, nick, blurb, min, max, value, flags])

@mcp.tool()
def Gimp_Procedure_add_double_array_argument(ctx: Context, name: str, nick: str, blurb: str = None, flags: str) -> str:
    """Add a new double array argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_double_array_argument', args=[name, nick, blurb, flags])

@mcp.tool()
def Gimp_Procedure_add_double_array_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, flags: str) -> str:
    """Add a new double array auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_double_array_aux_argument', args=[name, nick, blurb, flags])

@mcp.tool()
def Gimp_Procedure_add_double_array_return_value(ctx: Context, name: str, nick: str, blurb: str = None, flags: str) -> str:
    """Add a new double array return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_double_array_return_value', args=[name, nick, blurb, flags])

@mcp.tool()
def Gimp_Procedure_add_double_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, min: float, max: float, value: float, flags: str) -> str:
    """Add a new floating-point in double precision auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param min: The minimum value for this argument.
    :param max: The maximum value for this argument.
    :param value: The default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_double_aux_argument', args=[name, nick, blurb, min, max, value, flags])

@mcp.tool()
def Gimp_Procedure_add_double_return_value(ctx: Context, name: str, nick: str, blurb: str = None, min: float, max: float, value: float, flags: str) -> str:
    """Add a new floating-point in double precision return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param min: The minimum value for this argument.
    :param max: The maximum value for this argument.
    :param value: The default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_double_return_value', args=[name, nick, blurb, min, max, value, flags])

@mcp.tool()
def Gimp_Procedure_add_drawable_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpDrawable argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_drawable_argument', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_drawable_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpDrawable auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_drawable_aux_argument', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_drawable_return_value(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpDrawable return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_drawable_return_value', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_enum_argument(ctx: Context, name: str, nick: str, blurb: str = None, enum_type: str, value: int, flags: str) -> str:
    """Add a new enum argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param enum_type: The GType for this argument.
    :param value: The default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_enum_argument', args=[name, nick, blurb, enum_type, value, flags])

@mcp.tool()
def Gimp_Procedure_add_enum_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, enum_type: str, value: int, flags: str) -> str:
    """Add a new enum auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param enum_type: The GType for this argument.
    :param value: The default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_enum_aux_argument', args=[name, nick, blurb, enum_type, value, flags])

@mcp.tool()
def Gimp_Procedure_add_enum_return_value(ctx: Context, name: str, nick: str, blurb: str = None, enum_type: str, value: int, flags: str) -> str:
    """Add a new enum return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param enum_type: The GType for this argument.
    :param value: The default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_enum_return_value', args=[name, nick, blurb, enum_type, value, flags])

@mcp.tool()
def Gimp_Procedure_add_file_argument(ctx: Context, name: str, nick: str, blurb: str = None, action: str, none_ok: bool = None, default_file: str = None, flags: str) -> str:
    """Add a new GFile argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param action: The type of file to expect.
    :param none_ok: Whether NULL is allowed.
    :param default_file: File to use if none is assigned.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_file_argument', args=[name, nick, blurb, action, none_ok, default_file, flags])

@mcp.tool()
def Gimp_Procedure_add_file_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, action: str, none_ok: bool = None, default_file: str = None, flags: str) -> str:
    """Add a new GFile auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param action: The type of file to expect.
    :param none_ok: Whether NULL is allowed.
    :param default_file: File to use if none is assigned.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_file_aux_argument', args=[name, nick, blurb, action, none_ok, default_file, flags])

@mcp.tool()
def Gimp_Procedure_add_file_return_value(ctx: Context, name: str, nick: str, blurb: str = None, flags: str) -> str:
    """Add a new GFile return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_file_return_value', args=[name, nick, blurb, flags])

@mcp.tool()
def Gimp_Procedure_add_font_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool = None, default_value: str = None, default_to_context: bool, flags: str) -> str:
    """Add a new GimpFont argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether NULL is a valid value.
    :param default_value: Default value.
    :param default_to_context: Use the context’s font as default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_font_argument', args=[name, nick, blurb, none_ok, default_value, default_to_context, flags])

@mcp.tool()
def Gimp_Procedure_add_font_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, default_value: str = None, default_to_context: bool, flags: str) -> str:
    """Add a new GimpFont auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param default_value: Default value.
    :param default_to_context: Use the context’s font as default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_font_aux_argument', args=[name, nick, blurb, default_value, default_to_context, flags])

@mcp.tool()
def Gimp_Procedure_add_font_return_value(ctx: Context, name: str, nick: str, blurb: str = None, flags: str) -> str:
    """Add a new GimpFont return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_font_return_value', args=[name, nick, blurb, flags])

@mcp.tool()
def Gimp_Procedure_add_gradient_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool = None, default_value: str = None, default_to_context: bool, flags: str) -> str:
    """Add a new GimpGradient argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether NULL is a valid value.
    :param default_value: Default value.
    :param default_to_context: Use the context’s gradient as default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_gradient_argument', args=[name, nick, blurb, none_ok, default_value, default_to_context, flags])

@mcp.tool()
def Gimp_Procedure_add_gradient_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, default_value: str = None, default_to_context: bool, flags: str) -> str:
    """Add a new GimpGradient auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param default_value: Default value.
    :param default_to_context: Use the context’s gradient as default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_gradient_aux_argument', args=[name, nick, blurb, default_value, default_to_context, flags])

@mcp.tool()
def Gimp_Procedure_add_gradient_return_value(ctx: Context, name: str, nick: str, blurb: str = None, flags: str) -> str:
    """Add a new GimpGradient return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_gradient_return_value', args=[name, nick, blurb, flags])

@mcp.tool()
def Gimp_Procedure_add_group_layer_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpGroupLayer argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_group_layer_argument', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_group_layer_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpGroupLayer auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_group_layer_aux_argument', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_group_layer_return_value(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpGroupLayer return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_group_layer_return_value', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_image_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpImage argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_image_argument', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_image_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpImage auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_image_aux_argument', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_image_return_value(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpImage return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_image_return_value', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_int32_array_argument(ctx: Context, name: str, nick: str, blurb: str = None, flags: str) -> str:
    """Add a new integer array argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_int32_array_argument', args=[name, nick, blurb, flags])

@mcp.tool()
def Gimp_Procedure_add_int32_array_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, flags: str) -> str:
    """Add a new integer array auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_int32_array_aux_argument', args=[name, nick, blurb, flags])

@mcp.tool()
def Gimp_Procedure_add_int32_array_return_value(ctx: Context, name: str, nick: str, blurb: str = None, flags: str) -> str:
    """Add a new integer array return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_int32_array_return_value', args=[name, nick, blurb, flags])

@mcp.tool()
def Gimp_Procedure_add_int_argument(ctx: Context, name: str, nick: str, blurb: str = None, min: int, max: int, value: int, flags: str) -> str:
    """Add a new integer argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param min: The minimum value for this argument.
    :param max: The maximum value for this argument.
    :param value: The default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_int_argument', args=[name, nick, blurb, min, max, value, flags])

@mcp.tool()
def Gimp_Procedure_add_int_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, min: int, max: int, value: int, flags: str) -> str:
    """Add a new integer auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param min: The minimum value for this argument.
    :param max: The maximum value for this argument.
    :param value: The default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_int_aux_argument', args=[name, nick, blurb, min, max, value, flags])

@mcp.tool()
def Gimp_Procedure_add_int_return_value(ctx: Context, name: str, nick: str, blurb: str = None, min: int, max: int, value: int, flags: str) -> str:
    """Add a new integer return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param min: The minimum value for this argument.
    :param max: The maximum value for this argument.
    :param value: The default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_int_return_value', args=[name, nick, blurb, min, max, value, flags])

@mcp.tool()
def Gimp_Procedure_add_item_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpItem argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_item_argument', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_item_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpItem auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_item_aux_argument', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_item_return_value(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpItem return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_item_return_value', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_layer_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpLayer argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_layer_argument', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_layer_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpLayer auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_layer_aux_argument', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_layer_mask_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpLayerMask argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_layer_mask_argument', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_layer_mask_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpLayerMask auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_layer_mask_aux_argument', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_layer_mask_return_value(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpLayerMask return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_layer_mask_return_value', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_layer_return_value(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpLayer return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_layer_return_value', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_menu_path(ctx: Context, menu_path: str) -> str:
    """Adds a menu path to the procedure. Only procedures which have a menu
label can add a menu path.

    :param menu_path: The procedure‘s additional menu path.
    """
    return call_api(ctx, 'Gimp.Procedure.add_menu_path', args=[menu_path])

@mcp.tool()
def Gimp_Procedure_add_palette_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool = None, default_value: str = None, default_to_context: bool, flags: str) -> str:
    """Add a new GimpPalette argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether NULL is a valid value.
    :param default_value: Default value.
    :param default_to_context: Use the context’s palette as default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_palette_argument', args=[name, nick, blurb, none_ok, default_value, default_to_context, flags])

@mcp.tool()
def Gimp_Procedure_add_palette_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, default_value: str = None, default_to_context: bool, flags: str) -> str:
    """Add a new GimpPalette auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param default_value: Default value.
    :param default_to_context: Use the context’s palette as default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_palette_aux_argument', args=[name, nick, blurb, default_value, default_to_context, flags])

@mcp.tool()
def Gimp_Procedure_add_palette_return_value(ctx: Context, name: str, nick: str, blurb: str = None, flags: str) -> str:
    """Add a new GimpPalette return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_palette_return_value', args=[name, nick, blurb, flags])

@mcp.tool()
def Gimp_Procedure_add_param_argument(ctx: Context, name: str, nick: str, blurb: str = None, param_type: str, flags: str) -> str:
    """Add a new param argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param param_type: The GPParamType for this argument.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_param_argument', args=[name, nick, blurb, param_type, flags])

@mcp.tool()
def Gimp_Procedure_add_param_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, param_type: str, flags: str) -> str:
    """Add a new param auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param param_type: The GPParamType for this argument.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_param_aux_argument', args=[name, nick, blurb, param_type, flags])

@mcp.tool()
def Gimp_Procedure_add_param_return_value(ctx: Context, name: str, nick: str, blurb: str = None, param_type: str, flags: str) -> str:
    """Add a new param return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param param_type: The GPParamType for this argument.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_param_return_value', args=[name, nick, blurb, param_type, flags])

@mcp.tool()
def Gimp_Procedure_add_parasite_argument(ctx: Context, name: str, nick: str, blurb: str = None, flags: str) -> str:
    """Add a new GimpParasite argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_parasite_argument', args=[name, nick, blurb, flags])

@mcp.tool()
def Gimp_Procedure_add_parasite_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, flags: str) -> str:
    """Add a new GimpParasite auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_parasite_aux_argument', args=[name, nick, blurb, flags])

@mcp.tool()
def Gimp_Procedure_add_parasite_return_value(ctx: Context, name: str, nick: str, blurb: str = None, flags: str) -> str:
    """Add a new GimpParasite return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_parasite_return_value', args=[name, nick, blurb, flags])

@mcp.tool()
def Gimp_Procedure_add_path_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpPath argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_path_argument', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_path_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpPath auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_path_aux_argument', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_path_return_value(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpPath return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_path_return_value', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_pattern_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool = None, default_value: str = None, default_to_context: bool, flags: str) -> str:
    """Add a new GimpPattern argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether NULL is a valid value.
    :param default_value: Default value.
    :param default_to_context: Use the context’s pattern as default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_pattern_argument', args=[name, nick, blurb, none_ok, default_value, default_to_context, flags])

@mcp.tool()
def Gimp_Procedure_add_pattern_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, default_value: str = None, default_to_context: bool, flags: str) -> str:
    """Add a new GimpPattern auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param default_value: Default value.
    :param default_to_context: Use the context’s pattern as default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_pattern_aux_argument', args=[name, nick, blurb, default_value, default_to_context, flags])

@mcp.tool()
def Gimp_Procedure_add_pattern_return_value(ctx: Context, name: str, nick: str, blurb: str = None, flags: str) -> str:
    """Add a new GimpPattern return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_pattern_return_value', args=[name, nick, blurb, flags])

@mcp.tool()
def Gimp_Procedure_add_resource_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool = None, default_value: str = None, flags: str) -> str:
    """Add a new GimpResource argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether NULL is a valid value.
    :param default_value: Default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_resource_argument', args=[name, nick, blurb, none_ok, default_value, flags])

@mcp.tool()
def Gimp_Procedure_add_resource_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, default_value: str = None, flags: str) -> str:
    """Add a new GimpResource auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param default_value: Default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_resource_aux_argument', args=[name, nick, blurb, default_value, flags])

@mcp.tool()
def Gimp_Procedure_add_resource_return_value(ctx: Context, name: str, nick: str, blurb: str = None, flags: str) -> str:
    """Add a new GimpResource return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_resource_return_value', args=[name, nick, blurb, flags])

@mcp.tool()
def Gimp_Procedure_add_selection_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpSelection argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_selection_argument', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_selection_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpSelection auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_selection_aux_argument', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_selection_return_value(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpSelection return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_selection_return_value', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_string_argument(ctx: Context, name: str, nick: str, blurb: str = None, value: str, flags: str) -> str:
    """Add a new string argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param value: The default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_string_argument', args=[name, nick, blurb, value, flags])

@mcp.tool()
def Gimp_Procedure_add_string_array_argument(ctx: Context, name: str, nick: str, blurb: str = None, flags: str) -> str:
    """Add a new string array argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_string_array_argument', args=[name, nick, blurb, flags])

@mcp.tool()
def Gimp_Procedure_add_string_array_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, flags: str) -> str:
    """Add a new string array auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_string_array_aux_argument', args=[name, nick, blurb, flags])

@mcp.tool()
def Gimp_Procedure_add_string_array_return_value(ctx: Context, name: str, nick: str, blurb: str = None, flags: str) -> str:
    """Add a new string array return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_string_array_return_value', args=[name, nick, blurb, flags])

@mcp.tool()
def Gimp_Procedure_add_string_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, value: str, flags: str) -> str:
    """Add a new string auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param value: The default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_string_aux_argument', args=[name, nick, blurb, value, flags])

@mcp.tool()
def Gimp_Procedure_add_string_return_value(ctx: Context, name: str, nick: str, blurb: str = None, value: str, flags: str) -> str:
    """Add a new string return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param value: The default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_string_return_value', args=[name, nick, blurb, value, flags])

@mcp.tool()
def Gimp_Procedure_add_text_layer_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpTextLayer argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_text_layer_argument', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_text_layer_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpTextLayer auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_text_layer_aux_argument', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_text_layer_return_value(ctx: Context, name: str, nick: str, blurb: str = None, none_ok: bool, flags: str) -> str:
    """Add a new GimpTextLayer return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param none_ok: Whether no is a valid value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_text_layer_return_value', args=[name, nick, blurb, none_ok, flags])

@mcp.tool()
def Gimp_Procedure_add_uint_argument(ctx: Context, name: str, nick: str, blurb: str = None, min: int, max: int, value: int, flags: str) -> str:
    """Add a new unsigned integer argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param min: The minimum value for this argument.
    :param max: The maximum value for this argument.
    :param value: The default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_uint_argument', args=[name, nick, blurb, min, max, value, flags])

@mcp.tool()
def Gimp_Procedure_add_uint_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, min: int, max: int, value: int, flags: str) -> str:
    """Add a new unsigned integer auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param min: The minimum value for this argument.
    :param max: The maximum value for this argument.
    :param value: The default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_uint_aux_argument', args=[name, nick, blurb, min, max, value, flags])

@mcp.tool()
def Gimp_Procedure_add_uint_return_value(ctx: Context, name: str, nick: str, blurb: str = None, min: int, max: int, value: int, flags: str) -> str:
    """Add a new unsigned integer return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param min: The minimum value for this argument.
    :param max: The maximum value for this argument.
    :param value: The default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_uint_return_value', args=[name, nick, blurb, min, max, value, flags])

@mcp.tool()
def Gimp_Procedure_add_unit_argument(ctx: Context, name: str, nick: str, blurb: str = None, show_pixels: bool, show_percent: bool, value: str, flags: str) -> str:
    """Add a new GimpUnit argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param show_pixels: Whether to allow pixels as a valid option.
    :param show_percent: Whether to allow percent as a valid option.
    :param value: The default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_unit_argument', args=[name, nick, blurb, show_pixels, show_percent, value, flags])

@mcp.tool()
def Gimp_Procedure_add_unit_aux_argument(ctx: Context, name: str, nick: str, blurb: str = None, show_pixels: bool, show_percent: bool, value: str, flags: str) -> str:
    """Add a new GimpUnit auxiliary argument to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param show_pixels: Whether to allow pixels as a valid option.
    :param show_percent: Whether to allow percent as a valid option.
    :param value: The default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_unit_aux_argument', args=[name, nick, blurb, show_pixels, show_percent, value, flags])

@mcp.tool()
def Gimp_Procedure_add_unit_return_value(ctx: Context, name: str, nick: str, blurb: str = None, show_pixels: bool, show_percent: bool, value: str, flags: str) -> str:
    """Add a new GimpUnit return value to procedure.

    :param name: The name of the argument to be created.
    :param nick: The label used in GimpProcedureDialog.
    :param blurb: A more detailed help description.
    :param show_pixels: Whether to allow pixels as a valid option.
    :param show_percent: Whether to allow percent as a valid option.
    :param value: The default value.
    :param flags: Argument flags.
    """
    return call_api(ctx, 'Gimp.Procedure.add_unit_return_value', args=[name, nick, blurb, show_pixels, show_percent, value, flags])

@mcp.tool()
def Gimp_Procedure_create_config(ctx: Context) -> str:
    """Create a GimpConfig with properties that match procedure‘s arguments, to be
used in gimp_procedure_run_config() method.

    """
    return call_api(ctx, 'Gimp.Procedure.create_config', args=[])

@mcp.tool()
def Gimp_Procedure_find_argument(ctx: Context, name: str) -> str:
    """Searches the procedure‘s arguments for a GParamSpec called name.

    :param name: An argument name.
    """
    return call_api(ctx, 'Gimp.Procedure.find_argument', args=[name])

@mcp.tool()
def Gimp_Procedure_find_aux_argument(ctx: Context, name: str) -> str:
    """Searches the procedure‘s auxiliary arguments for a GParamSpec
called name.

    :param name: An auxiliary argument name.
    """
    return call_api(ctx, 'Gimp.Procedure.find_aux_argument', args=[name])

@mcp.tool()
def Gimp_Procedure_find_return_value(ctx: Context, name: str) -> str:
    """Searches the procedure‘s return values for a GParamSpec called
name.

    :param name: A return value name.
    """
    return call_api(ctx, 'Gimp.Procedure.find_return_value', args=[name])

@mcp.tool()
def Gimp_Procedure_get_argument_sync(ctx: Context, arg_name: str) -> str:
    """Available since: 3.0

    :param arg_name: The name of one of procedure‘s arguments or auxiliary arguments.
    """
    return call_api(ctx, 'Gimp.Procedure.get_argument_sync', args=[arg_name])

@mcp.tool()
def Gimp_Procedure_get_arguments(ctx: Context, n_arguments: int) -> str:
    """Available since: 3.0

    :param n_arguments: Returns the number of arguments.
    """
    return call_api(ctx, 'Gimp.Procedure.get_arguments', args=[n_arguments])

@mcp.tool()
def Gimp_Procedure_get_authors(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.Procedure.get_authors', args=[])

@mcp.tool()
def Gimp_Procedure_get_aux_arguments(ctx: Context, n_arguments: int) -> str:
    """Available since: 3.0

    :param n_arguments: Returns the number of auxiliary arguments.
    """
    return call_api(ctx, 'Gimp.Procedure.get_aux_arguments', args=[n_arguments])

@mcp.tool()
def Gimp_Procedure_get_blurb(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.Procedure.get_blurb', args=[])

@mcp.tool()
def Gimp_Procedure_get_copyright(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.Procedure.get_copyright', args=[])

@mcp.tool()
def Gimp_Procedure_get_date(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.Procedure.get_date', args=[])

@mcp.tool()
def Gimp_Procedure_get_help(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.Procedure.get_help', args=[])

@mcp.tool()
def Gimp_Procedure_get_help_id(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.Procedure.get_help_id', args=[])

@mcp.tool()
def Gimp_Procedure_get_icon_file(ctx: Context) -> str:
    """Gets the file of the icon if one was set for procedure.

    """
    return call_api(ctx, 'Gimp.Procedure.get_icon_file', args=[])

@mcp.tool()
def Gimp_Procedure_get_icon_name(ctx: Context) -> str:
    """Gets the name of the icon if one was set for procedure.

    """
    return call_api(ctx, 'Gimp.Procedure.get_icon_name', args=[])

@mcp.tool()
def Gimp_Procedure_get_icon_pixbuf(ctx: Context) -> str:
    """Gets the GdkPixbuf of the icon if an icon was set this way for
procedure.

    """
    return call_api(ctx, 'Gimp.Procedure.get_icon_pixbuf', args=[])

@mcp.tool()
def Gimp_Procedure_get_icon_type(ctx: Context) -> str:
    """Gets the type of data set as procedure‘s icon. Depending on the
result, you can call the relevant specific function, such as
gimp_procedure_get_icon_name().

    """
    return call_api(ctx, 'Gimp.Procedure.get_icon_type', args=[])

@mcp.tool()
def Gimp_Procedure_get_image_types(ctx: Context) -> str:
    """This function retrieves the list of image types the procedure can
operate on. See gimp_procedure_set_image_types().

    """
    return call_api(ctx, 'Gimp.Procedure.get_image_types', args=[])

@mcp.tool()
def Gimp_Procedure_get_menu_label(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.Procedure.get_menu_label', args=[])

@mcp.tool()
def Gimp_Procedure_get_menu_paths(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.Procedure.get_menu_paths', args=[])

@mcp.tool()
def Gimp_Procedure_get_name(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.Procedure.get_name', args=[])

@mcp.tool()
def Gimp_Procedure_get_plug_in(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.Procedure.get_plug_in', args=[])

@mcp.tool()
def Gimp_Procedure_get_proc_type(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.Procedure.get_proc_type', args=[])

@mcp.tool()
def Gimp_Procedure_get_return_values(ctx: Context, n_return_values: int) -> str:
    """Available since: 3.0

    :param n_return_values: Returns the number of return values.
    """
    return call_api(ctx, 'Gimp.Procedure.get_return_values', args=[n_return_values])

@mcp.tool()
def Gimp_Procedure_get_sensitivity_mask(ctx: Context) -> str:
    """Available since: 3.0

    """
    return call_api(ctx, 'Gimp.Procedure.get_sensitivity_mask', args=[])

@mcp.tool()
def Gimp_Procedure_is_internal(ctx: Context) -> str:
    """Provide the information if procedure is an internal procedure. Only
a procedure looked up in the GimpPDB can be internal.
Procedures created by a plug-in in particular are never internal.

    """
    return call_api(ctx, 'Gimp.Procedure.is_internal', args=[])

@mcp.tool()
def Gimp_Procedure_new_return_values(ctx: Context, status: str, error: str = None) -> str:
    """Format the expected return values from procedures.

    :param status: The success status of the procedure run.
    :param error: 
    """
    return call_api(ctx, 'Gimp.Procedure.new_return_values', args=[status, error])

@mcp.tool()
def Gimp_Procedure_persistent_ready(ctx: Context) -> str:
    """Notify the main GIMP application that the persistent procedure has
been properly initialized and is ready to run.

    """
    return call_api(ctx, 'Gimp.Procedure.persistent_ready', args=[])

@mcp.tool()
def Gimp_Procedure_run(ctx: Context, first_arg_name: str = None, ...: str) -> str:
    """Runs the procedure named procedure_name with arguments given as
list of (name, value) pairs, terminated by NULL.

    :param first_arg_name: The name of an argument of procedure or NULL to
                 run procedure with default arguments.
    :param ...: The value of first_arg_name and any more argument
                 names and values as needed.
    """
    return call_api(ctx, 'Gimp.Procedure.run', args=[first_arg_name, ...])

@mcp.tool()
def Gimp_Procedure_run_config(ctx: Context, config: str = None) -> str:
    """Runs procedure, calling the run_func given in gimp_procedure_new().

    :param config: The procedure‘s arguments.
    """
    return call_api(ctx, 'Gimp.Procedure.run_config', args=[config])

@mcp.tool()
def Gimp_Procedure_run_valist(ctx: Context, first_arg_name: str = None, args: str) -> str:
    """Runs procedure with arguments names and values, given in the order as passed
to gimp_procedure_run().

    :param first_arg_name: The name of an argument of procedure or NULL to
                 run procedure with default arguments.
args            the value of first_arg_name and any more argument
                 names and values as needed.
    :param args: No description available.
    """
    return call_api(ctx, 'Gimp.Procedure.run_valist', args=[first_arg_name, args])

@mcp.tool()
def Gimp_Procedure_set_argument_sync(ctx: Context, arg_name: str, sync: str) -> str:
    """When the procedure’s run() function exits, a GimpProcedure‘s arguments
or auxiliary arguments can be automatically synced with a GimpParasite of
the GimpImage the procedure is running on.

    :param arg_name: The name of one of procedure‘s arguments or auxiliary arguments.
    :param sync: How to sync the argument or auxiliary argument.
    """
    return call_api(ctx, 'Gimp.Procedure.set_argument_sync', args=[arg_name, sync])

@mcp.tool()
def Gimp_Procedure_set_attribution(ctx: Context, authors: str, copyright: str, date: str) -> str:
    """Sets various attribution strings on procedure.

    :param authors: The procedure‘s author(s).
    :param copyright: The procedure‘s copyright.
    :param date: The procedure‘s date (written or published).
    """
    return call_api(ctx, 'Gimp.Procedure.set_attribution', args=[authors, copyright, date])

@mcp.tool()
def Gimp_Procedure_set_documentation(ctx: Context, blurb: str, help: str = None, help_id: str = None) -> str:
    """Sets various documentation strings on procedure:

    :param blurb: The procedure‘s blurb.
    :param help: The procedure‘s help text.
    :param help_id: The procedure‘s help ID.
    """
    return call_api(ctx, 'Gimp.Procedure.set_documentation', args=[blurb, help, help_id])

@mcp.tool()
def Gimp_Procedure_set_icon_file(ctx: Context, file: str = None) -> str:
    """Sets the icon for procedure to the contents of an image file.

    :param file: A GFile pointing to an image file.
    """
    return call_api(ctx, 'Gimp.Procedure.set_icon_file', args=[file])

@mcp.tool()
def Gimp_Procedure_set_icon_name(ctx: Context, icon_name: str = None) -> str:
    """Sets the icon for procedure to the icon referenced by icon_name.

    :param icon_name: An icon name.
    """
    return call_api(ctx, 'Gimp.Procedure.set_icon_name', args=[icon_name])

@mcp.tool()
def Gimp_Procedure_set_icon_pixbuf(ctx: Context, pixbuf: str = None) -> str:
    """Sets the icon for procedure to pixbuf.

    :param pixbuf: A GdkPixbuf.
    """
    return call_api(ctx, 'Gimp.Procedure.set_icon_pixbuf', args=[pixbuf])

@mcp.tool()
def Gimp_Procedure_set_image_types(ctx: Context, image_types: str) -> str:
    """This is a comma separated list of image types, or actually drawable
types, that this procedure can deal with. Wildcards are possible
here, so you could say “RGB*” instead of “RGB, RGBA” or “*” for all
image types.

    :param image_types: The image types this procedure can operate on.
    """
    return call_api(ctx, 'Gimp.Procedure.set_image_types', args=[image_types])

@mcp.tool()
def Gimp_Procedure_set_menu_label(ctx: Context, menu_label: str) -> str:
    """Sets the label to use for the procedure‘s menu entry, The
location(s) where to register in the menu hierarchy is chosen using gimp_procedure_add_menu_path().

    :param menu_label: The procedure‘s menu label.
    """
    return call_api(ctx, 'Gimp.Procedure.set_menu_label', args=[menu_label])

@mcp.tool()
def Gimp_Procedure_set_sensitivity_mask(ctx: Context, sensitivity_mask: int) -> str:
    """Sets the cases when procedure is supposed to be sensitive or not.

    :param sensitivity_mask: A binary mask of GimpProcedureSensitivityMask.
    """
    return call_api(ctx, 'Gimp.Procedure.set_sensitivity_mask', args=[sensitivity_mask])

@mcp.tool()
def Gimp_ProcedureConfig_get_choice_id(ctx: Context, property_name: str) -> str:
    """A utility function which will get the current string value of a
GimpParamSpecChoice property in config and convert it to the
integer ID mapped to this value.
This makes it easy to work with an Enum type locally, within a plug-in code.

    :param property_name: The name of a GimpParamSpecChoice property.
    """
    return call_api(ctx, 'Gimp.ProcedureConfig.get_choice_id', args=[property_name])

@mcp.tool()
def Gimp_ProcedureConfig_get_color_array(ctx: Context, property_name: str) -> str:
    """A function for bindings to get a GimpColorArray property. Getting
these with g_object_get() or g_object_get_property() won’t
work for the time being
so all our boxed array types must be set and get using these
alternative functions instead.

    :param property_name: The name of a GParamSpecBoxed param spec with GimpColorArray value type.
    """
    return call_api(ctx, 'Gimp.ProcedureConfig.get_color_array', args=[property_name])

@mcp.tool()
def Gimp_ProcedureConfig_get_core_object_array(ctx: Context, property_name: str) -> str:
    """A function for bindings to get a GimpCoreObjectArray property. Getting
these with g_object_get() or g_object_get_property() won’t
work for the time being
so all our boxed array types must be set and get using alternative
functions instead.

    :param property_name: The name of a GimpParamSpecCoreObjectArray param spec.
    """
    return call_api(ctx, 'Gimp.ProcedureConfig.get_core_object_array', args=[property_name])

@mcp.tool()
def Gimp_ProcedureConfig_get_procedure(ctx: Context) -> str:
    """This function returns the GimpProcedure which created config, see
gimp_procedure_create_config().

    """
    return call_api(ctx, 'Gimp.ProcedureConfig.get_procedure', args=[])

@mcp.tool()
def Gimp_ProcedureConfig_save_metadata(ctx: Context, exported_image: str, file: str) -> str:
    """Note: There is normally no need to call this function because it’s
already called by GimpExportProcedure after the run() callback.

    :param exported_image: The image that was actually exported.
    :param file: The file exported_image was written to.
    """
    return call_api(ctx, 'Gimp.ProcedureConfig.save_metadata', args=[exported_image, file])

@mcp.tool()
def Gimp_ProcedureConfig_set_color_array(ctx: Context, property_name: str, colors: str, n_colors: int) -> str:
    """A function for bindings to set a GimpColorArray property. Setting
these with g_object_set() or g_object_set_property() won’t
work for the time being
so all our boxed array types must be set and get using these
alternative functions instead.

    :param property_name: The name of a GParamSpecBoxed param spec with GimpColorArray value type.
    :param colors: An array of GeglColor.
    :param n_colors: The numbers of colors.
    """
    return call_api(ctx, 'Gimp.ProcedureConfig.set_color_array', args=[property_name, colors, n_colors])

@mcp.tool()
def Gimp_ProcedureConfig_set_core_object_array(ctx: Context, property_name: str, objects: str, n_objects: int) -> str:
    """A function for bindings to set a GimpCoreObjectArray property. Setting
these with g_object_set() or g_object_set_property() won’t
work for the time being
so all our boxed array types must be set and get using alternative
functions instead.

    :param property_name: The name of a GimpParamSpecCoreObjectArray param spec.
    :param objects: An array of GObjects.
    :param n_objects: The numbers of objects.
    """
    return call_api(ctx, 'Gimp.ProcedureConfig.set_core_object_array', args=[property_name, objects, n_objects])

@mcp.tool()
def Gimp_Resource_delete(ctx: Context) -> str:
    """Deletes a resource.

    """
    return call_api(ctx, 'Gimp.Resource.delete', args=[])

@mcp.tool()
def Gimp_Resource_duplicate(ctx: Context) -> str:
    """Duplicates a resource.

    """
    return call_api(ctx, 'Gimp.Resource.duplicate', args=[])

@mcp.tool()
def Gimp_Resource_get_id(ctx: Context) -> str:
    """mostly internal data and not reusable across sessions.

    """
    return call_api(ctx, 'Gimp.Resource.get_id', args=[])

@mcp.tool()
def Gimp_Resource_get_name(ctx: Context) -> str:
    """Returns the resource’s name.

    """
    return call_api(ctx, 'Gimp.Resource.get_name', args=[])

@mcp.tool()
def Gimp_Resource_is_brush(ctx: Context) -> str:
    """Returns whether the resource is a brush.

    """
    return call_api(ctx, 'Gimp.Resource.is_brush', args=[])

@mcp.tool()
def Gimp_Resource_is_editable(ctx: Context) -> str:
    """Whether the resource can be edited.

    """
    return call_api(ctx, 'Gimp.Resource.is_editable', args=[])

@mcp.tool()
def Gimp_Resource_is_font(ctx: Context) -> str:
    """Returns whether the resource is a font.

    """
    return call_api(ctx, 'Gimp.Resource.is_font', args=[])

@mcp.tool()
def Gimp_Resource_is_gradient(ctx: Context) -> str:
    """Returns whether the resource is a gradient.

    """
    return call_api(ctx, 'Gimp.Resource.is_gradient', args=[])

@mcp.tool()
def Gimp_Resource_is_palette(ctx: Context) -> str:
    """Returns whether the resource is a palette.

    """
    return call_api(ctx, 'Gimp.Resource.is_palette', args=[])

@mcp.tool()
def Gimp_Resource_is_pattern(ctx: Context) -> str:
    """Returns whether the resource is a pattern.

    """
    return call_api(ctx, 'Gimp.Resource.is_pattern', args=[])

@mcp.tool()
def Gimp_Resource_is_valid(ctx: Context) -> str:
    """Returns TRUE if the resource is valid.

    """
    return call_api(ctx, 'Gimp.Resource.is_valid', args=[])

@mcp.tool()
def Gimp_Resource_rename(ctx: Context, new_name: str) -> str:
    """Renames a resource. When the name is in use, renames to a unique name.

    :param new_name: The proposed new name of the resource.
    """
    return call_api(ctx, 'Gimp.Resource.rename', args=[new_name])

@mcp.tool()
def Gimp_TextLayer_get_antialias(ctx: Context) -> str:
    """Check if antialiasing is used in the text layer.

    """
    return call_api(ctx, 'Gimp.TextLayer.get_antialias', args=[])

@mcp.tool()
def Gimp_TextLayer_get_base_direction(ctx: Context) -> str:
    """Get the base direction used for rendering the text layer.

    """
    return call_api(ctx, 'Gimp.TextLayer.get_base_direction', args=[])

@mcp.tool()
def Gimp_TextLayer_get_color(ctx: Context) -> str:
    """Get the color of the text in a text layer.

    """
    return call_api(ctx, 'Gimp.TextLayer.get_color', args=[])

@mcp.tool()
def Gimp_TextLayer_get_font(ctx: Context) -> str:
    """Get the font from a text layer as string.

    """
    return call_api(ctx, 'Gimp.TextLayer.get_font', args=[])

@mcp.tool()
def Gimp_TextLayer_get_font_size(ctx: Context, unit: str) -> str:
    """Get the font size from a text layer.

    :param unit: The unit used for the font size.
    """
    return call_api(ctx, 'Gimp.TextLayer.get_font_size', args=[unit])

@mcp.tool()
def Gimp_TextLayer_get_hint_style(ctx: Context) -> str:
    """Get information about hinting in the specified text layer.

    """
    return call_api(ctx, 'Gimp.TextLayer.get_hint_style', args=[])

@mcp.tool()
def Gimp_TextLayer_get_indent(ctx: Context) -> str:
    """Get the line indentation of text layer.

    """
    return call_api(ctx, 'Gimp.TextLayer.get_indent', args=[])

@mcp.tool()
def Gimp_TextLayer_get_justification(ctx: Context) -> str:
    """Get the text justification information of the text layer.

    """
    return call_api(ctx, 'Gimp.TextLayer.get_justification', args=[])

@mcp.tool()
def Gimp_TextLayer_get_kerning(ctx: Context) -> str:
    """Check if kerning is used in the text layer.

    """
    return call_api(ctx, 'Gimp.TextLayer.get_kerning', args=[])

@mcp.tool()
def Gimp_TextLayer_get_language(ctx: Context) -> str:
    """Get the language used in the text layer.

    """
    return call_api(ctx, 'Gimp.TextLayer.get_language', args=[])

@mcp.tool()
def Gimp_TextLayer_get_letter_spacing(ctx: Context) -> str:
    """Get the letter spacing used in a text layer.

    """
    return call_api(ctx, 'Gimp.TextLayer.get_letter_spacing', args=[])

@mcp.tool()
def Gimp_TextLayer_get_line_spacing(ctx: Context) -> str:
    """Get the spacing between lines of text.

    """
    return call_api(ctx, 'Gimp.TextLayer.get_line_spacing', args=[])

@mcp.tool()
def Gimp_TextLayer_get_markup(ctx: Context) -> str:
    """Get the markup from a text layer as string.

    """
    return call_api(ctx, 'Gimp.TextLayer.get_markup', args=[])

@mcp.tool()
def Gimp_TextLayer_get_text(ctx: Context) -> str:
    """Get the text from a text layer as string.

    """
    return call_api(ctx, 'Gimp.TextLayer.get_text', args=[])

@mcp.tool()
def Gimp_TextLayer_resize(ctx: Context, width: float, height: float) -> str:
    """Resize the box of a text layer.

    :param width: The new box width in pixels.
    :param height: The new box height in pixels.
    """
    return call_api(ctx, 'Gimp.TextLayer.resize', args=[width, height])

@mcp.tool()
def Gimp_TextLayer_set_antialias(ctx: Context, antialias: bool) -> str:
    """Enable/disable anti-aliasing in a text layer.

    :param antialias: Enable/disable antialiasing of the text.
    """
    return call_api(ctx, 'Gimp.TextLayer.set_antialias', args=[antialias])

@mcp.tool()
def Gimp_TextLayer_set_base_direction(ctx: Context, direction: str) -> str:
    """Set the base direction in the text layer.

    :param direction: The base direction of the text.
    """
    return call_api(ctx, 'Gimp.TextLayer.set_base_direction', args=[direction])

@mcp.tool()
def Gimp_TextLayer_set_color(ctx: Context, color: str) -> str:
    """Set the color of the text in the text layer.

    :param color: The color to use for the text.
    """
    return call_api(ctx, 'Gimp.TextLayer.set_color', args=[color])

@mcp.tool()
def Gimp_TextLayer_set_font(ctx: Context, font: str) -> str:
    """Set the font of a text layer.

    :param font: The new font to use.
    """
    return call_api(ctx, 'Gimp.TextLayer.set_font', args=[font])

@mcp.tool()
def Gimp_TextLayer_set_font_size(ctx: Context, font_size: float, unit: str) -> str:
    """Set the font size.

    :param font_size: The font size.
    :param unit: The unit to use for the font size.
    """
    return call_api(ctx, 'Gimp.TextLayer.set_font_size', args=[font_size, unit])

@mcp.tool()
def Gimp_TextLayer_set_hint_style(ctx: Context, style: str) -> str:
    """Control how font outlines are hinted in a text layer.

    :param style: The new hint style.
    """
    return call_api(ctx, 'Gimp.TextLayer.set_hint_style', args=[style])

@mcp.tool()
def Gimp_TextLayer_set_indent(ctx: Context, indent: float) -> str:
    """Set the indentation of the first line in a text layer.

    :param indent: The indentation for the first line.
    """
    return call_api(ctx, 'Gimp.TextLayer.set_indent', args=[indent])

@mcp.tool()
def Gimp_TextLayer_set_justification(ctx: Context, justify: str) -> str:
    """Set the justification of the text in a text layer.

    :param justify: The justification for your text.
    """
    return call_api(ctx, 'Gimp.TextLayer.set_justification', args=[justify])

@mcp.tool()
def Gimp_TextLayer_set_kerning(ctx: Context, kerning: bool) -> str:
    """Enable/disable kerning in a text layer.

    :param kerning: Enable/disable kerning in the text.
    """
    return call_api(ctx, 'Gimp.TextLayer.set_kerning', args=[kerning])

@mcp.tool()
def Gimp_TextLayer_set_language(ctx: Context, language: str) -> str:
    """Set the language of the text layer.

    :param language: The new language to use for the text layer.
    """
    return call_api(ctx, 'Gimp.TextLayer.set_language', args=[language])

@mcp.tool()
def Gimp_TextLayer_set_letter_spacing(ctx: Context, letter_spacing: float) -> str:
    """Adjust the letter spacing in a text layer.

    :param letter_spacing: The additional letter spacing to use.
    """
    return call_api(ctx, 'Gimp.TextLayer.set_letter_spacing', args=[letter_spacing])

@mcp.tool()
def Gimp_TextLayer_set_line_spacing(ctx: Context, line_spacing: float) -> str:
    """Adjust the line spacing in a text layer.

    :param line_spacing: The additional line spacing to use.
    """
    return call_api(ctx, 'Gimp.TextLayer.set_line_spacing', args=[line_spacing])

@mcp.tool()
def Gimp_TextLayer_set_markup(ctx: Context, markup: str) -> str:
    """Set the markup for a text layer from a string.

    :param markup: The new markup to set.
    """
    return call_api(ctx, 'Gimp.TextLayer.set_markup', args=[markup])

@mcp.tool()
def Gimp_TextLayer_set_text(ctx: Context, text: str) -> str:
    """Set the text of a text layer.

    :param text: The new text to set.
    """
    return call_api(ctx, 'Gimp.TextLayer.set_text', args=[text])

@mcp.tool()
def Gimp_Unit_get_abbreviation(ctx: Context) -> str:
    """This function returns the abbreviation of the unit (e.g. “in” for
inches).
It can be used as a short label for the unit in the interface.
For long labels, use gimp_unit_get_name().

    """
    return call_api(ctx, 'Gimp.Unit.get_abbreviation', args=[])

@mcp.tool()
def Gimp_Unit_get_deletion_flag(ctx: Context) -> str:
    """Type: gboolean

    """
    return call_api(ctx, 'Gimp.Unit.get_deletion_flag', args=[])

@mcp.tool()
def Gimp_Unit_get_digits(ctx: Context) -> str:
    """Returns the number of digits set for unit.
Built-in units’ accuracy is approximately the same as an inch with
two digits. User-defined units can suggest a different accuracy.

    """
    return call_api(ctx, 'Gimp.Unit.get_digits', args=[])

@mcp.tool()
def Gimp_Unit_get_factor(ctx: Context) -> str:
    """A GimpUnit‘s factor is defined to be:

    """
    return call_api(ctx, 'Gimp.Unit.get_factor', args=[])

@mcp.tool()
def Gimp_Unit_get_id(ctx: Context) -> str:
    """The ID can be used to retrieve the unit with gimp_unit_get_by_id().

    """
    return call_api(ctx, 'Gimp.Unit.get_id', args=[])

@mcp.tool()
def Gimp_Unit_get_name(ctx: Context) -> str:
    """This function returns the usual name of the unit (e.g. “inches”).
It can be used as the long label for the unit in the interface.
For short labels, use gimp_unit_get_abbreviation().

    """
    return call_api(ctx, 'Gimp.Unit.get_name', args=[])

@mcp.tool()
def Gimp_Unit_get_scaled_digits(ctx: Context, resolution: float) -> str:
    """Returns the number of digits a unit field should provide to get
enough accuracy so that every pixel position shows a different
value from neighboring pixels.

    :param resolution: The resolution in PPI.
    """
    return call_api(ctx, 'Gimp.Unit.get_scaled_digits', args=[resolution])

@mcp.tool()
def Gimp_Unit_get_symbol(ctx: Context) -> str:
    """This is e.g. “”” for UNIT_INCH.

    """
    return call_api(ctx, 'Gimp.Unit.get_symbol', args=[])

@mcp.tool()
def Gimp_Unit_is_built_in(ctx: Context) -> str:
    """Returns whether the unit is built-in.

    """
    return call_api(ctx, 'Gimp.Unit.is_built_in', args=[])

@mcp.tool()
def Gimp_Unit_is_metric(ctx: Context) -> str:
    """Checks if the given unit is metric. A simplistic test is used
that looks at the unit’s factor and checks if it is 2.54 multiplied
by some common powers of 10. Currently it checks for mm, cm, dm, m.

    """
    return call_api(ctx, 'Gimp.Unit.is_metric', args=[])

@mcp.tool()
def Gimp_Unit_set_deletion_flag(ctx: Context, deletion_flag: bool) -> str:
    """Sets a GimpUnit‘s deletion_flag. If the deletion_flag of a unit is
TRUE when GIMP exits, this unit will not be saved in the users’s
“unitrc” file.

    :param deletion_flag: The new deletion_flag.
    """
    return call_api(ctx, 'Gimp.Unit.set_deletion_flag', args=[deletion_flag])

@mcp.tool()
def Gimp_VectorLoadProcedure_extract_dimensions(ctx: Context, file: str, data: str, error: str = None) -> str:
    """Extracts native or suggested dimensions from file, which must be a vector
file in the right format supported by procedure. It is considered a
programming error to pass a file of invalid format.

    :param file: A GFile which can be processed by procedure.
    :param data: The returned dimension data.
    :param error: No description available.
    """
    return call_api(ctx, 'Gimp.VectorLoadProcedure.extract_dimensions', args=[file, data, error])

def main():
    mcp.run()

if __name__ == '__main__':
    main()
