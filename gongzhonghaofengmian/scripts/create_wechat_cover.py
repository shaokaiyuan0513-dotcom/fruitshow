#!/usr/bin/env python3
"""Compose a 3.35:1 WeChat public account cover from cover images."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Tuple

try:
    from PIL import Image, ImageOps
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Pillow is required. Use the Codex bundled Python runtime or install Pillow."
    ) from exc


FOCUS_PRESETS = {
    "center": (0.5, 0.5),
    "top": (0.5, 0.0),
    "bottom": (0.5, 1.0),
    "left": (0.0, 0.5),
    "right": (1.0, 0.5),
    "top-left": (0.0, 0.0),
    "top-right": (1.0, 0.0),
    "bottom-left": (0.0, 1.0),
    "bottom-right": (1.0, 1.0),
}


def parse_focus(value: str) -> Tuple[float, float]:
    normalized = value.strip().lower()
    if normalized in FOCUS_PRESETS:
        return FOCUS_PRESETS[normalized]

    if "," in normalized:
        x_raw, y_raw = normalized.split(",", 1)
        try:
            x = float(x_raw) / 100.0
            y = float(y_raw) / 100.0
        except ValueError as exc:
            raise argparse.ArgumentTypeError(
                "Custom focus must be two percentages like 42,55."
            ) from exc
        if 0 <= x <= 1 and 0 <= y <= 1:
            return x, y

    raise argparse.ArgumentTypeError(
        "Focus must be a preset or two percentages like 42,55."
    )


def cover_crop(image: Image.Image, target_size: Tuple[int, int], focus: Tuple[float, float]) -> Image.Image:
    src_w, src_h = image.size
    target_w, target_h = target_size
    src_ratio = src_w / src_h
    target_ratio = target_w / target_h

    if src_ratio > target_ratio:
        crop_h = src_h
        crop_w = round(crop_h * target_ratio)
    else:
        crop_w = src_w
        crop_h = round(crop_w / target_ratio)

    max_left = src_w - crop_w
    max_top = src_h - crop_h
    left = round(max_left * focus[0])
    top = round(max_top * focus[1])
    box = (left, top, left + crop_w, top + crop_h)

    cropped = image.crop(box)
    return cropped.resize(target_size, Image.Resampling.LANCZOS)


def is_blank_layout_guide(image: Image.Image) -> bool:
    sample = image.convert("L").resize((160, 48), Image.Resampling.BILINEAR)
    if hasattr(sample, "get_flattened_data"):
        pixels = list(sample.get_flattened_data())
    else:
        pixels = list(sample.getdata())
    near_white = sum(1 for value in pixels if value >= 245)
    near_black = sum(1 for value in pixels if value <= 35)
    total = len(pixels)

    # Detect the provided white template with black guide lines. Real posters
    # should not be routed through this branch even when they contain whitespace.
    return (near_white / total) >= 0.93 and (near_black / total) <= 0.08


def output_default(source: Path) -> Path:
    return source.with_name(f"{source.stem}_gongzhonghao_cover.png")


def save_parts(canvas: Image.Image, output: Path, left_width: int, height: int) -> None:
    left = canvas.crop((0, 0, left_width, height))
    right = canvas.crop((left_width, 0, left_width + height, height))
    left.save(output.with_name(f"{output.stem}_left_2.35x1.png"))
    right.save(output.with_name(f"{output.stem}_right_1x1.png"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compose a 3.35:1 WeChat public account cover from left and right cover images."
    )
    parser.add_argument("source", type=Path, help="Left 2.35:1 cover image, or a poster for quick draft cropping.")
    parser.add_argument("--output", "-o", type=Path, help="Output PNG path.")
    parser.add_argument("--right-source", type=Path, help="Separate right 1:1 cover image. Recommended for final output.")
    parser.add_argument("--height", type=int, default=1000, help="Output height in pixels. Default: 1000.")
    parser.add_argument("--left-focus", type=parse_focus, default=parse_focus("center"))
    parser.add_argument("--right-focus", type=parse_focus, default=parse_focus("center"))
    parser.add_argument("--guide", action="store_true", help="Draw black border and divider for layout checking.")
    parser.add_argument(
        "--blank-mode",
        choices=("auto", "never", "always"),
        default="auto",
        help="Handle blank layout-guide images as clean white canvas. Default: auto.",
    )
    parser.add_argument("--export-parts", action="store_true", help="Also export separate left and right images.")
    args = parser.parse_args()

    if args.height <= 0:
        raise SystemExit("--height must be positive.")

    source = args.source.expanduser().resolve()
    output = (args.output.expanduser().resolve() if args.output else output_default(source))
    right_source = (args.right_source.expanduser().resolve() if args.right_source else source)

    left_width = round(args.height * 2.35)
    right_width = args.height
    total_width = left_width + right_width

    canvas = Image.new("RGB", (total_width, args.height), "white")

    with Image.open(source) as left_img:
        left_img = ImageOps.exif_transpose(left_img).convert("RGB")
        blank_source = args.blank_mode == "always" or (
            args.blank_mode == "auto" and is_blank_layout_guide(left_img)
        )
        if not blank_source:
            left_region = cover_crop(left_img, (left_width, args.height), args.left_focus)
            canvas.paste(left_region, (0, 0))

    if not blank_source:
        with Image.open(right_source) as right_img:
            right_img = ImageOps.exif_transpose(right_img).convert("RGB")
            right_region = cover_crop(right_img, (right_width, args.height), args.right_focus)
            canvas.paste(right_region, (left_width, 0))

    if args.guide:
        from PIL import ImageDraw

        draw = ImageDraw.Draw(canvas)
        draw.rectangle((0, 0, total_width - 1, args.height - 1), outline="black", width=4)
        draw.line((left_width, 0, left_width, args.height), fill="black", width=4)

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)
    if args.export_parts:
        save_parts(canvas, output, left_width, args.height)

    print(f"Saved {output}")
    print(f"Size: {total_width}x{args.height}")
    print(f"Split: left {left_width}x{args.height}, right {right_width}x{args.height}")


if __name__ == "__main__":
    main()
