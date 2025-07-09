# python/movie_generator/maya_movie_utils.py

import maya.cmds as cmds
import os
import datetime
from mvl_make_dailies.common_utils import logger

def playblast_scene(
    output_path,
    start_frame,
    end_frame,
    camera=None,
    width=1920,
    height=1080,
    format='qt', # 'qt', 'avi', etc.
    codec='h264', # For 'qt': 'h264', 'jpeg', 'prores', 'none'
    quality=100, # 0-100
    display_resolution=False,
    off_screen=True # Playblast without showing the viewport
):
    """
    Performs a Maya playblast with specified settings.
    """
    logger.info("Starting Maya Playblast...")
    logger.info(f"Output: {output_path}")
    logger.info(f"Frames: {start_frame}-{end_frame}")
    logger.info(f"Camera: {camera if camera else 'active'}")
    logger.info(f"Resolution: {width}x{height}")
    logger.info(f"Format: {format}, Codec: {codec}, Quality: {quality}")

    # Ensure Maya is in batch mode if off_screen is True and GUI is not present
    if off_screen and not cmds.about(batch=True):
        logger.warning("Running playblast off-screen requires Maya batch mode or a specific graphics setup. May not work reliably in interactive GUI.")

    # Set playback range
    cmds.playbackOptions(minTime=start_frame, maxTime=end_frame, animationStartTime=start_frame, animationEndTime=end_frame)
    logger.info(f"Maya playback range set to {start_frame}-{end_frame}.")

    # Set render global settings for playblast (if needed, e.g. for aspect ratio)
    # This might depend on your workflow, e.g. for render resolution
    # cmds.setAttr("defaultResolution.width", width)
    # cmds.setAttr("defaultResolution.height", height)
    # cmds.setAttr("defaultResolution.lockDeviceAspectRatio", 0)

    # Get the current active camera if none is specified
    if not camera:
        current_panel = cmds.getPanel(withFocus=True)
        if cmds.getPanel(typeOf=current_panel) == "modelPanel":
            camera = cmds.modelPanel(current_panel, query=True, camera=True)
            logger.info(f"Using active camera: {camera}")
        else:
            # Fallback to default persp if no model panel is active
            if cmds.objExists("persp"):
                camera = "persp"
                logger.info(f"No active model panel, defaulting to 'persp' camera.")
            else:
                logger.error("No active camera found and 'persp' does not exist. Cannot playblast.")
                raise RuntimeError("No suitable camera for playblast.")

    if not cmds.objExists(camera):
        logger.error(f"Specified camera '{camera}' does not exist.")
        raise ValueError(f"Camera '{camera}' not found in scene.")

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")

    # Ensure the output filename doesn't include frame padding or extension,
    # as playblast adds it. It needs to be the base name for the output file.
    base_name = os.path.splitext(os.path.basename(output_path))[0]
    output_full_path_no_ext = os.path.join(output_dir, base_name)

    # Perform the playblast
    try:
        cmds.playblast(
            filename=output_full_path_no_ext,
            startTime=start_frame,
            endTime=end_frame,
            width=width,
            height=height,
            format=format,
            quality=quality,
            compression=codec,
            showOrnaments=True, # Show camera gate, resolution gate etc.
            viewer=False, # Don't open playblast viewer
            offScreen=off_screen, # Render without showing the viewport
            percent=100, # Use 100% of the viewport resolution
            displayResolution=display_resolution # Show resolution gate (if True)
            # You might want to toggle specific HUD elements (e.g., cmds.displayRGBColor('hud', 0.5, 0.5, 0.5))
            # or turn off specific display layers before playblasting.
        )
        logger.info(f"Playblast complete: {output_path}")

        # The actual file created by playblast will have the format:
        # <filename>.<frame_number>.<extension> or <filename>.<extension> if it's a movie.
        # It's good practice to get the actual path returned by playblast.
        # Maya 2022+ playblast returns a list of paths. Older versions return the last path.
        # This is tricky as playblast doesn't always return the path reliably,
        # especially for movie formats where it might not pad.
        # For movie formats, it usually creates a single file without frame padding.
        # Let's assume for 'qt' it directly outputs the movie.
        # A more robust check would be to look for the file after playblast.
        expected_output_file = f"{output_full_path_no_ext}.{format}" # This is still an approximation
        if format == 'qt': # For movie output, it should just be filename.ext
            expected_output_file = output_path
        else: # For image sequence output
            expected_output_file = f"{output_full_path_no_ext}.{str(start_frame).zfill(4)}.{format}" # Assuming 4-digit padding

        if os.path.exists(expected_output_file):
            logger.info(f"Verified output file exists: {expected_output_file}")
        else:
            logger.warning(f"Could not verify existence of expected output file: {expected_output_file}")
            logger.warning("Please check Maya's playblast output conventions for the chosen format/codec.")

    except Exception as e:
        logger.error(f"Playblast failed: {e}")
        raise # Re-raise to indicate failure