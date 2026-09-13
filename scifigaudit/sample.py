from io import BytesIO

from PIL import Image, ImageDraw, ImageFont


def create_sample_figure() -> bytes:
    image = Image.new("RGB", (1400, 1000), "white")
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.load_default(size=34)
    label_font = ImageFont.load_default(size=26)
    draw.text((80, 45), "Fictional catalyst stability study", fill="black", font=title_font)
    draw.line((120, 850, 1300, 850), fill="black", width=5)
    draw.line((120, 150, 120, 850), fill="black", width=5)
    points_a = [(150, 720), (350, 610), (550, 500), (750, 430), (950, 360), (1200, 300)]
    points_b = [(150, 760), (350, 700), (550, 650), (750, 570), (950, 520), (1200, 470)]
    draw.line(points_a, fill=(0, 90, 170), width=12)
    draw.line(points_b, fill=(220, 120, 0), width=12)
    for point in points_a:
        draw.ellipse((point[0]-10, point[1]-10, point[0]+10, point[1]+10), fill=(0, 90, 170))
    for point in points_b:
        draw.rectangle((point[0]-10, point[1]-10, point[0]+10, point[1]+10), fill=(220, 120, 0))
    draw.text((550, 900), "Time (fictional units)", fill="black", font=label_font)
    draw.ellipse((1010, 98, 1034, 122), fill=(0, 90, 170))
    draw.text((1045, 94), "Sample A", fill="black", font=label_font)
    draw.rectangle((1180, 98, 1204, 122), fill=(220, 120, 0))
    draw.text((1215, 94), "Sample B", fill="black", font=label_font)
    output = BytesIO()
    image.save(output, format="PNG", dpi=(300, 300))
    return output.getvalue()
