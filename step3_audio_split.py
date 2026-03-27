"""
Step 3: Split dual-host podcast audio into Speaker A and Speaker B tracks.
Uses energy-based voice activity detection + simple speaker diarization.
"""
import json
from pathlib import Path
from datetime import date
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import numpy as np
from config import OUTPUT_DIR


def split_speakers(audio_path: Path, output_dir: Path = None):
    """
    Split a two-speaker podcast into separate audio tracks.
    
    Strategy:
    1. Detect non-silent segments
    2. Alternate assignment (podcast format: A speaks, B speaks, ...)
    3. Output two separate audio files with silence padding to maintain timing
    
    For more accurate diarization, we can later integrate pyannote.audio
    or resemblyzer, but this works for NotebookLM's clean dual-host format.
    """
    if output_dir is None:
        output_dir = OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🎵 Loading audio: {audio_path}")
    audio = AudioSegment.from_file(str(audio_path))
    
    print(f"   Duration: {len(audio) / 1000:.1f}s")
    print(f"   Sample rate: {audio.frame_rate}Hz")
    print(f"   Channels: {audio.channels}")
    
    # Convert to mono if stereo
    if audio.channels > 1:
        audio = audio.set_channels(1)
    
    # Detect non-silent segments
    print("🔍 Detecting speech segments...")
    segments = detect_nonsilent(
        audio,
        min_silence_len=500,   # 500ms silence = segment break
        silence_thresh=-40,     # dBFS threshold
        seek_step=50           # 50ms resolution
    )
    
    print(f"   Found {len(segments)} speech segments")
    
    # Create two tracks with silence
    speaker_a = AudioSegment.silent(duration=len(audio))
    speaker_b = AudioSegment.silent(duration=len(audio))
    
    # Alternate assignment: odd segments = A, even = B
    segments_info = []
    for i, (start_ms, end_ms) in enumerate(segments):
        speaker = "A" if i % 2 == 0 else "B"
        segment_audio = audio[start_ms:end_ms]
        
        if speaker == "A":
            speaker_a = speaker_a.overlay(segment_audio, position=start_ms)
        else:
            speaker_b = speaker_b.overlay(segment_audio, position=start_ms)
        
        segments_info.append({
            "speaker": speaker,
            "start_ms": start_ms,
            "end_ms": end_ms,
            "duration_ms": end_ms - start_ms,
        })
        
        print(f"   Segment {i+1}: Speaker {speaker} [{start_ms/1000:.1f}s - {end_ms/1000:.1f}s]")
    
    # Export
    path_a = output_dir / "speaker_a.wav"
    path_b = output_dir / "speaker_b.wav"
    
    speaker_a.export(str(path_a), format="wav")
    speaker_b.export(str(path_b), format="wav")
    
    # Save segment info
    info_path = output_dir / "segments.json"
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump(segments_info, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Speaker A audio: {path_a}")
    print(f"✅ Speaker B audio: {path_b}")
    print(f"📋 Segments info: {info_path}")
    
    return path_a, path_b, segments_info


def main():
    audio_path = OUTPUT_DIR / "podcast_raw.wav"
    
    if not audio_path.exists():
        # Try other formats
        for ext in [".mp3", ".m4a", ".ogg", ".webm"]:
            alt = audio_path.with_suffix(ext)
            if alt.exists():
                audio_path = alt
                break
    
    if not audio_path.exists():
        print("❌ No podcast audio found. Run step 2 first.")
        return
    
    split_speakers(audio_path)


if __name__ == "__main__":
    main()
