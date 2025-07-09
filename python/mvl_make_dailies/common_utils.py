import sys 
import os
import logging
import tempfile
import re
from enum import Enum

from mvl_core_pipeline import rez_utils
from mvl_core_pipeline.fig import Fig, YAMLConfigDriver
from mvl_core_pipeline.logger import Logger


logger = Logger(name='movie_generator', repo_name='rez-make-dailies').get_logger()
logger.setLevel(logging.DEBUG)

error_handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
error_handler.setFormatter(formatter)
logger.addHandler(error_handler)

cfg = Fig('mvl_make_dailies', 'knobs_template', YAMLConfigDriver()) 

class NukeTemplate(Enum):
    MVL_VFX_TEMPLATE_SLATE_AND_BURNIN = "MVL_VFX_Template_Slate_Overlay_v0.0.1.nk"


def writer_keys():
    """
    Returns a list of keys used for writer metadata in the Nuke template.
    These keys are used to extract writer related arguments from the command line arguments.
    """
    return [
        "file","file_type",
        "mov64_codec", "mov64_fps", "first", "last"
    ]   

def reformat_keys():
    """
    Returns a list of keys used for reformat metadata in the Nuke template.
    These keys are used to extract reformat related arguments from the command line arguments.
    """
    return [
        "type", "format"
    ]

def colorspace_keys():
    """
    Returns a list of keys used for colorspace metadata in the Nuke template.
    These keys are used to extract colorspace related arguments from the command line arguments.
    These keys same as the knobs in the Nuke template.
    """
    return [
        "colorspace_in", "colorspace_out"
    ]

def burn_in_keys():
    """
    Returns a list of keys used for burn-in metadata in the Nuke template.
    These keys are used to extract burn-in related arguments from the command line arguments.
    """
    return [
        "burnin", "burnIn_textScale", "topleft", "topcenter", "topright",
        "bottomleft", "bottomcenter", "bottomright"
    ]   

def slate_keys():
    """
    Returns a list of keys used for slate metadata in the Nuke template.
    These keys are used to extract slate related arguments from the command line arguments.
    """
    return [
        "f_version_name", "f_submission_note", "f_submitting_for", "f_shot_name", "f_shot_types",
        "f_vfx_scope_of_work", "f_show", "f_vendor", "f_date", "f_frames_first", "f_frames_last",
        "f_frames_duration", "f_media_color", "text", "f_shot_description", "f_episode", "f_scene",
        "f_sequence_name", "optional_fields_label", "f_opt1_key", "f_opt1_value", "f_opt2_key",
        "f_opt2_value", "f_opt3_key", "f_opt3_value", "f_opt4_key", "f_opt4_value", "f_opt5_key",
        "f_opt5_value", "f_opt6_key", "f_opt6_value"
    ]

def read_keys():   
    """
    Returns a list of keys used for read metadata in the Nuke template.
    These keys are used to extract read related arguments from the command line arguments.
    """
    return [
        "file"
    ]

def writer_args():
    return cfg.get_config()['template']['Nodes']['write']

def reformat_args():
    return cfg.get_config()['template']['Nodes']['reformat']

def colorspace_args():
    return cfg.get_config()['template']['Nodes']['colorspace']
 
def burnin_args():
    return cfg.get_config()['template']['Nodes']['burnin']

def slate_args():
    return cfg.get_config()['template']['Nodes']['slate']

def get_package_path()->str:
    """
    Get the package path for the mvl_make_dailies package.
    This function retrieves the path from the environment variable REZ_MVL_MAKE_DAILIES_ROOT,  
    which is set by Rez when the package is loaded. 
    
    Returns:
        str: The path to the mvl_make_dailies package directory.
    """
    return rez_utils.get_repo_root('mvl_make_dailies')

def get_python_package_path()->str:
    """
    Get the package path for the mvl_make_dailies package.
    This function retrieves the path from the environment variable REZ_MVL_MAKE_DAILIES_ROOT,  
    which is set by Rez when the package is loaded.
    If the environment variable is not set, it falls back to the current directory. 
    Returns:
        str: The normalized path to the mvl_make_dailies package directory.
    """

    # Get the base path for the package's Python modules to set in sys.path
    # This assumes REZ_mvl_make_dailies_ROOT is set by Rez
    package_path = get_package_path()
    if package_path:
        package_python_path = os.path.join(package_path, 'python')
    else:
        logger.warning("REZ_MVL_MAKE_DAILIES_ROOT not found. Relying on current sys.path or shell setup.")
        # Fallback if not running in a full Rez env (e.g., local testing)
        package_python_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    return package_python_path

