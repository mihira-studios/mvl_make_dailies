# python/mvl_make_dailies/generate_movie.py

import argparse
import sys
import os
import subprocess
import tempfile
import re

from mvl_make_dailies.common_utils import (slate_args, burnin_args, reformat_args, colorspace_args, writer_args)
from mvl_make_dailies.common_utils import logger 
from mvl_make_dailies.movie_commands import APP_MODE_COMMANDS

def add_arguments_from_keys(parser, keys):
    type_map = {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool
    }

    for arg in keys:
        arg = arg.copy()  # so you don't mutate the input
        name = arg.pop("name")

        try:
            # Convert "type" string to callable
            if "type" in arg and isinstance(arg["type"], str):
                arg["type"] = type_map[arg["type"].strip().lower()]
            if "type" in arg and isinstance(arg['type'], float):
                logger.info(f"add_arguments_from_keys float type {arg['type']} for node {name}")
                
            parser.add_argument(name, **arg)
        except KeyError as e:
            logger.error(f"Invalid type in argument '{name}': {e}")
        except Exception as e:
            logger.error(f"Failed to add argument '{name}': {e}")
            
        
def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="Generate a movie from an image sequence or Maya scene, adhering to dailies best practices.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "app_mode",
        default="daily",
        choices=list(APP_MODE_COMMANDS.keys()),
        help="Specify the application mode:\n"
             " daily: Use Nuke to render a movie from an image sequence."
    )

    parser.add_argument("--input", required=True, help="Path to the input image sequence (e.g., /path/to/sequence.####.exr).") 
    parser.add_argument("--output", required=True, help="Path for the output movie file (e.g., /path/to/output.mov).")
    parser.add_argument("--first", type=int, help="Start frame.")
    parser.add_argument("--last", type=int, help="End frame.")
 
    add_arguments_from_keys(parser, slate_args())
    add_arguments_from_keys(parser, burnin_args())
    add_arguments_from_keys(parser, reformat_args())
    add_arguments_from_keys(parser, colorspace_args())
    add_arguments_from_keys(parser, writer_args())        

    args = parser.parse_args(argv)
    if args.app_mode in APP_MODE_COMMANDS:
        APP_MODE_COMMANDS[args.app_mode](args)
    else:
        raise ValueError(f"Unknown app_mode: {args.app_mode}")

if __name__ == "__main__":
    main()