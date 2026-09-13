from io import BytesIO

from PIL import Image, ImageDraw


def create_sample_figure() -> bytes:
    image = Image.new("RGB", (1400, 1000), "white")
    draw = ImageDraw.Draw(image)
    draw.text((80, 45), "Fictional catalyst stability study", fill="black")
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
    draw.text((570, 900), "Time (fictional units)", fill="black")
    draw.text((1020, 100), "● Sample A   ■ Sample B", fill="black")
    output = BytesIO()
    image.save(output, format="PNG", dpi=(300, 300))
    return output.getvalue()

