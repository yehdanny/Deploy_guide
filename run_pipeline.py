"""
Main Pipeline Runner
Runs all steps in sequence for each article.
"""
import sys
import json
import asyncio
from pathlib import Path
from datetime import date
from config import OUTPUT_DIR


def run_pipeline(article_index: int = 0, skip_notebooklm: bool = False):
    """
    Run the full pipeline for one article.
    
    Args:
        article_index: Which article to process (0-based)
        skip_notebooklm: Skip NotebookLM step (use existing audio)
    """
    print("=" * 60)
    print(f"🚀 NotebookLM Podcast Pipeline")
    print(f"📅 {date.today().isoformat()}")
    print("=" * 60)
    
    # ── Step 1: Scrape CNBC ──
    print("\n" + "─" * 40)
    print("📰 STEP 1: Scraping CNBC AI articles")
    print("─" * 40)
    from step1_cnbc_scraper import main as scrape
    articles = scrape()
    
    if not articles or article_index >= len(articles):
        print(f"❌ No article at index {article_index}")
        return False
    
    article = articles[article_index]
    print(f"\n🎯 Selected: {article['title']}")
    
    # Create per-article output dir
    safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in article["title"][:50])
    article_dir = OUTPUT_DIR / f"{date.today().isoformat()}_{safe_name}"
    article_dir.mkdir(parents=True, exist_ok=True)
    
    # ── Step 2: NotebookLM ──
    if not skip_notebooklm:
        print("\n" + "─" * 40)
        print("🎙️ STEP 2: NotebookLM podcast generation")
        print("─" * 40)
        from step2_notebooklm import generate_podcast
        audio_path = article_dir / "podcast_raw.wav"
        result = asyncio.run(generate_podcast(
            article["title"], 
            article.get("content", ""),
            audio_path
        ))
        if not result:
            print("❌ NotebookLM failed. Aborting.")
            return False
    else:
        print("\n⏭️ Skipping NotebookLM (using existing audio)")
        audio_path = article_dir / "podcast_raw.wav"
        if not audio_path.exists():
            # Check for other formats
            for ext in [".mp3", ".m4a", ".webm"]:
                alt = audio_path.with_suffix(ext)
                if alt.exists():
                    audio_path = alt
                    break
    
    # ── Step 3: Split Audio ──
    print("\n" + "─" * 40)
    print("🔊 STEP 3: Splitting speaker audio")
    print("─" * 40)
    from step3_audio_split import split_speakers
    path_a, path_b, segments = split_speakers(audio_path, article_dir)
    
    # ── Step 4: SadTalker ──
    print("\n" + "─" * 40)
    print("🎭 STEP 4: Generating talking head videos")
    print("─" * 40)
    from step4_sadtalker import generate_talking_head, setup_sadtalker
    setup_sadtalker()
    
    from config import SPEAKER_A_IMAGE, SPEAKER_B_IMAGE
    
    video_a = generate_talking_head(
        SPEAKER_A_IMAGE, path_a,
        article_dir / "talker_a.mp4", "Speaker A"
    )
    video_b = generate_talking_head(
        SPEAKER_B_IMAGE, path_b,
        article_dir / "talker_b.mp4", "Speaker B"
    )
    
    if not video_a or not video_b:
        print("❌ SadTalker failed. Aborting.")
        return False
    
    # ── Step 5: Compose Video ──
    print("\n" + "─" * 40)
    print("🎬 STEP 5: Composing final video")
    print("─" * 40)
    from step5_compose_video import compose_switching_video
    segments_file = article_dir / "segments.json"
    final_video = compose_switching_video(
        video_a, video_b, segments_file,
        article_dir / "final_video.mp4",
        article["title"]
    )
    
    if not final_video:
        print("❌ Video composition failed. Aborting.")
        return False
    
    # ── Step 6: Thumbnail ──
    print("\n" + "─" * 40)
    print("🎨 STEP 6: Generating thumbnail")
    print("─" * 40)
    from step6_thumbnail import generate_thumbnail
    thumbnail = generate_thumbnail(
        topic=article["title"][:30],
        output_path=article_dir / "thumbnail.png"
    )
    
    # ── Step 7: Upload ──
    print("\n" + "─" * 40)
    print("📤 STEP 7: Uploading to YouTube")
    print("─" * 40)
    from step7_youtube_upload import upload_video
    
    title = f"小葉五分鐘說時事 - {article['title'][:50]}"
    description = (
        f"📰 {article['title']}\n\n"
        f"原文來源：{article.get('url', 'CNBC')}\n\n"
        f"本集由 AI 自動生成，使用 NotebookLM 語音摘要功能，"
        f"將 CNBC 當日 AI 科技新聞轉化為繁體中文雙人 Podcast。\n\n"
        f"#AI #人工智慧 #科技新聞 #CNBC #Podcast"
    )
    
    video_id = upload_video(
        video_path=final_video,
        title=title,
        description=description,
        thumbnail_path=thumbnail,
    )
    
    if video_id:
        print("\n" + "=" * 60)
        print(f"🎉 SUCCESS!")
        print(f"📺 https://www.youtube.com/watch?v={video_id}")
        print("=" * 60)
        return True
    else:
        print("\n❌ Upload failed")
        return False


def main():
    skip_nlm = "--skip-notebooklm" in sys.argv
    idx = 0
    
    for arg in sys.argv[1:]:
        if arg.isdigit():
            idx = int(arg)
    
    run_pipeline(article_index=idx, skip_notebooklm=skip_nlm)


if __name__ == "__main__":
    main()
