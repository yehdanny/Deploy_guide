"""
Step 7: Upload video to YouTube via Data API v3.
"""
import json
import os
from pathlib import Path
from datetime import date

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config import (
    OUTPUT_DIR, YOUTUBE_CLIENT_SECRETS, 
    YOUTUBE_TOKEN, YOUTUBE_SCOPES
)


def get_youtube_service():
    """Authenticate and return YouTube API service."""
    creds = None
    
    # Load existing token
    if YOUTUBE_TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(YOUTUBE_TOKEN), YOUTUBE_SCOPES)
    
    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing YouTube token...")
            creds.refresh(Request())
        else:
            if not YOUTUBE_CLIENT_SECRETS.exists():
                print(f"❌ Client secrets not found: {YOUTUBE_CLIENT_SECRETS}")
                return None
            
            print("🔑 Starting OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(YOUTUBE_CLIENT_SECRETS), YOUTUBE_SCOPES
            )
            creds = flow.run_local_server(port=8080)
        
        # Save token
        with open(YOUTUBE_TOKEN, "w") as f:
            f.write(creds.to_json())
        print("✅ Token saved")
    
    return build("youtube", "v3", credentials=creds)


def upload_video(
    video_path: Path,
    title: str,
    description: str,
    tags: list = None,
    thumbnail_path: Path = None,
    category_id: str = "28",  # 28 = Science & Technology
    privacy: str = "public"
):
    """
    Upload a video to YouTube.
    
    Args:
        video_path: Path to the video file
        title: Video title
        description: Video description
        tags: List of tags
        thumbnail_path: Path to thumbnail image
        category_id: YouTube category ID
        privacy: "public", "unlisted", or "private"
    """
    youtube = get_youtube_service()
    if not youtube:
        return None
    
    if tags is None:
        tags = ["AI", "人工智慧", "科技新聞", "CNBC", "Podcast", "繁體中文"]
    
    print(f"📤 Uploading: {title}")
    print(f"   File: {video_path}")
    print(f"   Privacy: {privacy}")
    
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
            "defaultLanguage": "zh-TW",
            "defaultAudioLanguage": "zh-TW",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }
    
    media = MediaFileUpload(
        str(video_path),
        mimetype="video/mp4",
        resumable=True,
        chunksize=10 * 1024 * 1024  # 10MB chunks
    )
    
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )
    
    # Upload with progress
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            progress = int(status.progress() * 100)
            print(f"   ⏳ Upload progress: {progress}%")
    
    video_id = response["id"]
    print(f"✅ Uploaded! Video ID: {video_id}")
    print(f"   URL: https://www.youtube.com/watch?v={video_id}")
    
    # Set thumbnail if provided
    if thumbnail_path and thumbnail_path.exists():
        print("🎨 Setting thumbnail...")
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(thumbnail_path), mimetype="image/png")
            ).execute()
            print("✅ Thumbnail set")
        except Exception as e:
            print(f"⚠️ Thumbnail failed (may need verified account): {e}")
    
    return video_id


def main():
    video_path = OUTPUT_DIR / "final_video.mp4"
    thumbnail_path = OUTPUT_DIR / "thumbnail.png"
    
    if not video_path.exists():
        print("❌ No final video found. Run previous steps first.")
        return
    
    # Load article info for title/description
    articles_files = sorted(OUTPUT_DIR.glob("articles_*.json"))
    title = f"AI科技新聞 Podcast - {date.today().strftime('%Y/%m/%d')}"
    description = "由 NotebookLM 生成的繁體中文 AI 新聞 Podcast"
    
    if articles_files:
        with open(articles_files[-1], encoding="utf-8") as f:
            articles = json.load(f)
        if articles:
            article = articles[0]
            title = f"小葉五分鐘說時事 - {article['title'][:50]}"
            description = (
                f"📰 {article['title']}\n\n"
                f"原文來源：{article.get('url', 'CNBC')}\n\n"
                f"本集由 AI 自動生成，使用 NotebookLM 語音摘要功能，"
                f"將 CNBC 當日 AI 科技新聞轉化為繁體中文雙人 Podcast。\n\n"
                f"#AI #人工智慧 #科技新聞 #CNBC #Podcast"
            )
    
    video_id = upload_video(
        video_path=video_path,
        title=title,
        description=description,
        thumbnail_path=thumbnail_path if thumbnail_path.exists() else None,
    )
    
    if video_id:
        # Save upload info
        info = {
            "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "title": title,
            "date": date.today().isoformat(),
        }
        with open(OUTPUT_DIR / "upload_info.json", "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
