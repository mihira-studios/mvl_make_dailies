# mvl-make-dailies

rez-env mvl_make_dailies

make_movie <command> --input <sourcefile> --output <destfile>

## Required Arguments

- `--input` : Path to the input image sequence (for Nuke render)
- `--output` : Path for the output movie file


### Common Arguments 
| Argument         | Type    | Required | Description                                                        |
|------------------|---------|----------|--------------------------------------------------------------------|
| `--input`        | str     | Yes*     | Path to spurce  (e.g.,`/path/to/sequence.####.exr`)                |
| `--output`       | str     | Yes      | Path for the output movie file (e.g., `/path/to/output####.mov`).      |
| `--start`        | int     | Yes      | Start frame.                                                       |
| `--end`          | int     | Yes      | End frame.                                                         |
| `--frame_rate`   | int     | No       | Frame rate for the output movie. Default: 24                       |
| `--mov_codec`    | str     | No       | Codec for .mov files. Default: H.264                               |


### Nuke-Specific Arguments

| Argument             | Type   | Default | Description                                      |
|----------------------|--------|---------|--------------------------------------------------|
| `--input_colorspace` | str    | ACEScg  | [Nuke Only] Input colorspace for the image sequence. |
| `--output_colorspace`| str    | sRGB    | [Nuke Only] Output colorspace for the rendered movie. |
| `--output_file_type` | str    | mov     | [Nuke Only] Output file type for the rendered movie. Choices: `mov` |


Command : "daily"

Usage example:

make_movie daily --input "<sourcedir>/GEN63_SC_48_SH_0160__main_plate_v001_camA_takeA_f4448x3096_####.exr" --output "<destdir>/GEN63_SC_48_SH_0160__main_plate_v001.mov"

API:

from mvl_make_dailies.movie_commands import create_movie_from_sequence

data = {'input' : r'<path/to/sequence.####.exr>r, 'output': r'<path/to/mov_file.mov>'}

create_movie_from_sequence(data)


