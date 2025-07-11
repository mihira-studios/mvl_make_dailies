# python/nuke_movie_generator/generate_movie.py

import nuke
import argparse
import os
import sys
from mvl_make_dailies.common_utils import logger, create_temp_file, NukeTemplate, get_nuke_template_path
import tempfile
import uuid
import json


def normalize_path(path):
    """Ensure Windows paths use double backslashes for Nuke compatibility."""
    return path.replace("\\", "\\\\")

def apply_knob_values(node_name, knob_data, logger=None):
    """
    Sets knob values on a Nuke node if the node exists and the knobs are valid.

    Args:
        node_name (str): The name of the node in the Nuke script.
        knob_data (dict): Dictionary of knob_name: value to set.
        logger (logging.Logger, optional): Logger for error reporting. If not provided, errors print to stderr.
    """

    try:
        node = nuke.toNode(node_name)
        if node is None:
            msg = f"{node_name} node not found. Please check the Nuke script template."
            if logger:
                logger.error(msg)
            else:
                print(f"ERROR: {msg}", file=sys.stderr)
            sys.exit(1)

        for k, v in knob_data.items():
            if k in node.knobs() and v is not None:
                node[k].setValue(v) 

    except Exception as e:
        import traceback
        logger.error(f"Failed to set knob '{k}' to value '{v}': {e}")
        logger.debug(traceback.format_exc())
   


def generate_movie(
    file_in_path,
    file_out_path,  
    slate_data=None,
    overlay_data=None,
    reformat_data=None,
    colorspace_data=None, 
    write_data=None,  
):
    """
    Read the nuke script, update paths, and render the movie with best practices.
    :param input_path: Path to the input image sequence (e.g., /path/to/shot.####.exr )
    :param output_path: Path for the output MOV file (e.g., /path/to/shot_dailies.mov)
    :param start_frame: Start frame of the sequence.
    :param end_frame: End frame of the sequence.
    :param input_colorspace: Input color space (default: "linear")
    :param output_colorspace: Output color space (default: "sRGB")
    :param output_file_type: Output file type (default: "mov")
    :param mov_codec: Codec for .mov files (default: "H.264")
    :param frame_rate: Frame rate for the output (default: 24)
    :param metadata_to_preserve: List of Nuke knobs/metadata to preserve (default: None)
    
    """
    mvl_format = reformat_data['format'] if reformat_data and 'format' in reformat_data else 'HD_1080'  # Default to HD_1080

    sequence_path_nomalized = normalize_path(file_in_path)
    output_mov_path_nomalized = normalize_path(file_out_path)

    ranges = nuke.tcl('frames ranges')
    first, last = [int(x) for x in ranges.split('-')]

    nuke.scriptClear()
    nuke.root()['first_frame'].setValue(first)
    nuke.root()['last_frame'].setValue(last)
    nuke.root()['format'].setValue(mvl_format) 
    
    # Import the Nuke script template
    nuke.nodePaste(get_nuke_template_path(NukeTemplate.MVL_VFX_TEMPLATE_SLATE_AND_BURNIN))

    # Mvl Read Node
    read_node = nuke.toNode('MVL_READ')
    if read_node:
        read_node['file'].setValue(sequence_path_nomalized)
        read_node['frame_mode'].setValue('sequence') 

    apply_knob_values('MVL_FORMAT', reformat_data, logger)
    apply_knob_values('MVL_COLORSPACE', colorspace_data, logger)
    apply_knob_values('MVL_READ', {'file': sequence_path_nomalized}, logger)
    apply_knob_values('NETFLIX_TEMPLATE_SLATE', slate_data, logger)
    apply_knob_values('Netflix_MEI_Overlay', overlay_data, logger)

    if overlay_data.get('burnin') is False:
        # Optionally disable the node
        node = nuke.toNode("Netflix_MEI_Overlay")
        if node:
            node['disable'].setValue(True)
            logger.info("Disabled Netflix_MEI_Overlay due to --no-burnin")
        
    
        

    output_dir = os.path.dirname(output_mov_path_nomalized)
    if not os.path.exists(output_dir): 
        os.makedirs(output_dir)
    write_data["file"] = output_mov_path_nomalized
    apply_knob_values('MVL_MOV_WRITER', write_data, logger)

    temp_nk_path = os.path.join(tempfile.gettempdir(), f"mvl_temp_script_{uuid.uuid4().hex}.nk")
    nuke.scriptSaveAs(temp_nk_path)
    logger.info(f"Nuke script saved to {temp_nk_path}")

def main():
    """
    Main function to parse command line arguments and call the generate_movie function.
    This function uses argparse to handle command line arguments for the input image sequence,
    output MOV file, and optional slate and burn-in data.
    It then calls the generate_movie function with the provided arguments.
    If any errors occur during the process, they are logged and the script exits with an error
    code.
    :return: None   
    """
    parser = argparse.ArgumentParser(description="Generate a movie from an image sequence using Nuke.")
    parser.add_argument("src", help="Path to the input image sequence (e.g., /path/to/shot.####.exr)")
    parser.add_argument("dst", help="Path for the output MOV file (e.g., /path/to/shot_dailies.mov)")
    parser.add_argument("--slate", type=str, default=None, help="Slate data as JSON string")
    parser.add_argument("--burnin", type=str, default=None, help="Burn-in data as JSON string")
    parser.add_argument("--reformat", type=str, default=None, help="Reformat data as JSON string")
    parser.add_argument("--colorspace", type=str, default=None, help="Colorspace data as JSON string")
    parser.add_argument("--write", type=str, default=None, help="Write data as JSON string")
    parser.add_argument("--read", type=str, default=None, help="Read data as JSON string") 
    
    args = parser.parse_args()

    file_in = args.src
    file_out = args.dst

    slate_data = json.loads(args.slate) if args.slate else None
    burnin_data = json.loads(args.burnin) if args.burnin else None
    reformat_data = json.loads(args.reformat) if args.reformat else None
    colorspace_data = json.loads(args.colorspace) if args.colorspace else None
    write_data = json.loads(args.write) if args.write else None

    try:
        generate_movie(
            file_in_path= file_in,
            file_out_path= file_out,
            slate_data=slate_data,
            overlay_data=burnin_data,
            reformat_data=reformat_data,
            colorspace_data=colorspace_data,
            write_data=write_data
        )
    except Exception as e:
        print(f"An error occurred during dailies rendering: {e}", file=sys.stderr)
        sys.exit(1) # Exit with an error code

if __name__ == "__main__":
    main()

