

import os
import sys  
import subprocess
import tempfile
import argparse
import json
from mvl_make_dailies.common_utils import (get_python_package_path, get_nuke_executable_path, 
                                           gather_frame_range, logger, 
                                           is_valid_frame_range, slate_keys, burn_in_keys, reformat_keys, colorspace_keys, writer_keys, read_keys)


 
def create_houdini_playblast(args):
    """
    Create a playblast from a Houdini scene.
    This function render a playblast from a Houdini scene, adhering to dailies best practices.
    Args:
        args (dict): Parsed command line arguments.
    """

    from mvl_make_dailies.houdini.HoudiniSceneHandler import HoudiniSceneHandler
    from mvl_make_dailies.houdini.HoudiniRenderManager import HoudiniRenderManager
    from mvl_make_dailies.houdini.RenderStrategy import RopRenderStrategy, FlipbookRenderStrategy

    data = vars(args)

    resolved_strategy = args.get('strategy')

    scene = HoudiniSceneHandler(args.get("input"))
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
    resolved_camera_path = scene.getCameraPath(args.get("view"))
    if resolved_camera_path is None:
        logger.error("No valid camera found in the scene. Please specify a valid camera path.")
        sys.exit(1)

    logger.info(f"Rendering with camera: {resolved_camera_path}")
    logger.info(f"Output path: {args.get('output')}")
    logger.info(f"Frame range: {args.get('start')} - {args.get('end')}")
    logger.info(f"Resolution: {args.get('resX')} x {args.get('resY')}")

    manager.render(
        camera_path= resolved_camera_path,
        output_path=args.get("output"),
        start_frame= args.get('start'),
        end_frame= args.get('end'),
        res_x=args.get("resX"),
        res_y=args.get("resY"),
        rop_type ="ifd" # or 'ifd' for Mantra
    )

    #hou.hipFile.save(file_name, save_to_recent_files=True)
    scene.save()

def create_movie_from_sequence(args):
    """
    Create a movie from an image sequence using Nuke.
    This function uses Nuke to render a movie from an image sequence, adhering to dailies best practices.
    Args:
        args (argparse.Namespace): Parsed command line arguments.
    """

    logger.info(f"ceate movie from seq : {args}")

    dcc_name = "nuke"
    try:
        launcher_path = os.path.join(get_python_package_path(), "mvl_make_dailies", "nuke", "main.py")
        if not os.path.exists(launcher_path):    
            logger.error(f"Nuke launcher script not found: {launcher_path}")
            sys.exit(1) 

        file_sequence_path = args.input
        if is_valid_frame_range(args.first, args.last):
            frame_range = range(args.first ,args.last)
        else:
            frame_range = gather_frame_range(os.path.dirname(file_sequence_path)) 
        
        mov_file_path = args.output
        if not mov_file_path.lower().endswith(('.mov')):
            logger.error("Output file must be a .mov file.")
            sys.exit(1)

        nuke_exe = get_nuke_executable_path()
        if not nuke_exe and not os.path.exists(nuke_exe):
            logger.error("Nuke executable not found. Please ensure Nuke is installed and the path is set correctly.")
            sys.exit(1)
        
        slate_data = {k: getattr(args, k) for k in slate_keys() if hasattr(args, k) and getattr(args, k) is not None}
        burnin_data = {k: getattr(args, k) for k in burn_in_keys() if hasattr(args, k)}
        colorspace_data = {k: getattr(args, k) for k in colorspace_keys() if hasattr(args, k) and getattr(args, k) is not None}
        write_data = {k: getattr(args, k) for k in writer_keys() if hasattr(args, k) and getattr(args, k) is not None}
        reformat_data = {k: getattr(args, k) for k in reformat_keys() if hasattr(args, k) and getattr(args, k) is not None}

        cmd = [
            nuke_exe,
            "-F", f"{frame_range.start - 1}-{frame_range.stop}", 
            "-x", launcher_path, file_sequence_path, mov_file_path, 
            '--slate', json.dumps(slate_data), 
            '--burnin', json.dumps(burnin_data), 
            '--reformat', json.dumps(reformat_data), 
            '--colorspace', json.dumps(colorspace_data), 
            '--write', json.dumps(write_data), 
        ]
        
        logger.info(f"Running Nuke render command: {cmd}")
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)   
            stdout, stderr = process.communicate()
            return_code = process.returncode
            if return_code != 0:
                logger.error(f"{dcc_name} process exited with non-zero status: {return_code}")
                if stdout:
                    logger.error(f"{dcc_name} STDOUT:\n{stdout}")
                if stderr:
                    logger.error(f"{dcc_name} STDERR:\n{stderr}")
                sys.exit(return_code)
            else:
                logger.info(f"{dcc_name} process completed successfully.")
                sys.exit(0)

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