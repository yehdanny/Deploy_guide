"""
Step 5: Compose final video with FFmpeg.
- Two speaker videos side by side or switching view
- Key point cards overlay when topics change
- Reference style: talking head with topic cards
"""
import subprocess
import json
from pathlib import Path
from config import OUTPUT_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS


def create_keypoint_card(text: str, output_path: Path, 
                          width: int = 800, height: int = 200):
    """
    Create a key point card image using FFmpeg drawtext.
    These appear as overlays during topic transitions.
    """
    # Use FFmpeg to generate a card with text
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=0x1a1a2e:s={width}x{height}:d=1",
        "-vf", (
            f"drawtext=text='{text}'"
            f":fontsize=40"
            f":fontcolor=white"
            f":x=(w-text_w)/2"
            f":y=(h-text_h)/2"
            f":borderw=2"
            f":bordercolor=black"
            f":fontfile=C\\\\:/Windows/Fonts/msjh.ttc"
        ),
        "-frames:v", "1",
        str(output_path)
    ]
    
    subprocess.run(cmd, capture_output=True, check=True)
    return output_path


def compose_switching_video(
    video_a: Path,
    video_b: Path,
    segments_file: Path,
    output_path: Path,
    article_title: str = ""
):
    """
    Compose a video that switches between speakers based on segments.
    
    Layout reference (from the user's example):
    - Active speaker takes ~70% of screen
    - Inactive speaker in small PIP corner
    - Key point cards appear as overlays
    """
    print("🎬 Composing final video...")
    
    # Load segments
    with open(segments_file, encoding="utf-8") as f:
        segments = json.load(f)
    
    if not segments:
        print("❌ No segments found")
        return None
    
    total_duration = max(s["end_ms"] for s in segments) / 1000.0
    
    # Build FFmpeg filter complex for speaker switching
    # Main speaker gets full screen, other gets PIP in bottom-right
    
    # Scale both videos to target size
    pip_w = VIDEO_WIDTH // 4   # 480px
    pip_h = VIDEO_HEIGHT // 4  # 270px
    pip_x = VIDEO_WIDTH - pip_w - 20  # 20px margin from right
    pip_y = VIDEO_HEIGHT - pip_h - 20  # 20px margin from bottom
    
    # Build segment-based enable expressions for switching
    a_main_times = []
    b_main_times = []
    
    for seg in segments:
        start = seg["start_ms"] / 1000.0
        end = seg["end_ms"] / 1000.0
        if seg["speaker"] == "A":
            a_main_times.append((start, end))
        else:
            b_main_times.append((start, end))
    
    # Create the enable expression for when A is the main speaker
    def time_expr(times):
        parts = []
        for s, e in times:
            parts.append(f"between(t,{s:.2f},{e:.2f})")
        return "+".join(parts) if parts else "0"
    
    a_main_expr = time_expr(a_main_times)
    b_main_expr = time_expr(b_main_times)
    
    # FFmpeg filter: overlay approach
    # When A speaks: A is big, B is PIP
    # When B speaks: B is big, A is PIP
    filter_complex = (
        # Scale inputs
        f"[0:v]scale={VIDEO_WIDTH}:{VIDEO_HEIGHT},setsar=1[va_full];"
        f"[1:v]scale={VIDEO_WIDTH}:{VIDEO_HEIGHT},setsar=1[vb_full];"
        f"[0:v]scale={pip_w}:{pip_h},setsar=1[va_pip];"
        f"[1:v]scale={pip_w}:{pip_h},setsar=1[vb_pip];"
        
        # Create base: A full when A speaks, B full when B speaks
        # Use overlay with enable
        f"[va_full][vb_pip]overlay={pip_x}:{pip_y}:enable='{a_main_expr}'[scene_a];"
        f"[vb_full][va_pip]overlay={pip_x}:{pip_y}:enable='{b_main_expr}'[scene_b];"
        
        # Blend scenes (only one active at a time)
        f"[scene_a][scene_b]overlay=0:0:enable='{b_main_expr}'[vout]"
    )
    
    # Mix audio from both speakers
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_a),    # Input 0: Speaker A video
        "-i", str(video_b),    # Input 1: Speaker B video
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "0:a",         # Use original podcast audio instead
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        "-r", str(VIDEO_FPS),
        "-s", f"{VIDEO_WIDTH}x{VIDEO_HEIGHT}",
        "-t", str(total_duration),
        str(output_path)
    ]
    
    print(f"   Output: {output_path}")
    print(f"   Duration: {total_duration:.1f}s")
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    
    if result.returncode != 0:
        print(f"❌ FFmpeg failed: {result.stderr[-500:]}")
        
        # Fallback: simpler side-by-side layout
        print("🔄 Trying simpler side-by-side layout...")
        return compose_side_by_side(video_a, video_b, output_path, total_duration)
    
    print(f"✅ Final video: {output_path}")
    return output_path


def compose_side_by_side(video_a: Path, video_b: Path, 
                          output_path: Path, duration: float = None):
    """Fallback: simple side-by-side layout."""
    half_w = VIDEO_WIDTH // 2
    
    filter_complex = (
        f"[0:v]scale={half_w}:{VIDEO_HEIGHT},setsar=1[left];"
        f"[1:v]scale={half_w}:{VIDEO_HEIGHT},setsar=1[right];"
        f"[left][right]hstack=inputs=2[vout];"
        f"[0:a][1:a]amix=inputs=2:duration=longest[aout]"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_a),
        "-i", str(video_b),
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        "-r", str(VIDEO_FPS),
        str(output_path)
    ]
    
    if duration:
        cmd.insert(-1, "-t")
        cmd.insert(-1, str(duration))
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    
    if result.returncode != 0:
        print(f"❌ Side-by-side also failed: {result.stderr[-500:]}")
        return None
    
    print(f"✅ Side-by-side video: {output_path}")
    return output_path


def main():
    video_a = OUTPUT_DIR / "talker_a.mp4"
    video_b = OUTPUT_DIR / "talker_b.mp4"
    segments_file = OUTPUT_DIR / "segments.json"
    output = OUTPUT_DIR / "final_video.mp4"
    
    for f in [video_a, video_b, segments_file]:
        if not f.exists():
            print(f"❌ Missing: {f}")
            print("   Run previous steps first.")
            return
    
    compose_switching_video(video_a, video_b, segments_file, output)


if __name__ == "__main__":
    main()
