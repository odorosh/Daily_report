import os
import sys
from PIL import Image, ImageDraw, ImageFont

# 1. Path to the Noto Color Emoji font on Fedora Linux.
# (If your system uses a different filename or path, please adjust it here)
FONT_PATH = "/usr/share/fonts/google-noto-color-emoji-fonts/Noto-COLRv1.ttf"

# Ensure the output directory is always created in the project root,
# even if this script is placed inside a subfolder like 'tools/'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "icons")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 2. Comprehensive dictionary mapping WMO weather codes to clean emoji symbols
weather_emoji_map = {
    0: '☀️',   # Clear sky
    1: '🌤️', 2: '⛅',  # Partly cloudy
    3: '☁️',   # Cloudy / Overcast
    45: '🌫️', 48: '🌫️',  # Fog and depositing rime fog
    51: '🌧️', 53: '🌧️', 55: '🌧️',  # Drizzle: Light, moderate, and dense intensity
    61: '🌧️', 63: '🌧️', 65: '🌧️',  # Rain: Slight, moderate, and heavy intensity
    71: '❄️', 73: '❄️', 75: '❄️',  # Snow fall: Slight, moderate, and heavy intensity
    80: '🌦️', 81: '🌦️', 82: '🌦️',  # Rain showers: Slight, moderate, and violent
    95: '⚡', 96: '⛈️', 99: '⛈️'   # Thunderstorm: Slight, moderate, and with heavy hail
}

# 3. Function to render a single emoji character into a transparent PNG file
def export_emoji_to_png(emoji_char, output_path):
    size = 128  # Target resolution for the icon (128x128 pixels is ideal for plotting)

    # Create an empty canvas with full alpha transparency (RGBA)
    # Fixed the color bounds from 256 to the correct max value of 255
    image = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    try:
        # Load the emoji font at the desired scaling size
        font = ImageFont.truetype(FONT_PATH, 100)

        # Draw the emoji character exactly in the center of the image canvas.
        # Passing embedded_color=True forces Pillow to render using full vector color assets.
        draw.text((size // 2, size // 2), emoji_char, font=font, fill="white", embedded_color=True, anchor="mm")

        # Save the resulting image as a transparent web-ready PNG file
        image.save(output_path, "PNG")
    except Exception as e:
        print(f"[ERROR] Failed to generate icon for emoji {emoji_char}: {e}", file=sys.stderr)

# 4. Main loop to generate all structured icons
print(f"[INFO] Generating colored assets using font: {FONT_PATH}")
for wmo_code, emoji in weather_emoji_map.items():
    file_path = os.path.join(OUTPUT_DIR, f"{wmo_code}.png")
    export_emoji_to_png(emoji, file_path)

print(f"[SUCCESS] All weather icons have been generated and saved to: {OUTPUT_DIR}/")
