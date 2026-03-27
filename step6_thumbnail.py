"""
Step 6: Generate YouTube thumbnail from template.
- Load the user's template image
- Overlay date and topic text on the orange rectangle area
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from datetime import date
from config import OUTPUT_DIR, THUMBNAIL_TEMPLATE


# Orange rectangle region (approximate, adjust after testing with actual template)
# These coordinates define where the orange bar is in the template
ORANGE_RECT = {
    "left": 30,
    "top": 430,
    "right": 590,
    "bottom": 520,
}


def find_font(preferred_fonts=None):
    """Find a suitable CJK font on the system."""
    if preferred_fonts is None:
        preferred_fonts = [
            "C:/Windows/Fonts/msjhbd.ttc",   # Microsoft JhengHei Bold
            "C:/Windows/Fonts/msjh.ttc",      # Microsoft JhengHei
            "C:/Windows/Fonts/msyh.ttc",      # Microsoft YaHei
            "C:/Windows/Fonts/simsun.ttc",    # SimSun
            "C:/Windows/Fonts/arial.ttf",     # Fallback
        ]
    
    for font_path in preferred_fonts:
        if Path(font_path).exists():
            return font_path
    
    return None


def generate_thumbnail(
    topic: str,
    date_str: str = None,
    template_path: Path = None,
    output_path: Path = None
):
    """
    Generate thumbnail by overlaying text on the orange rectangle.
    
    Args:
        topic: Article/video topic text
        date_str: Date string (defaults to today)
        template_path: Path to template image
        output_path: Path to save output
    """
    if template_path is None:
        template_path = THUMBNAIL_TEMPLATE
    if output_path is None:
        output_path = OUTPUT_DIR / "thumbnail.png"
    if date_str is None:
        date_str = date.today().strftime("%Y/%m/%d")
    
    print(f"🎨 Generating thumbnail...")
    print(f"   Topic: {topic}")
    print(f"   Date: {date_str}")
    
    # Load template
    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        print("   Please place your thumbnail template at the path above.")
        return None
    
    img = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    
    # Calculate text area
    rect = ORANGE_RECT
    rect_width = rect["right"] - rect["left"]
    rect_height = rect["bottom"] - rect["top"]
    
    # Combined text: date + topic
    display_text = f"{date_str} {topic}"
    
    # Find font and size to fit the rectangle height
    font_path = find_font()
    if not font_path:
        print("⚠️ No CJK font found, using default")
        font = ImageFont.load_default()
    else:
        # Target font size = rectangle height (with some padding)
        target_height = int(rect_height * 0.85)
        font_size = target_height
        
        # Shrink font if text is too wide
        while font_size > 10:
            font = ImageFont.truetype(font_path, font_size)
            bbox = draw.textbbox((0, 0), display_text, font=font)
            text_width = bbox[2] - bbox[0]
            if text_width <= rect_width - 20:  # 10px padding each side
                break
            font_size -= 2
        
        font = ImageFont.truetype(font_path, font_size)
    
    # Calculate centered position within orange rect
    bbox = draw.textbbox((0, 0), display_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = rect["left"] + (rect_width - text_width) // 2
    y = rect["top"] + (rect_height - text_height) // 2
    
    # Draw text (white with slight shadow for readability)
    # Shadow
    draw.text((x + 2, y + 2), display_text, fill=(0, 0, 0, 180), font=font)
    # Main text
    draw.text((x, y), display_text, fill=(255, 255, 255, 255), font=font)
    
    # Save
    img.save(str(output_path), "PNG")
    print(f"✅ Thumbnail saved: {output_path}")
    
    return output_path


def main():
    # Test with sample data
    import json
    
    articles_file = sorted(OUTPUT_DIR.glob("articles_*.json"))
    if articles_file:
        with open(articles_file[-1], encoding="utf-8") as f:
            articles = json.load(f)
        if articles:
            generate_thumbnail(topic=articles[0]["title"][:30])
            return
    
    # Fallback test
    generate_thumbnail(topic="AI科技新聞摘要")


if __name__ == "__main__":
    main()
