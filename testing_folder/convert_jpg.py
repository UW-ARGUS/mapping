from PIL import Image
import os

def convert_png_to_jpg(png_path, jpg_path=None):
    if not os.path.exists(png_path):
        print(f"[✗] File not found: {png_path}")
        return

    # Set default jpg path if not provided
    if jpg_path is None:
        jpg_path = os.path.splitext(png_path)[0] + '.jpg'

    # Open and convert image
    with Image.open(png_path) as img:
        # Convert image mode if it has transparency
        if img.mode in ("RGBA", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            img = background
        else:
            img = img.convert("RGB")

        img.save(jpg_path, 'JPEG')
        print(f"[✓] Converted {png_path} → {jpg_path}")

# Example usage
convert_png_to_jpg('face1_resize.png')
convert_png_to_jpg('face2_resize.png')
convert_png_to_jpg('face3_resize.png')
convert_png_to_jpg('face4_resize.png')
