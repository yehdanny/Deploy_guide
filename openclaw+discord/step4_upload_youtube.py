"""
Step 4: Upload video to YouTube as a Short
Uses YouTube Data API v3 with OAuth2 authentication.
"""
import json
import os
import sys
import http.client
import httplib2
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")
CLIENT_SECRET_FILE = os.path.join(CONFIG_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(CONFIG_DIR, "token.json")

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    """Get authenticated YouTube service."""
    creds = None
    
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing access token...")
            creds.refresh(Request())
        else:
            print("🔐 Starting OAuth2 authorization flow...")
            print("   A browser window will open for you to authorize.")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=8080, prompt="consent")
        
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        print("✅ Authorization successful!")
    
    return build("youtube", "v3", credentials=creds)

def upload_video(youtube, video_file, metadata, settings):
    """Upload video to YouTube."""
    yt_settings = settings["youtube"]
    
    body = {
        "snippet": {
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata.get("tags", []) + yt_settings.get("tags", []),
            "categoryId": yt_settings["category_id"],
            "defaultLanguage": yt_settings.get("default_language", "zh-TW"),
        },
        "status": {
            "privacyStatus": yt_settings.get("privacy_status", "public"),
            "selfDeclaredMadeForKids": False,
            "shorts": {
                "title": metadata["title"][:40]  # Shorts title
            }
        }
    }
    
    # Remove shorts if API doesn't support it (older API versions)
    # The #shorts tag in title/description helps YouTube recognize it
    if "#shorts" not in metadata["title"].lower():
        body["snippet"]["title"] = metadata["title"]
    
    media = MediaFileUpload(
        video_file,
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024  # 1MB chunks
    )
    
    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media
    )
    
    print(f"📤 Uploading: {metadata['title']}")
    print(f"   File: {video_file}")
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"   Progress: {int(status.progress() * 100)}%")
    
    video_id = response["id"]
    video_url = f"https://youtube.com/shorts/{video_id}"
    
    print(f"\n✅ Upload complete!")
    print(f"🎬 Video ID: {video_id}")
    print(f"🔗 URL: {video_url}")
    
    return video_id, video_url

def main(job_dir):
    job_file = os.path.join(job_dir, "job.json")
    with open(job_file, "r", encoding="utf-8") as f:
        job = json.load(f)
    
    if job["status"] not in ("audio_added", "video_generated"):
        print(f"⚠️ Job status is '{job['status']}', expected 'audio_added' or 'video_generated'")
        if job["status"] == "uploaded":
            print(f"   Already uploaded: {job.get('youtube_url')}")
            return
        return
    
    # Use audio version if available, otherwise raw video
    video_file = job.get("final_video") or job.get("video_file")
    if not video_file or not os.path.exists(video_file):
        print(f"❌ Video file not found: {video_file}")
        return
    
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        settings = json.load(f)
    
    youtube = get_authenticated_service()
    video_id, video_url = upload_video(youtube, video_file, job["metadata"], settings)
    
    job["status"] = "uploaded"
    job["youtube_video_id"] = video_id
    job["youtube_url"] = video_url
    with open(job_file, "w", encoding="utf-8") as f:
        json.dump(job, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 Pipeline complete! Video is live at: {video_url}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python step4_upload_youtube.py <job_dir>")
        sys.exit(1)
    main(sys.argv[1])
