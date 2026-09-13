from io import BytesIO

from PIL import Image

from scifigaudit.analysis import analyse_figure
from scifigaudit.report import report_json
from scifigaudit.sample import create_sample_figure
from scifigaudit.validation import validate_upload


def test_sample_is_valid_png():
    data = create_sample_figure()
    assert validate_upload(data, "image/png") is None
    image = Image.open(BytesIO(data))
    assert image.size == (1400, 1000)


def test_analysis_is_explainable_and_bounded():
    image = Image.open(BytesIO(create_sample_figure()))
    result = analyse_figure(image, "A fictional comparison of two samples across time, using shapes and colours.")
    assert 0 <= result.score <= 100
    assert len(result.checks) == 6
    assert all(check.evidence for check in result.checks)
    assert "journal approval" in result.scope_notice
    assert '"score"' in report_json(result)


def test_validation_rejects_empty_wrong_and_large_files():
    assert validate_upload(b"", "image/png")
    assert validate_upload(b"not an image", "image/png")
    assert validate_upload(b"\x89PNG\r\n\x1a\n" + b"0" * (10 * 1024 * 1024), "image/png")


def test_description_requires_meaningful_length():
    image = Image.new("RGB", (1000, 1000), "white")
    result = analyse_figure(image, "short")
    description = next(c for c in result.checks if c.key == "description")
    assert description.status == "review"


def test_content_touching_border_is_flagged():
    image = Image.new("RGB", (480, 300), (245, 245, 245))
    pixels = image.load()
    for y in range(300):
        pixels[3, y] = (180, 180, 180)
    result = analyse_figure(image, "")
    edge_check = next(c for c in result.checks if c.key == "edges")
    assert edge_check.status == "review"
