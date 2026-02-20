

import subprocess
import sys
import os
import json

VIDEO_IN  = "output_final.mp4"
AUDIO_IN  = "voiceover.mp3"
VIDEO_OUT = "final_with_audio.mp4"
WORDS_FILE = "word_timings.json"

# ─────────────────────────────────────────────
#  Check files
# ─────────────────────────────────────────────
print("=" * 50)
print("  MERGE DIAGNOSTIC")
print("=" * 50)

for f in [VIDEO_IN, AUDIO_IN]:
    if os.path.exists(f):
        mb = os.path.getsize(f) / (1024*1024)
        print(f"  ✓ Found: {f}  ({mb:.2f} MB)")
    else:
        print(f"  ✗ MISSING: {f}")


print("\nChecking ffmpeg...")
try:
    result = subprocess.run(
        ["ffmpeg", "-version"],
        capture_output=True, text=True
    )
    first_line = result.stdout.split("\n")[0]
    print(f"  ✓ {first_line}")
except FileNotFoundError:
    print("  ✗ ffmpeg NOT FOUND")
    print("\n  Install it:")
    print("    Windows: winget install ffmpeg")
    print("    Then close and reopen your terminal")
    sys.exit(1)


print(f"\nChecking {VIDEO_IN} for existing audio track...")
probe = subprocess.run(
    ["ffmpeg", "-i", VIDEO_IN],
    capture_output=True, text=True
)
output = probe.stderr
has_audio = "Audio:" in output
has_video = "Video:" in output
print(f"  Video track: {'✓' if has_video else '✗'}")
print(f"  Audio track: {'✓ already has audio' if has_audio else '✗ no audio (expected)'}")


print(f"\nMerging video + audio → {VIDEO_OUT} ...")
print("(Using ffmpeg directly — most reliable method)\n")

cmd = [
    "ffmpeg",
    "-y",                        # overwrite output
    "-i", VIDEO_IN,              # input video (no audio)
    "-i", AUDIO_IN,              # input audio
    "-c:v", "copy",              # copy video stream (no re-encode, fast)
    "-c:a", "aac",               # encode audio as aac
    "-b:a", "192k",              # audio bitrate
    "-map", "0:v:0",             # take video from first input
    "-map", "1:a:0",             # take audio from second input
    "-shortest",                 # end when shortest stream ends
    VIDEO_OUT
]

print("Running:", " ".join(cmd))
print()

result = subprocess.run(cmd)

if result.returncode == 0 and os.path.exists(VIDEO_OUT):
    mb = os.path.getsize(VIDEO_OUT) / (1024*1024)
    print(f"\n✅  Success! → {VIDEO_OUT}  ({mb:.2f} MB)")
    print("\nVerifying output has both streams...")
    probe2 = subprocess.run(
        ["ffmpeg", "-i", VIDEO_OUT],
        capture_output=True, text=True
    )
    out2 = probe2.stderr
    print(f"  Video: {'✓' if 'Video:' in out2 else '✗'}")
    print(f"  Audio: {'✓' if 'Audio:' in out2 else '✗'}")
else:
    print(f"\n✗ Merge failed (return code {result.returncode})")
    print("Check the error above ↑")