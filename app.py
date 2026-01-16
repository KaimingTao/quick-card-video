import argparse
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip
import yaml


IPHONE15_SIZE = (1179, 2556)  # width, height in pixels


def load_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def wrap_text(text: str, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines = []
    current = words[0]
    for word in words[1:]:
        test = f"{current} {word}"
        if draw.textlength(test, font=font) <= max_width:
            current = test
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def load_config(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return {
        "font_size": int(data.get("font_size", 96)),
        "font_color": str(data.get("font_color", "#f8fafc")),
        "background_color": str(data.get("background_color", "#111827")),
    }


def render_image(text: str, size: tuple[int, int], config: dict) -> Image.Image:
    width, height = size
    bg = Image.new("RGB", (width, height), config["background_color"])
    draw = ImageDraw.Draw(bg)

    padding = 140
    max_width = width - padding * 2
    max_height = height - padding * 2

    font_size = config["font_size"]
    lines = []
    while font_size >= 36:
        font = load_font(font_size)
        lines = wrap_text(text, font, max_width, draw)
        line_bbox = font.getbbox("Ag")
        line_height = line_bbox[3] - line_bbox[1]
        spacing = int(line_height * 0.35)
        total_height = (line_height * len(lines)) + (spacing * (len(lines) - 1))
        max_line_width = max(draw.textlength(line, font=font) for line in lines)
        if total_height <= max_height and max_line_width <= max_width:
            break
        font_size -= 4

    line_bbox = font.getbbox("Ag")
    line_height = line_bbox[3] - line_bbox[1]
    spacing = int(line_height * 0.35)
    total_height = (line_height * len(lines)) + (spacing * (len(lines) - 1))
    start_y = (height - total_height) // 2

    for i, line in enumerate(lines):
        line_width = draw.textlength(line, font=font)
        x = (width - line_width) // 2
        y = start_y + i * (line_height + spacing)
        draw.text((x, y), line, font=font, fill=config["font_color"])

    return bg


def next_output_dir(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    candidate = base / today
    if not candidate.exists():
        candidate.mkdir()
        return candidate

    index = 2
    while True:
        candidate = base / f"{today}_{index}"
        if not candidate.exists():
            candidate.mkdir()
            return candidate
        index += 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a static image and 10s video from text.")
    parser.add_argument("text", nargs="*", help="Sentence(s) to render.")
    parser.add_argument("--output", default="outputs", help="Base output directory.")
    parser.add_argument("--duration", type=int, default=10, help="Video duration in seconds.")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second.")
    parser.add_argument("--config", default="config.yaml", help="Path to YAML config file.")
    args = parser.parse_args()

    if args.text:
        text = " ".join(args.text)
    else:
        text = input("Enter the sentence(s) to render: ").strip()
        if not text:
            raise SystemExit("No text provided.")
    config = load_config(Path(args.config))
    out_dir = next_output_dir(Path(args.output))
    image_path = out_dir / "figure.png"
    video_path = out_dir / "video.mp4"

    image = render_image(text, IPHONE15_SIZE, config)
    image.save(image_path)

    clip = ImageClip(str(image_path)).with_duration(args.duration).with_fps(args.fps)
    clip.write_videofile(str(video_path), codec="libx264", audio=False)

    print(f"Saved image to: {image_path}")
    print(f"Saved video to: {video_path}")


if __name__ == "__main__":
    main()
