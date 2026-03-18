# GoPro Video Sorting

This project analyzes GoPro videos from a folder and classifies timeline segments into:

- `movement`
- `stationary`
- `night`

It produces a single unified timeline across all videos in the folder and exports practical files for review and editing.

## Features

- Folder scan for common video formats (`.mp4`, `.mov`, `.mkv`, `.avi`)
- Start-time inference from GoPro filename pattern like `20220304T000819S000000_GH580049.MP4`
- Night detection based on frame brightness
- Large-motion detection based on optical flow (smoothed to avoid small jitter noise)
- Unified timeline sorted by absolute start time across all videos
- Export outputs:
	- `timeline.csv`
	- `timeline.json`
	- `summary.json`
	- `cut_by_label.sh` (ready-to-run ffmpeg cut commands)

## Project Structure

```text
src/gopro_sorting/
	__init__.py
	config.py
	models.py
	discovery.py
	analyze_brightness.py
	analyze_motion.py
	classify.py
	timeline.py
	exporters.py
	edit_script.py
	cli.py
	gui.py
tests/
	conftest.py
	test_discovery.py
	test_timeline.py
	test_exporters.py
resources/
	20220304T000819S000000_GH580049.MP4
```

## Requirements

- Linux
- Python 3.11+
- `ffmpeg` installed in PATH (for clip cutting/rearranging workflow)

Install Python dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run: CLI

From repository root:

```bash
PYTHONPATH=src python -m gopro_sorting.cli resources --output-dir output
```

Optional tuning:

```bash
PYTHONPATH=src python -m gopro_sorting.cli resources \
	--output-dir output \
	--brightness-night-threshold 40 \
	--motion-threshold 2.2 \
	--sample-every-n-frames 30 \
	--min-segment-seconds 3.0 \
	--confidence-floor 0.55 \
	--max-analysis-seconds 120
```

## Run: GUI

```bash
PYTHONPATH=src python -m gopro_sorting.gui
```

Pick input/output folders and click `Run analysis`.

## Output Files

- `output/timeline.csv`
	- Spreadsheet-friendly timeline of all segments.
- `output/timeline.json`
	- Structured version of the timeline.
- `output/summary.json`
	- Durations by class and low-confidence segment list.
- `output/cut_by_label.sh`
	- Shell script containing ffmpeg commands to cut each segment into:
		- `output/clips/movement/`
		- `output/clips/stationary/`
		- `output/clips/night/`

## How to Cut Videos by Type

After generating output files:

```bash
./output/cut_by_label.sh
```

This creates per-segment clips organized by class.

## How to Rearrange Videos by Type

Example: create one ordered list with `night` clips first, then `stationary`, then `movement`.

```bash
find output/clips/night -type f -name '*.mp4' | sort > output/night.list
find output/clips/stationary -type f -name '*.mp4' | sort > output/stationary.list
find output/clips/movement -type f -name '*.mp4' | sort > output/movement.list
cat output/night.list output/stationary.list output/movement.list > output/reordered.list
```

Convert into ffmpeg concat format:

```bash
awk '{print "file '\''" $0 "'\''"}' output/reordered.list > output/concat.txt
```

Render one merged playback video:

```bash
ffmpeg -y -f concat -safe 0 -i output/concat.txt -c copy output/reordered_merged.mp4
```

If stream-copy concat fails due to codec differences, re-encode:

```bash
ffmpeg -y -f concat -safe 0 -i output/concat.txt -c:v libx264 -c:a aac output/reordered_merged_reencoded.mp4
```

## Threshold Tuning Tips

- Too many clips labeled `movement`:
	- Increase `--motion-threshold`.
- Movement missed during strong ship/camera movement:
	- Decrease `--motion-threshold`.
- Too many clips labeled `night`:
	- Decrease `--brightness-night-threshold` sensitivity by lowering threshold value.
- Night not detected enough:
	- Raise `--brightness-night-threshold`.

## Tests

```bash
PYTHONPATH=src pytest -q
```

## Notes

- Filename timestamp parsing assumes UTC for GoPro-style names.
- If filename pattern is missing, file modification time is used as fallback for timeline ordering.
