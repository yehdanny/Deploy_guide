"""
Pipeline Configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# FFmpeg path (winget install location)
FFMPEG_BIN = Path(os.environ.get("FFMPEG_BIN", r"C:\Users\ygz08\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin"))
if FFMPEG_BIN.exists() and str(FFMPEG_BIN) not in os.environ.get("PATH", ""):
    os.environ["PATH"] = str(FFMPEG_BIN) + os.pathsep + os.environ.get("PATH", "")

# Paths
PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"
ASSETS_DIR = PROJECT_ROOT / "assets"
SADTALKER_DIR = PROJECT_ROOT / "SadTalker"
COOKIES_DIR = PROJECT_ROOT / "cookies"

# Create dirs
for d in [OUTPUT_DIR, ASSETS_DIR, COOKIES_DIR]:
    d.mkdir(exist_ok=True)

# CNBC
CNBC_AI_URL = "https://www.cnbc.com/ai-artificial-intelligence/"

# NotebookLM
NOTEBOOKLM_URL = "https://notebooklm.google.com/"
NOTEBOOKLM_WAIT_SECONDS = 720  # 12 min max wait for audio generation

# SadTalker
SPEAKER_A_IMAGE = ASSETS_DIR / "speaker_a.png"
SPEAKER_B_IMAGE = ASSETS_DIR / "speaker_b.png"

# Video
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 25

# Thumbnail
THUMBNAIL_TEMPLATE = ASSETS_DIR / "thumbnail_template.png"

# YouTube
YOUTUBE_CLIENT_SECRETS = PROJECT_ROOT / "client_secrets.json"
YOUTUBE_TOKEN = PROJECT_ROOT / "youtube_token.json"
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
