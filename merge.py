"""
Merges voiceover.mp3 into output_final.mp4
Run: python merge.py
Output: final_with_audio.mp4
"""

import sys, os

try:
    from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip
    from moviepy.video.VideoClip import VideoClip
except ImportError:
    print("Run: pip install moviepy"); sys.exit(1)

VIDEO_IN  = "output_final.mp4"
AUDIO_IN  = "voiceover.mp3"
VIDEO_OUT = "final_with_audio.mp4"

# ── Check files exist ─────────────────────────────────────
for f in [VIDEO_IN, AUDIO_IN]:
    if not os.path.exists(f):
        print(f"❌  File not found: {f}")
        sys.exit(1)

print(f"Loading video : {VIDEO_IN}")
print(f"Loading audio : {AUDIO_IN}")

video = VideoFileClip(VIDEO_IN)
audio = AudioFileClip(AUDIO_IN)

print(f"Video duration : {video.duration:.1f}s")
print(f"Audio duration : {audio.duration:.1f}s")

# Trim video to audio length if needed
if video.duration > audio.duration:
    video = video.subclipped(0, audio.duration)

# Attach audio
final = video.with_audio(audio)

print(f"\nExporting → {VIDEO_OUT} ...\n")
final.write_videofile(
    VIDEO_OUT,
    codec="libx264",
    audio_codec="aac",
    preset="fast",
    ffmpeg_params=["-crf", "20"],
    threads=4,
    logger="bar",
)

print(f"\n✅  Done!  →  {VIDEO_OUT}")