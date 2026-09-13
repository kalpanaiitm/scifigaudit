from collections import Counter

import numpy as np
from PIL import Image

from .models import AuditResult, Check

SCOPE_NOTICE = (
    "Heuristic pre-submission screen only; not journal approval or an assessment of "
    "scientific validity, research integrity, or guaranteed accessibility."
)


def _check(key: str, label: str, status: str, message: str, evidence: str, weight: int) -> Check:
    return Check(key, label, status, message, evidence, weight)


def _dominant_colours(rgb: np.ndarray) -> list[tuple[int, int, int]]:
    small = Image.fromarray(rgb).resize((120, 120)).convert("RGB")
    quantized = small.quantize(colors=8).convert("RGB")
    pixels = np.asarray(quantized, dtype=np.uint8).reshape(-1, 3)
    counts = Counter(tuple(int(channel) for channel in pixel) for pixel in pixels)
    return [colour for colour, _ in counts.most_common(8)]


def _colour_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    # Weighted RGB distance: a transparent warning signal, not a clinical CVD model.
    dr, dg, db = (a[i] - b[i] for i in range(3))
    return float(np.sqrt(0.30 * dr * dr + 0.59 * dg * dg + 0.11 * db * db))


def analyse_figure(image: Image.Image, description: str = "") -> AuditResult:
    rgb_image = image.convert("RGB")
    rgb = np.asarray(rgb_image)
    width, height = rgb_image.size
    checks: list[Check] = []

    shortest = min(width, height)
    if shortest >= 1000:
        checks.append(_check("pixels", "Pixel dimensions", "pass", "The image has substantial pixel dimensions.", f"{width} × {height} pixels", 20))
    elif shortest >= 700:
        checks.append(_check("pixels", "Pixel dimensions", "review", "Dimensions may be adequate for some layouts; verify at final publication size.", f"{width} × {height} pixels", 20))
    else:
        checks.append(_check("pixels", "Pixel dimensions", "review", "The shorter edge is under 700 pixels and may reproduce poorly.", f"{width} × {height} pixels", 20))

    dpi = image.info.get("dpi")
    if dpi and min(dpi[:2]) >= 300:
        checks.append(_check("dpi", "Resolution metadata", "pass", "Embedded DPI metadata is at least 300.", f"Reported DPI: {dpi[0]:.0f} × {dpi[1]:.0f}", 10))
    else:
        evidence = "No reliable DPI metadata detected" if not dpi else f"Reported DPI: {dpi[0]:.0f} × {dpi[1]:.0f}"
        checks.append(_check("dpi", "Resolution metadata", "info", "Verify resolution against the target journal at the intended physical size.", evidence, 0))

    grey = np.asarray(rgb_image.convert("L"), dtype=np.float32)
    p1, p99 = np.percentile(grey, [1, 99])
    spread = float(p99 - p1)
    status = "pass" if spread >= 120 else "review"
    message = "The image has a broad luminance range." if status == "pass" else "The luminance range is limited; inspect labels and data marks for contrast."
    checks.append(_check("contrast", "Luminance contrast", status, message, f"1st–99th percentile spread: {spread:.1f}/255", 20))

    colours = _dominant_colours(rgb)
    data_colours = [
        c for c in colours
        if max(c) - min(c) >= 35 and sum(c) / 3 < 240
    ]
    distances = [_colour_distance(a, b) for i, a in enumerate(data_colours) for b in data_colours[i + 1 :]]
    min_distance = min(distances) if distances else 0.0
    colour_status = "pass" if len(data_colours) >= 2 and min_distance >= 28 else "review"
    colour_message = (
        "Dominant colours show reasonable weighted separation."
        if colour_status == "pass"
        else "Some dominant colours are similar; do not rely on colour alone to distinguish data."
    )
    evidence = f"{len(data_colours)} dominant data colour(s); minimum weighted distance: {min_distance:.1f}"
    checks.append(_check("colour", "Colour distinguishability", colour_status, colour_message, evidence, 20))

    border = max(3, round(min(width, height) * 0.02))
    centre = rgb[border:-border, border:-border] if width > 2 * border and height > 2 * border else rgb
    border_pixels = np.concatenate((rgb[:border].reshape(-1, 3), rgb[-border:].reshape(-1, 3), rgb[:, :border].reshape(-1, 3), rgb[:, -border:].reshape(-1, 3)))
    background = np.median(rgb.reshape(-1, 3).astype(float), axis=0)
    border_difference = np.mean(np.abs(border_pixels.astype(float) - background), axis=1)
    changed_border_fraction = float(np.mean(border_difference > 12))
    centre_variation = float(np.mean(np.std(centre.astype(float), axis=0)))
    crop_status = "review" if changed_border_fraction >= 0.01 else "pass"
    crop_message = "Important content may touch the image edge; inspect for clipping." if crop_status == "review" else "No strong edge-clipping signal was detected."
    evidence = f"Changed border pixels: {changed_border_fraction * 100:.1f}%; centre variation: {centre_variation:.1f}"
    checks.append(_check("edges", "Edge and cropping signal", crop_status, crop_message, evidence, 15))

    desc_len = len(description.strip())
    if 40 <= desc_len <= 1000:
        checks.append(_check("description", "Figure description", "pass", "A concise description was supplied for human review.", f"{desc_len} characters", 15))
    else:
        checks.append(_check("description", "Figure description", "review", "Add a concise description covering the figure's purpose and main visual relationships.", f"{desc_len} characters supplied", 15))

    earned = sum(c.weight for c in checks if c.status == "pass")
    possible = sum(c.weight for c in checks)
    score = round(100 * earned / possible) if possible else 0
    human_review = [
        "Confirm every axis, unit, legend, panel label, scale bar, and symbol is present and readable at final size.",
        "Confirm information is not conveyed by colour alone; use labels, shapes, line styles, or patterns as well.",
        "Compare file type, dimensions, resolution, and colour mode with the selected journal's current instructions.",
        "Check that the caption/alt text communicates the figure's purpose without claiming more than the data show.",
        "Inspect the original data and workflow; this app cannot detect manipulation, fabrication, or scientific errors.",
    ]
    return AuditResult(score, checks, human_review, SCOPE_NOTICE)
