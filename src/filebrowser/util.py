from pathlib import Path

from PIL import Image, ImageOps


def format_bytes(amount: int) -> str:
    value = float(amount)

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024:
            return f"{value:.2f} {unit}"

        value /= 1024

    return f"{value:.2f} PB"

def thumbnail_image(target: Path, destination: Path) -> Path | None:
    try:
        with Image.open(target) as image:
            image.thumbnail((256, 256))
            image = ImageOps.exif_transpose(image)
            image.save(destination, "WEBP", quality=50, method=0)

    except Exception as e:
        print(e)
        return None

    return destination