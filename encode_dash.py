import os
import subprocess

# ─── CONFIGURATION ───────────────────────────────────────────────────────────────
# Point these to your files/folders:
INPUT_FILE = "catVideo.mp4"
OUTPUT_DIR  = "output_dash"
# ────────────────────────────────────────────────────────────────────────────────

def encode_to_dash(input_file: str, output_dir: str):
    """
    Encode `input_file` into three resolutions (1080p, 720p, 480p) with 2s segments,
    packaged as DASH (manifest.mpd) in `output_dir`.
    """
    variants = [
        {"label": "1080p", "width": 1920, "height": 1080, "video_bitrate": "5000k", "audio_bitrate": "128k"},
        {"label": "720p",  "width": 1280, "height": 720,  "video_bitrate": "3000k", "audio_bitrate": "128k"},
        {"label": "480p",  "width": 854,  "height": 480,  "video_bitrate": "1500k", "audio_bitrate": "128k"},
    ]

    os.makedirs(output_dir, exist_ok=True)

    # Build filter_complex to split & scale
    splits = len(variants)
    split_labels = "".join(f"[v{i}]" for i in range(splits))
    fc = [f"[0:v]split={splits}{split_labels};"]
    for i, v in enumerate(variants):
        fc.append(f"[v{i}]scale={v['width']}:{v['height']}[v{i}out];")
    filter_complex = "".join(fc).rstrip(";")

    # Build ffmpeg command
    cmd = [
        "ffmpeg", "-y",
        "-i", input_file,
        "-filter_complex", filter_complex
    ]

    # Map each video + audio rendition
    for i, v in enumerate(variants):
        cmd += [
            "-map", f"[v{i}out]",
            "-b:v:" + str(i), v["video_bitrate"],
            "-map", "0:a",
            "-b:a:" + str(i), v["audio_bitrate"]
        ]

    # DASH muxer options
    cmd += [
        "-use_timeline", "1",
        "-use_template", "1",
        "-seg_duration", "2",
        "-adaptation_sets", "id=0,streams=v id=1,streams=a",
        "-f", "dash",
        os.path.join(output_dir, "manifest.mpd")
    ]

    print("Running ffmpeg command:\n", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"DASH package created at {output_dir}/manifest.mpd")

if __name__ == "__main__":
    encode_to_dash(INPUT_FILE, OUTPUT_DIR)