def get_config_path()->str:
    """
    Get the configuration path for the mvl_make_dailies package.
    This function retrieves the path from the environment variable REZ_MVL_MAKE_DAILIES_ROOT,
    which is set by Rez when the package is loaded.
    If the environment variable is not set, it defaults to the current working directory.
    Returns:
        str: The normalized path to the mvl_make_dailies package's config directory.
    """
    return os.path.join(get_package_path(), 'configs')

def get_nuke_template_path(template=NukeTemplate.MVL_VFX_TEMPLATE_SLATE_AND_BURNIN)->str:
    """
    Get the template path for the mvl_make_dailies package.
    This function retrieves the path from the environment variable REZ_MVL_MAKE_DAILIES_ROOT,
    which is set by Rez when the package is loaded.
    If the environment variable is not set, it defaults to the current working directory.
    Returns:
        str: The normalized path to the mvl_make_dailies package's templates directory.
    """
    return os.path.join(get_package_path(), 'templates', "nuke", template.value)

def get_nuke_executable_path()->str:
    """
    Get the Nuke root path from the environment variable REZ_NUKE_ROOT.
    If the variable is not set, it defaults to the current working directory.
    Returns:
        str: The normalized path to the Nuke root directory.
    """

    # Get the base path for the Nuke root directory
    nuke_root = os.environ.get('REZ_NUKE_ROOT', '')
    version = nuke_root.replace("\\", "/").split("/")[-1]
    major_version = version.split('.')[0]
    nuke_executable_path = f"C:\\Program Files\\Nuke{version}\\Nuke{major_version}.0.exe" 
    if not nuke_executable_path:
        logger.warning("NUKE_ROOT not found. Using current working directory as fallback.")
        nuke_executable_path = os.getcwd()
    
    return os.path.normpath(nuke_executable_path)

def gather_frame_range(sequence_path) -> range:
    """
    Collect the frame range from a file sequence path.
    This function assumes the sequence is named with a pattern like
    "image.####.exr" or "image_####.exr" where #### is the frame number.
    If the sequence is a folder, it will gather all files in that folder
    and determine the frame range based on the file names.
    If the sequence is a single file, it will return a range with that single frame.

    Args:
        sequecence_path (str): Path to the image sequence or folder containing the sequence.
    """
    frame_pattern = re.compile(r'(\d+)\.[a-zA-Z0-9]+$') # Matches digits before the last dot and extension

    frames = []
    if os.path.isdir(sequence_path):
        files = sorted(os.listdir(sequence_path))
        for file in files:
            full_file_path = os.path.join(sequence_path, file)
            if os.path.isfile(full_file_path) and file.lower().endswith(('.exr', '.jpg', '.png')):
                match = frame_pattern.search(file)
                if match:
                    try:
                        frame_number = int(match.group(1))
                        frames.append(frame_number)
                    except ValueError as e:
                        logger.warning(f"Could not convert frame number '{match.group(1)}' from file '{file}': {e}")
                else:
                    logger.warning(f"No frame number found in file: {file} matching pattern.")
    elif os.path.isfile(sequence_path):
        file_name = os.path.basename(sequence_path)
        match = frame_pattern.search(file_name)
        if match:
            try:
                frame_number = int(match.group(1))
                frames.append(frame_number)
            except ValueError as e:
                raise ValueError(f"Could not convert frame number '{match.group(1)}' from file '{file_name}': {e}")
        else:
            raise ValueError(f"No frame number found in file: {file_name} matching expected pattern.")
    else:
        raise ValueError(f"Invalid sequence path: {sequence_path}. Must be a file or directory.")

    if not frames:
        raise ValueError(f"No valid image files found in directory: {sequence_path}")

    start = min(frames)
    end = max(frames)

    logger.info(f"Gathered frame range from {sequence_path}: {start} to {end}")

    return range(start, end ) 

