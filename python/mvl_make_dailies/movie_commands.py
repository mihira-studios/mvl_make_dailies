

import os
import sys  
import subprocess
import tempfile
import argparse
import json
import shlex
from mvl_make_dailies.common_utils import (get_python_package_path, get_nuke_executable_path, 
                                           gather_frame_range, logger, 
                                           is_valid_frame_range, slate_keys, burn_in_keys, reformat_keys, colorspace_keys, writer_keys, read_keys)

from mvl_rezboot import resolver

def escape_json_arg(data):
    return '"' + json.dumps(data).replace('"', '\\"') + '"'

def create_houdini_playblast(args_dict):
    """
    Create a playblast from a Houdini scene.
    This function render a playblast from a Houdini scene, adhering to dailies best practices.
    Args:
        args_dict (dict): Parsed command line arguments.
    """

    from mvl_make_dailies.houdini.HoudiniSceneHandler import HoudiniSceneHandler
    from mvl_make_dailies.houdini.HoudiniRenderManager import HoudiniRenderManager
    from mvl_make_dailies.houdini.RenderStrategy import RopRenderStrategy, FlipbookRenderStrategy

    resolved_strategy = args_dict.get('strategy')

    scene = HoudiniSceneHandler(args_dict.get("input"))
    is_file_loaded  = scene.load_scene() 
    if not is_file_loaded:
        logger.error(f"Failed to load Houdini scene file: {scene.file_path}")
        sys.exit(1) 
    
    if not os.path.exists(scene.file_path):
        logger.error(f"Houdini scene file not found: {scene.file_path}")
        sys.exit(1) 

    if resolved_strategy == "flipbook":
        strategy = FlipbookRenderStrategy(scene)
    elif resolved_strategy == "rop": 
        strategy = RopRenderStrategy(scene)

    manager = HoudiniRenderManager(strategy)
    resolved_camera_path = scene.getCameraPath(args_dict.get("view"))
    if resolved_camera_path is None:
        logger.error("No valid camera found in the scene. Please specify a valid camera path.")
        sys.exit(1)

    logger.info(f"Rendering with camera: {resolved_camera_path}")
    logger.info(f"Output path: {args_dict.get('output')}")
    logger.info(f"Frame range: {args_dict.get('start')} - {args_dict.get('end')}")
    logger.info(f"Resolution: {args_dict.get('resX')} x {args_dict.get('resY')}")

    manager.render(
        camera_path = resolved_camera_path,
        output_path = args_dict.get("output"),
        start_frame = args_dict.get('start'),
        end_frame = args_dict.get('end'),
        res_x = args_dict.get("resX"),
        res_y = args_dict.get("resY"),
        rop_type ="ifd" # or 'ifd' for Mantra
    )

    #hou.hipFile.save(file_name, save_to_recent_files=True)
    scene.save()

def create_movie_from_sequence(args_dict):
    """
    Create a movie from an image sequence using Nuke.
    This function uses Nuke to render a movie from an image sequence, adhering to dailies best practices.
    
    Args:
        args_dict (dict): Dictionary of arguments.
    """
    dcc_name = "nuke"
    try:
        launcher_path = os.path.join(get_python_package_path(), "mvl_make_dailies", "nuke", "main.py")
        if not os.path.exists(launcher_path):
            logger.error(f"Nuke launcher script not found: {launcher_path}")
            sys.exit(1)

        file_sequence_path = args_dict.get("input")
        first_frame = args_dict.get("first")
        last_frame = args_dict.get("last")

        if is_valid_frame_range(first_frame, last_frame):
            frame_range = range(first_frame, last_frame + 1)
        else:
            frame_range = gather_frame_range(os.path.dirname(file_sequence_path))

        slate_start_frame = frame_range.start - 1 if args_dict.get("slate") else frame_range.start
        frame_range = range(slate_start_frame, frame_range.stop)

        mov_file_path = args_dict.get("output")
        if not mov_file_path or not mov_file_path.lower().endswith('.mov'):
            logger.error("Output file must be a .mov file.")
            sys.exit(1)

        # Collect metadata
        slate_data = {k: args_dict[k] for k in slate_keys() if k in args_dict and args_dict[k] is not None}
        burnin_data = {k: args_dict.get(k) for k in burn_in_keys() if k in args_dict}
        colorspace_data = {k: args_dict[k] for k in colorspace_keys() if k in args_dict and args_dict[k] is not None}
        write_data = {k: args_dict[k] for k in writer_keys() if k in args_dict and args_dict[k] is not None}
        reformat_data = {k: args_dict[k] for k in reformat_keys() if k in args_dict and args_dict[k] is not None}

        launcher_args = [
            "--src", f"{file_sequence_path}",
            "--dst", f"{mov_file_path}",
            "--slate", json.dumps(slate_data),
            "--burnin", json.dumps(burnin_data),
            "--reformat", json.dumps(reformat_data),
            "--colorspace",json.dumps(colorspace_data),
            "--write", json.dumps(write_data),
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            for arg in launcher_args:
                f.write(arg + "\n")

            args_file = f.name
            
        cmd = [
            "-F", f"{frame_range.start}-{frame_range.stop}",
            "-x", f"{launcher_path}",
            f'@{args_file}',
        ]

        nuke_command_str = " ".join(cmd)

        try:
            from mvl_rezboot.resolver import Resolver
            nuke_resolver = Resolver(f"nuke {nuke_command_str}")
            nuke_resolver.run()       

        except Exception as e:
             logger.error(f"Failed to launch Nuke subprocess: {e}", exc_info=True)
             sys.exit(1)

    except Exception as e:
        logger.error(f"Nuke movie render script failed: {e}", exc_info=True)
        sys.exit(1)

# Command/Strategy mapping
APP_MODE_COMMANDS = {
    "daily": create_movie_from_sequence,
}