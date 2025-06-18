

from mvl_make_dailies.common_utils import getPythonPackagePath, getConfigPath, getNukeExecutablePath, gatherFrameRange, logger, isValidFrameRange, isvalidPath
import os
import sys  
import subprocess
import tempfile
import argparse
 
def createMoveFromSequence(args):
    
    dcc_name = "nuke"
    try:
        launcher_path = os.path.join(getPythonPackagePath(), "mvl_make_dailies", "nuke", "main.py")
        if not os.path.exists(launcher_path):    
            logger.error(f"Nuke launcher script not found: {launcher_path}")
            sys.exit(1) 
        
        if not isvalidPath(os.path.dirname(args.input)):
            logger.error(f"Input file sequence path is invalid: {args.input}")
            sys.exit(1)
        if os.path.exists(args.output):
            logger.warning(f"Output file already exists: {args.output}. It will be overwritten.")

        file_sequence_path = args.input
        if isValidFrameRange(args.start, args.end):
            frame_range = range(args.start,args.end)
        else:
            frame_range = gatherFrameRange(os.path.dirname(file_sequence_path)) # This will raise an error if the sequence is invalid
        
        mov_file_path = args.output
        if not mov_file_path.lower().endswith(('.mov')):
            logger.error("Output file must be a .mov file.")
            sys.exit(1)

        nuke_exe = getNukeExecutablePath()
        cmd = " ".join([nuke_exe,"-F", f"{frame_range.start}-{frame_range.stop}", "-x", launcher_path, file_sequence_path, mov_file_path])
        
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
    "playblast_maya": None, # Placeholder for Maya playblast command
    "daily": createMoveFromSequence,
}