def is_valid_frame_range(start, stop):
    """
    Check if the provided frame range is valid.
    A valid range must have start < stop and both must be non-negative integers.
    
    Args:
        start (int): Start frame number.
        stop (int): Stop frame number.
    
    Raises:
        ValueError: If the frame range is invalid.
    """
    if start is None and stop is None:
        return False
    if start >= stop:
        raise ValueError(f"Invalid frame range: start ({start}) must be less than stop ({stop}).")
    if start < 0 or stop < 0:
        raise ValueError(f"Frame numbers must be non-negative integers. Received: start={start}, stop={stop}.")
    if not isinstance(start, int) or not isinstance(stop, int):
        raise ValueError(f"Frame numbers must be integers. Received: start={start} ({type(start)}), stop={stop} ({type(stop)}).")   
    if start == stop:
        logger.warning(f"Start frame ({start}) is equal to stop frame ({stop}). This will result in a single frame output.")
    if (start is None) or (stop is None):
        logger.error("Both --start and --end must be provided.")
        sys.exit(1)
    
    logger.info(f"Valid frame range: {start} to {stop}")
    return True 

def create_temp_file(prefix="mvl_make_dailies", suffix="nk") -> str:
    """
    Create a temporary file with a unique name.
    The file will be created in the system's temporary directory.
    
    Returns:
        str: The path to the created temporary file.
    """
    
    temp_file = tempfile.NamedTemporaryFile(prefix="mvl_make_dailies_", suffix=".mov", delete=False)
    temp_file.close()  # Close the file so it can be used later
    logger.info(f"Created temporary file: {temp_file.name}")
    return temp_file.name

def is_valid_path(path):
    """
    Check if the provided path is valid.
    A valid path must be a string and not empty.
    
    Args:
        path (str): The path to check.
    
    Returns:
        bool: True if the path is valid, False otherwise.
    """
    if os.path.exists(path):
        if os.path.isfile(path) or os.path.isdir(path):
            logger.info(f"Valid path: {path}")
            return True
        else:
            logger.error(f"Path exists but is neither a file nor a directory: {path}")
            return False
    
    logger.error(f"Path does not exist: {path}")
    return False

def enableHouModule():
    """
    Set up the environment so that "import hou" works.
    """
    import sys, os
    
    # Importing hou will load Houdini's libraries and initialize Houdini.
    # This will cause Houdini to load any HDK extensions written in C++.
    # These extensions need to link against Houdini's libraries,
    # so the symbols from Houdini's libraries must be visible to other
    # libraries that Houdini loads.  To make the symbols visible, we add the
    # RTLD_GLOBAL dlopen flag.
    if hasattr(sys, "setdlopenflags"):
        old_dlopen_flags = sys.getdlopenflags()
        sys.setdlopenflags(old_dlopen_flags | os.RTLD_GLOBAL)

    python_version = sys.version_info
    python_major_version = python_version.major
    python_minor_version = python_version.minor    

    houdini_root  = os.environ.get('REZ_HOUDINI_ROOT')
    if not houdini_root:
        logger.error("houdini installation not found! make sure to rub rez-env houdini mvl_make_dailies")
        sys.exit(1)
    
    houdini_version = houdini_root.replace("\\", "/").split("/")[-1]
    vrn = str(houdini_version)[:-3]
    sidefx_root = f"C:\\Program Files\\Side Effects Software\\Houdini {vrn}"
    houdini_python_module_path = os.path.join(sidefx_root,"houdini",f"python{python_major_version}.{python_minor_version}libs")

    logger.info(f"houdini python module path : {houdini_python_module_path}")
  
    if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
        os.add_dll_directory(os.path.join(sidefx_root, "bin"))

    try:
        import hou
    except ModuleNotFoundError:
        # If the hou module could not be imported, then add 
        # $HFS/houdini/pythonX.Ylibs to sys.path so Python can locate the
        # hou module.
        sys.path.append(os.path.join(sidefx_root, "bin"))
        sys.path.append(houdini_python_module_path)
        
        import hou
    finally:
        # Reset dlopen flags back to their original value.
        if hasattr(sys, "setdlopenflags"):
            sys.setdlopenflags(old_dlopen_flags)