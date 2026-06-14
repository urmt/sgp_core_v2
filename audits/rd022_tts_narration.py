"""Generate TTS narration for RD-022 explainer video, then mux with Manim output."""

import subprocess
import os
import json

VOICE = "en-US-BrianNeural"  # Warm, casual, approachable

# Scene narration with approximate start times (seconds)
# These are crafted to fit the visual timing from the Manim render
SCENES = [
    {
        "name": "title",
        "start": 0.0,
        "text": (
            "The Mystery of the Sand Pile Score."
        ),
    },
    {
        "name": "what_is_c",
        "start": 3.5,
        "text": (
            "Imagine a pile of sand. Push one grain, and some move with it. "
            "We give the pile a score from zero to one. "
            "High score means they move together. Low score means randomly."
        ),
    },
    {
        "name": "the_question",
        "start": 13.5,
        "text": (
            "But is this score real? "
            "Or did we measure it wrong?"
        ),
    },
    {
        "name": "eight_rulers",
        "start": 20.0,
        "text": (
            "So we tried eight different rulers. "
            "Each measures the score differently. "
            "But all eight agree. "
            "The score predicts how well the sand bounces back."
        ),
    },
    {
        "name": "the_result",
        "start": 34.0,
        "text": (
            "Eight out of eight agree. "
            "Every way of measuring correctly predicts recovery. "
            "The score is real."
        ),
    },
    {
        "name": "the_mystery",
        "start": 47.0,
        "text": (
            "But we still don't know what the score measures. "
            "Not the grains. Not the speed. Not the shape. "
            "Something else. "
            "That's the mystery we're still working on."
        ),
    },
]


def generate_scene_audio(scene, output_dir="/tmp/tts_scenes"):
    """Generate TTS audio for one scene."""
    os.makedirs(output_dir, exist_ok=True)
    mp3_path = os.path.join(output_dir, f"{scene['name']}.mp3")
    txt_path = os.path.join(output_dir, f"{scene['name']}.txt")

    # Write text for reference
    with open(txt_path, "w") as f:
        f.write(scene["text"])

    # Generate TTS
    cmd = [
        "edge-tts",
        "--text", scene["text"],
        "--voice", VOICE,
        "--write-media", mp3_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR generating {scene['name']}: {result.stderr}")
        return None

    # Get duration with ffprobe
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", mp3_path],
        capture_output=True, text=True,
    )
    info = json.loads(probe.stdout)
    duration = float(info["format"]["duration"])
    print(f"  {scene['name']}: {duration:.1f}s (target start: {scene['start']}s)")
    return mp3_path, duration


def build_narration_track(scenes, output_path="/tmp/narration_full.mp3"):
    """Combine scene audio files into one track with correct timing."""
    # First, get all audio files
    audio_files = []
    for scene in scenes:
        result = generate_scene_audio(scene)
        if result:
            mp3_path, duration = result
            audio_files.append((scene["start"], mp3_path, duration))

    if not audio_files:
        print("No audio files generated!")
        return None

    # Build ffmpeg filter to place each clip at its start time
    inputs = []
    filter_parts = []
    for i, (start, mp3_path, duration) in enumerate(audio_files):
        inputs.extend(["-i", mp3_path])
        # adelay in milliseconds, pad to align
        delay_ms = int(start * 1000)
        filter_parts.append(f"[{i}]adelay={delay_ms}|{delay_ms},apad=pad_dur=80[a{i}]")

    # Mix all streams together
    mix_inputs = "".join(f"[a{i}]" for i in range(len(audio_files)))
    filter_parts.append(
        f"{mix_inputs}amix=inputs={len(audio_files)}:duration=longest:dropout_transition=0[out]"
    )

    filter_graph = ";".join(filter_parts)

    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", filter_graph,
        "-map", "[out]",
        "-t", "78",  # cap at 78s (video is 73.6s + a little padding)
        output_path,
    ]

    print(f"\nBuilding narration track...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr[-500:]}")
        return None

    # Check output duration
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", output_path],
        capture_output=True, text=True,
    )
    info = json.loads(probe.stdout)
    print(f"  Narration track: {float(info['format']['duration']):.1f}s")
    return output_path


def mux_video_audio(video_path, narration_path, output_path):
    """Combine video and narration into final output."""
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", narration_path,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        output_path,
    ]
    print(f"\nMuxing final video...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr[-500:]}")
        return None
    print(f"  Final: {output_path}")
    return output_path


if __name__ == "__main__":
    video_path = "/home/student/sgp_core_v2/media/videos/rd022_explainer/480p15/SandPileExplainer.mp4"
    narration_path = "/tmp/narration_full.mp3"
    final_path = "/home/student/sgp_core_v2/media/videos/rd022_explainer/480p15/SandPileExplainer_narrated.mp4"

    narration = build_narration_track(SCENES, narration_path)
    if narration:
        mux_video_audio(video_path, narration, final_path)
        # Also generate just the narration for review
        print(f"\nDone! Files:")
        print(f"  Narration only: {narration_path}")
        print(f"  Narrated video: {final_path}")
