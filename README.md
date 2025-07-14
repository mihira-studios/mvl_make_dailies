# 🎨 mvl-make-dailies

A tool to generate movie files from image sequences (e.g., Nuke renders), with support for slates, burn-ins, metadata fields, and formatting options.

---

## 🛠️ Quick Start

### 1. Activate Environment

```bash
rez-env mvl_make_dailies
```

### 2. Run the Tool

```bash
make_movie daily --input "<source_sequence_path>" --output "<output_movie_path>"
```

✅ **Required Arguments**

- `--input` : Path to the input image sequence (e.g., `/path/to/file.####.exr`)
- `--output` : Path to the output `.mov` file (e.g., `/path/to/output.mov`)

---

## ⚙️ Example Usage

```bash
make_movie daily \
  --input "/project/plates/GEN63_SC_48_SH_0160_v001.####.exr" \
  --output "/project/dailies/GEN63_SC_48_SH_0160_v001.mov" \
  --first 1001 \
  --last 1050 \
  --f_version_name "v001" \
  --f_shot_name "GEN63_SC_48_SH_0160" \
  --f_show "GEN63" \
  --f_vendor "MyStudio" \
  --f_submission_note "Lighting pass update" \
  --colorspace_in "linear" \
  --colorspace_out "sRGB" \
  --mov64_codec "h264" \
  --mov64_fps 24
```

---

## 📾 Available Arguments

### 🧱 Core

- `--input <path>`: Input sequence (e.g., `/path/to/sequence.####.exr`)
- `--output <path>`: Output movie (e.g., `/path/to/output.mov`)
- `--first <frame>`: Start frame
- `--last <frame>`: End frame
- `--no-slate`: Disable slate
- `--no-burnin`: Disable burn-in metadata

### 🏷️ Metadata Fields

- `--f_version_name <str>`
- `--f_submission_note <str>`
- `--f_submitting_for <str>`
- `--f_shot_name <str>`
- `--f_shot_types <str>`
- `--f_vfx_scope_of_work <str>`
- `--f_show <str>`
- `--f_vendor <str>`
- `--f_date <str>`
- `--f_frames_first <int>`
- `--f_frames_last <int>`
- `--f_frames_duration <int>`
- `--f_shot_description <str>`
- `--f_episode <str>`
- `--f_scene <str>`
- `--f_sequence_name <str>`

### 🧪 Optional Custom Fields

- `--optional_fields_label <str>`
- `--f_opt1_key/--f_opt1_value`
- `--f_opt2_key/--f_opt2_value`
- `--f_opt3_key/--f_opt3_value`
- `--f_opt4_key/--f_opt4_value`
- `--f_opt5_key/--f_opt5_value`
- `--f_opt6_key/--f_opt6_value`

### 🖼️ Burn-in Customization

- `--burnin_text_scale <float>`
- `--topleft / --topcenter / --topright`
- `--bottomleft / --bottomcenter / --bottomright`
- `--burnIn_color <str>` (e.g., `"white"`)
- `--burnIn_opacity <float>` (0 to 1)

### 🎮 Reformat & Resize

- `--format <str>`
- `--type <str>`: Crop box (e.g., `0 0 1920 1080`)
- `--filter <str>`
- `--resize {fit,fill,crop,none}`
- `--black_outside <bool>`
- `--clamp <bool>`
- `--pbb <bool>`

### 🎨 Color Management

- `--colorspace_in <str>`
- `--colorspace_out <str>`

### 🧪 Output Settings

- `--file-type <str>`: Output extension (e.g., `mov`)
- `--mov64_codec <str>`: Codec (e.g., `h264`)
- `--mov64_fps <int>`: Frames per second

---

## 🧬 Python API

Use the dailies tool in your pipeline scripts:

```python
from mvl_make_dailies.movie_commands import create_movie_from_sequence

data = {
    'input': r'/path/to/sequence.####.exr',
    'output': r'/path/to/output.mov',
    'first': 1001,
    'last': 1050,
    'f_version_name': 'v001',
    'f_show': 'GEN63',
    'colorspace_in': 'linear',
    'colorspace_out': 'sRGB',
}

create_movie_from_sequence(data)
```

---

## 📘 Help

To view CLI help at any time:

```bash
make_movie --help
```

---

## 📌 Notes

- Image sequences should be numbered using `####` or similar convention.
- Ensure Nuke is properly set up in the environment.
- Burn-ins and slates follow studio naming and formatting standards.

---

## 🧑‍💻 Contributors

Maintained by the MVL DEV Team.\
For support or issues, contact: [systems@mihira.studio.com](mailto\:systems@mihira.studio.com)

