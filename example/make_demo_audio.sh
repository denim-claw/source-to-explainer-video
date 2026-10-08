#!/usr/bin/env bash
# Placeholder narration audio so the example pipeline can be proven end-to-end
# WITHOUT any paid TTS call. It is room-tone noise, NOT speech.
# Replace these WAVs with real synthesised narration before calling the output a
# deliverable; see references/tts.md.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p audio
# seconds per scene (edit to match your script length)
secs=(16 14 12)
for i in "${!secs[@]}"; do
  n=$((i + 1))
  out=$(printf 'audio/scene-%02d.wav' "$n")
  if [ -f "$out" ]; then
    echo "keep existing $out"
    continue
  fi
  ffmpeg -v error -y -f lavfi -i "anoisesrc=color=pink:amplitude=0.02:sample_rate=24000:duration=${secs[$i]}" \
    -ac 1 -c:a pcm_s16le "$out"
  echo "wrote $out (${secs[$i]}s placeholder, not speech)"
done
echo "PLACEHOLDER AUDIO — replace before delivery."
