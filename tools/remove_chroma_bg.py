from collections import deque
from pathlib import Path
from PIL import Image


INPUTS = [
    ("assets/pets/baby/happy_1.png", "assets/pets/baby/happy_1.png"),
]


def is_background_like(pixel):
    r, g, b, a = pixel

    if a == 0:
        return True

    # Bright green chroma key
    green_bg = g >= 180 and r <= 80 and b <= 120

    # Bright magenta chroma key
    magenta_bg = r >= 180 and b >= 180 and g <= 100

    return green_bg or magenta_bg


def remove_connected_background(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    pixels = img.load()
    width, height = img.size

    visited = set()
    queue = deque()

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
    print(f"Saved: {output_path}")


for input_file, output_file in INPUTS:
    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.exists():
        print(f"Missing: {input_path}")
        continue

    remove_connected_background(input_path, output_path)