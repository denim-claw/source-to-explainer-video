#!/usr/bin/env python3
"""Build measured narration timing + one 48 kHz mono WAV from per-utterance audio files.

Captions and scene boundaries must come from decoded PCM sample counts, not
container duration (MP3 padding) or character counts. Integer *_sample fields are
authoritative; legacy seconds fields are derived without boundary rounding.
Run this after synthesising one audio file per natural spoken utterance.

Usage:
    python3 build_narration_timing.py --out . audio/s1.mp3 audio/s2.mp3 ...

Options:
    --gap 0.35    silence inserted after every utterance except the last (default 0.35 s)
    --tail 0.80   extra hold after the last utterance (default 0.80 s)
    --sr 48000    sample rate of the assembled WAV (default 48000)

Writes:
    timing.json   [{"id", "audio", "dur", "start"}] with dur including the gap
    narration.wav 48 kHz 16-bit mono, same length as sum(dur)

Dependencies: ffprobe + ffmpeg on PATH. Works on Python 3.12+ (no audioop, no numpy).
"""
import argparse, json, os, struct, subprocess


def probe_seconds(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(out)


def decode_pcm(path: str, sr: int) -> bytes:
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-f", "s16le", "-acodec", "pcm_s16le",
         "-ar", str(sr), "-ac", "1", "-"],
        capture_output=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed on {path}: {r.stderr.decode()[:400]}")
    return r.stdout


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+", help="one audio file per utterance, in scene order")
    ap.add_argument("--out", default=".", help="output directory")
    ap.add_argument("--gap", type=float, default=0.35)
    ap.add_argument("--tail", type=float, default=0.80)
    ap.add_argument("--sr", type=int, default=48000)
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    if a.sr <= 0 or a.gap < 0 or a.tail < 0:
        ap.error("sample rate must be positive; gaps must be nonnegative")
    metas, chunks, clock = [], [], 0
    for i, path in enumerate(a.inputs):
        pcm = decode_pcm(path, a.sr)
        if len(pcm) % 2:
            raise ValueError(f"unaligned s16 mono PCM: {path}")
        samples = len(pcm) // 2
        gap_samples = round(a.sr * (a.tail if i == len(a.inputs) - 1 else a.gap))
        end = clock + samples
        boundary = end + gap_samples
        metas.append({"id": os.path.splitext(os.path.basename(path))[0],
                      "audio": samples / a.sr,
                      "dur": (samples + gap_samples) / a.sr,
                      "start": clock / a.sr,
                      "end": end / a.sr,
                      "sample_rate": a.sr,
                      "audio_samples": samples,
                      "gap_samples": gap_samples,
                      "start_sample": clock,
                      "end_sample": end,
                      "boundary_sample": boundary})
        chunks.extend([pcm, b"\x00\x00" * gap_samples])
        clock = boundary

    json.dump(metas, open(os.path.join(a.out, "timing.json"), "w"), indent=1, ensure_ascii=False)
    data = b"".join(chunks)
    header = (b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVEfmt " +
              struct.pack("<IHHIIHH", 16, 1, 1, a.sr, a.sr * 2, 2, 16) +
              b"data" + struct.pack("<I", len(data)))
    with open(os.path.join(a.out, "narration.wav"), "wb") as fh:
        fh.write(header + data)

    total = round(sum(m["dur"] for m in metas), 3)
    print(json.dumps(metas, ensure_ascii=False))
    print(f"total={total}s utterances={len(metas)}")


if __name__ == "__main__":
    main()
