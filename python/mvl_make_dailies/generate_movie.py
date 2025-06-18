# python/mvl_make_dailies/generate_movie.py

import argparse
import sys
import os
import subprocess
import tempfile
import re

# Import common utilities
from mvl_make_dailies.common_utils import logger 
from mvl_make_dailies.common_utils import getPythonPackagePath, getNukeExecutablePath, getConfigPath, isValidFrameRange
from mvl_make_dailies.movie_commands import APP_MODE_COMMANDS


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="Generate a movie from an image sequence or Maya scene, adhering to dailies best practices.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "app_mode",
        choices=list(APP_MODE_COMMANDS.keys()),
        help="Specify the application mode:\n"
             " daily: Use Nuke to render a movie from an image sequence."
    )

    # --- Common Arguments ---
    parser.add_argument("--input", required=True, help="Path to the input image sequence (e.g., /path/to/sequence.####.exr).") 
    parser.add_argument("--output", required=True, help="Path for the output movie file (e.g., /path/to/output.mov).")
    parser.add_argument("--start", type=int, help="Start frame.")
    parser.add_argument("--end", type=int, help="End frame.")
    parser.add_argument("--frame_rate", type=int, default=24, help="Frame rate for the output movie.")
    parser.add_argument("--mov_codec", default="H.264", help="Codec for .mov files (e.g., 'h264', 'apcn' for Apple ProRes).")
    

    # --- Nuke-Specific Arguments ---
    nuke_group = parser.add_argument_group('Nuke-Specific Arguments')
    nuke_group.add_argument("--input_colorspace", default="ACEScg", help="[Nuke Only] Input colorspace for the image sequence.")
    nuke_group.add_argument("--output_colorspace", default="sRGB", help="[Nuke Only] Output colorspace for the rendered movie.") 
    nuke_group.add_argument("--output_file_type", default="mov", choices=["mov", "mp4", "avi"], help="[Nuke Only] Output file type for the rendered movie.")

    args = parser.parse_args(argv)

    if args.app_mode in APP_MODE_COMMANDS:
        APP_MODE_COMMANDS[args.app_mode](args)
    else:
        raise ValueError(f"Unknown app_mode: {args.app_mode}")
    

if __name__ == "__main__":
    main()