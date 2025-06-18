# python/nuke_movie_generator/generate_movie.py

import nuke
import argparse
import os
import sys
import subprocess
from mvl_make_dailies.common_utils import logger, createTempFile

def generateMovie(
    sequence_path,
    output_mov_path,  
    input_colorspace="linear", 
    output_colorspace="sRGB", 
    output_file_type="mov",
    mov_codec="H.264",
    frame_rate=24,
    metadata_to_preserve=None,
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
    logger.info(f"Nuke Python API: {nuke.NUKE_VERSION_STRING}")

    # Clear any existing script
    nuke.scriptClear()

    ranges = nuke.tcl('frames ranges')
    frame_start, frame_stop = ranges.split('-')

    # Create a Read node
    read_node = nuke.nodes.Read()
    read_node['file'].fromUserText(f"{sequence_path} {frame_start}-{frame_stop}")  # Set the file path for the image sequence
    
    # Create a Write node
    write_node = nuke.nodes.Write()
    write_node['file'].setValue(output_mov_path)
    write_node['file_type'].setValue('mov') # Or 'mp4', 'h264', etc. depends on Nuke's codecs
    write_node['knobChanged'].setValue("if nuke.thisNode()['file_type'].value() == 'mov': nuke.thisNode()['codec'].setValue('h264')") # Set codec for mov
    write_node['colorspace'].setValue(output_colorspace)  # Set output color space
    write_node['fps'].setValue(frame_rate)  # Set frame rate for the output
    
    # Connect the Read node to the Write node
    write_node.setInput(0, read_node)
    
    tempfile = createTempFile(prefix="mvl_make_dailies", suffix="nk") # Create a temporary Nuke script file
    logger.info(f"Nuke script created for: {tempfile}")
    logger.info(f"Output path: {output_mov_path}")
    
    # Render the script
    logger.info("Rendering...")
    nuke.execute(write_node, 1001, 1010) # Example frame range, adjust as needed
    logger.info("Rendering complete!")

    nuke.scriptSave(tempfile)
    logger.info(f"Nuke script saved to: {tempfile}")



def main():
    """
    Main function to run the Nuke script for generating dailies.
    It expects the following command line arguments:
    1. Path to the Nuke script template
    2. Path to the new Nuke script to be created    
    3. Path to the file sequence (e.g., /path/to/shot.####.exr)
    4. Path to the output MOV file (e.g., /path/to/shot
    5. Path to the output MOV file (e.g., /path/to/shot_dailies.mov)
    
    """
    if len(sys.argv) < 3:
        logger.error("Insufficient arguments provided. Expected 5 arguments.")
        sys.exit(1)

    file_sequence_path = sys.argv[1]
    mov_file_path = str(sys.argv[2])
    
    try:
        scriptPath = generateMovie(
            sequence_path=file_sequence_path ,
            output_mov_path=mov_file_path,
        )
    except Exception as e:
        print(f"An error occurred during dailies rendering: {e}", file=sys.stderr)
        sys.exit(1) # Exit with an error code

   
             
if __name__ == "__main__":
    # Nuke will run this script as __main__
    main()

