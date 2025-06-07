import os
import subprocess
import sys

#
# ─── CONFIG ────────────────────────────────────────────────────────
#
# Put your *absolute* input path here:
INPUT_FILE = r"C:/Users/mason/Documents/Computer Networks/videoProject/catVideo.mp4"
# And your output folder here:
OUTPUT_DIR = r"C:/Users/mason/Documents/Computer Networks/videoProject/output_dash"
#
# ───────────────────────────────────────────────────────────────────
#

def encode_to_dash(input_file, output_dir):
    # sanity check
    if not os.path.isfile(input_file):
        print(f"ERROR: can't find input file: {input_file}", file=sys.stderr)
        sys.exit(1)
    os.makedirs(output_dir, exist_ok=True)

    # build filter_complex with forced DAR
    fc = ";".join([
        "[0:v]split=3[v0][v1][v2]",
        "[v0]scale=1920:1080,setsar=1,setdar=16/9[v0out]",
        "[v1]scale=1280:720,  setsar=1,setdar=16/9[v1out]",
        "[v2]scale=854:480,   setsar=1,setdar=16/9[v2out]"
    ])

    cmd = [
        "ffmpeg", "-y",
        "-i", input_file,
        "-filter_complex", fc,
        # map video+audio for each rendition
        "-map", "[v0out]", "-b:v:0", "5000k",
        "-map", "0:a",      "-b:a:0", "128k",

        "-map", "[v1out]", "-b:v:1", "3000k",
        "-map", "0:a",      "-b:a:1", "128k",

        "-map", "[v2out]", "-b:v:2", "1500k",
        "-map", "0:a",      "-b:a:2", "128k",

        # DASH‐specific
        "-f", "dash",
        "-use_timeline", "1",
        "-use_template", "1",
        "-seg_duration", "2",
        "-adaptation_sets", "id=0,streams=v id=1,streams=a",
        # nice clean naming:
        "-init_seg_name",  "init-$RepresentationID$.m4s",
        "-media_seg_name", "chunk-$RepresentationID$-$Number%05d$.m4s",
        "manifest.mpd"
    ]

    print("\nRunning:\n  " + " \\\n  ".join(cmd) + "\n")
    # run *inside* the output dir so everything lands there
    subprocess.run(cmd, cwd=output_dir, check=True)
print(f"DASH package complete -> {OUTPUT_DIR}/manifest.mpd")

if __name__ == "__main__":
    encode_to_dash(INPUT_FILE, OUTPUT_DIR)
