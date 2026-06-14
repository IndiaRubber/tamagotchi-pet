from collections import deque
from pathlib import Path
from PIL import Image


SPRITE_ROOT = Path("assets/pets")

# Chroma colors we expect from generated images.
# Bright green is preferred.
GREEN_THRESHOLD = {
    "r_max": 80,
    "g_min": 160,
    "b_max": 120,
}

MAGENTA_THRESHOLD = {
    "r_min": 160,
    "g_max": 100,
    "b_min": 160,
}


def is_background_like(pixel):
    r, g, b, a = pixel

    if a == 0:
        return True

    green_bg = (
        r <= GREEN_THRESHOLD["r_max"]
        and g >= GREEN_THRESHOLD["g_min"]
        and b <= GREEN_THRESHOLD["b_max"]
    )

    magenta_bg = (
        r >= MAGENTA_THRESHOLD["r_min"]
        and g <= MAGENTA_THRESHOLD["g_max"]
        and b >= MAGENTA_THRESHOLD["b_min"]
    )

    return green_bg or magenta_bg


def border_has_chroma_background(img):
    """
    Safety check:
    Only process files that actually have chroma-key pixels on the border.
    This prevents the script from touching normal transparent sprites.
    """

    img = img.convert("RGBA")
    pixels = img.load()
    width, height = img.size

    for x in range(width):
        if is_background_like(pixels[x, 0]):
            return True
        if is_background_like(pixels[x, height - 1]):
            return True

    for y in range(height):
        if is_background_like(pixels[0, y]):
            return True
        if is_background_like(pixels[width - 1, y]):
            return True

    return False


def remove_connected_background(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")

    if not border_has_chroma_background(img):
        print(f"Skipped, no chroma border: {input_path}")
        return

    pixels = img.load()
    width, height = img.size

    visited = set()
    queue = deque()

    # Start flood fill from image borders only.
    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))

    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    while queue:
        x, y = queue.popleft()

        if (x, y) in visited:
            continue

        if x < 0 or y < 0 or x >= width or y >= height:
            continue

        visited.add((x, y))

        if not is_background_like(pixels[x, y]):
            continue

        pixels[x, y] = (0, 0, 0, 0)

        queue.append((x + 1, y))
        queue.append((x - 1, y))
        queue.append((x, y + 1))
        queue.append((x, y - 1))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    print(f"Cleaned: {output_path}")


def main():
    if not SPRITE_ROOT.exists():
        print(f"Missing sprite folder: {SPRITE_ROOT}")
        return

    png_files = sorted(SPRITE_ROOT.rglob("*.png"))

    if not png_files:
        print(f"No PNG files found under: {SPRITE_ROOT}")
        return

    for input_path in png_files:
        remove_connected_background(input_path, input_path)


if __name__ == "__main__":
    main()