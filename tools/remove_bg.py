from collections import deque
from pathlib import Path
from PIL import Image

INPUTS = [
    ("assets/pets/baby/idle_0.png", "assets/pets/baby/idle_0.png"),
    ("assets/pets/baby/idle_1.png", "assets/pets/baby/idle_1.png"),
    ("assets/pets/baby/happy_0.png", "assets/pets/baby/happy_0.png"),
    ("assets/pets/baby/sleep_0.png", "assets/pets/baby/sleep_0.png"),
    ("assets/pets/baby/hungry_0.png", "assets/pets/baby/hungry_0.png"),
    ("assets/pets/baby/dirty_0.png", "assets/pets/baby/dirty_0.png"),
    ("assets/pets/baby/tired_0.png", "assets/pets/baby/tired_0.png"),
    ("assets/pets/baby/sad_0.png", "assets/pets/baby/sad_0.png"),
    ("assets/pets/baby/sick_0.png", "assets/pets/baby/sick_0.png"),
]


def is_background_like(pixel):
    r, g, b, a = pixel

    if a == 0:
        return True

    # Checkerboard / near-white background only.
    # This is intentionally broad, but flood-fill keeps it from eating Bit's body.
    return r >= 215 and g >= 215 and b >= 215


def remove_connected_background(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
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
    print(f"Saved: {output_path}")


for input_file, output_file in INPUTS:
    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.exists():
        print(f"Missing: {input_path}")
        continue

    remove_connected_background(input_path, output_path)