---
name: gongzhonghaofengmian
description: Generate WeChat public account article cover images from a provided poster by using image generation/editing to create two new simplified cover designs, then stitch a 2.35:1 main cover and a 1:1 square thumbnail into a 3.35:1 horizontal cover. Use when the user asks for 公众号封面, 微信公众号封面, WeChat article cover, or turning a poster into generated dual cover images.
---

# 公众号封面

## Overview

Generate a single 3.35:1 horizontal WeChat public account cover from a supplied poster. The required workflow is to use image generation/editing to create two new simplified cover designs, then stitch them into the final canvas: a left 2.35:1 article-cover region and a right 1:1 thumbnail region.

Use `scripts/create_wechat_cover.py` only for deterministic stitching after the two cover images have been generated. Do not use it to crop the original poster as the final-quality result.

## Output Spec

- Final ratio: `3.35:1`.
- Default final size: `3350x1000`.
- Left region: `2350x1000` (`2.35:1`).
- Right region: `1000x1000` (`1:1`).
- Default format: PNG.
- Required behavior: generate two new cover images from the poster prompt, then compose them with `--right-source`.
- Deliver only the final stitched `3350x1000` image to the user-facing destination. Keep the intermediate `2350x1000` and `1000x1000` generated images in a temporary/workspace staging folder unless the user explicitly asks for them.
- Do not directly crop the original tall poster for final output. Cropping is acceptable only when the user explicitly asks for a rough preview.
- Do not add borders, guide lines, or text unless the user asks. The reference template with black outlines is only a layout guide.
- If the user passes a blank white layout reference by mistake, the script's default `--blank-mode auto` should treat it as a clean white canvas so old guide lines are not cropped into the output.

## Required Workflow

1. Get the source poster or key visual path from the user.
2. Use an image-generation or image-editing tool to create a new `2350x1000` left cover from the poster. This is a redesign, not a crop.
3. Use an image-generation or image-editing tool to create a new `1000x1000` right cover from the poster. This is a redesign, not a crop.
4. Use the reference poster only for style, subject, color, title text, and title hierarchy. Do not preserve all poster details.
5. Before prompting, inspect the poster palette and describe its exact visual feeling in the prompt: dominant background hue, brightness, saturation, accent colors, and text color. The generated covers must match the source poster's palette and brightness rather than drifting darker or moodier.
6. Use this prompt intent for both generation tasks:

```text
把这张图通过生成方式转化成公众号封面，只保留装饰部分和大小标题，标题居中并放大，其他培训时间、地点、费用、二维码、长段信息可以省略。严格按照原海报的配色、亮度和饱和度生成：背景必须匹配原海报的主色和明暗关系，强调色必须匹配原海报的荧光黄绿色/高亮色，标题保持原海报的白色粗体高对比效果。不要自动把画面调暗，不要改成更深的紫色、黑紫色、暗蓝紫或赛博夜景色调。保持原图的 AIGC 视觉设计风格、科技感装饰、柔和 3D 质感和核心视觉氛围。
```

7. For the left `2.35:1` cover, add:

```text
横版 2.35:1 构图，画布 2350x1000。主标题是第一视觉中心，居中或略偏左，保留核心视觉装饰，信息要少而醒目。
```

8. For the right `1:1` cover, add:

```text
方形 1:1 构图，画布 1000x1000。标题更集中，适合小尺寸缩略图阅读，保留一个最有识别度的主体或装饰。
```

9. Save the generated left and right cover images to a temporary/workspace staging folder, not the desktop or final user-facing destination, unless the user explicitly requests the separate files.
10. Stitch the two generated images:

```bash
python scripts/create_wechat_cover.py /path/to/left-2350x1000.png --right-source /path/to/right-1000x1000.png --output /path/to/final-cover.png
```

11. If the available Python lacks Pillow, use the bundled Codex Python runtime when available:

```bash
/Users/shaokaiyuan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/create_wechat_cover.py /path/to/left-2350x1000.png --right-source /path/to/right-1000x1000.png --output /path/to/final-cover.png
```

12. Verify the result dimensions. The width must equal `3.35 * height`; for the default size this is `3350x1000`.
13. Deliver only the final stitched image path. Do not mention or expose intermediate images unless the user asked for them.

## Palette Lock

- Match the source poster's colors tightly. If the poster uses light purple/lavender gradients, keep the generated covers light purple/lavender; do not convert them to dark purple.
- Preserve the source poster's brightness level. If the source is bright, glossy, and airy, the generated covers must also be bright, glossy, and airy.
- Preserve accent colors exactly by description: neon yellow-green should stay neon yellow-green, white title text should stay white, and secondary blue/pink accents should not dominate unless present in the source.
- Add this negative color constraint when prompting: `不要加深背景，不要使用暗紫、黑紫、深蓝紫、夜景霓虹、低曝光或高暗角效果。`
- Reject or regenerate outputs when the palette is visibly darker than the source poster.

## Rough Preview Only

Use direct cropping only when the user explicitly asks for a fast rough preview. Never present this as the final cover:

```bash
python scripts/create_wechat_cover.py /path/to/poster.png --output /path/to/draft-cover.png --left-focus top --right-focus top
```

## Stitching Guidance

- Generated inputs should already be `2350x1000` and `1000x1000`. The script will still fit them if needed, but exact-size generated images are preferred.
- Use a temporary/workspace staging folder for generated inputs. Only the final stitched image should be saved to the user's requested output location by default.
- Preserve the largest title and strongest visual identity in the left 2.35:1 area because it is the main article cover.
- Preserve a clean, recognizable title lockup in the right 1:1 area because it appears as the square thumbnail.
- Use `--right-source` for the generated `1000x1000` right cover.
- Use `--left-focus` and `--right-focus` only to fit already generated covers when their dimensions are slightly off, not to crop the original poster into the final result.
- Use `--export-parts` when the user also wants the separate `2.35:1` and `1:1` files.
- Use `--guide` only for checking layout; it draws a black outer border and divider like the provided reference image.
- Do not use a blank layout reference as a real poster. It is acceptable only for guide/template verification.

## Quality Check

Before final delivery, inspect the generated image or at least verify:

- The final canvas ratio is exactly `3.35:1`.
- The split is at `2.35 / 3.35` of the full width.
- There is only one internal divider when `--guide` is used.
- The left and right halves are newly generated cover designs, not cropped slices of a tall poster.
- The color palette and brightness are close to the source poster; reject noticeably darker, moodier, or differently colored outputs.
- No important title, subject, product, or logo is awkwardly cut off.
- Small poster details such as QR codes, schedules, prices, and long bullet lists are removed unless the user explicitly asks to keep them.
- The output does not include guide borders unless requested.
- Only one final stitched image is delivered by default; intermediate left/right generated images are not copied to the desktop or final destination unless explicitly requested.
