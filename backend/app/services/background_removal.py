"""Background removal service using rembg."""

from PIL import Image
from rembg import remove


def remove_background(input_path: str, output_path: str, bg_color: tuple = (255, 255, 255)):
    """
    Remove background from image and replace with solid color.

    Args:
        input_path: Path to input image
        output_path: Path to save output image
        bg_color: RGB tuple for background color (default: white)

    Raises:
        Exception: If background removal fails
    """
    try:
        # Load input image
        input_image = Image.open(input_path)

        # Remove background using rembg (U2-Net model)
        # This returns image with transparent background (RGBA)
        output_image = remove(input_image)

        # Create new image with specified background color
        bg_image = Image.new('RGB', output_image.size, bg_color)

        # Paste the person onto the background
        # The alpha channel (transparency) is used as mask
        bg_image.paste(output_image, (0, 0), output_image)

        # Save as JPEG with high quality
        bg_image.save(output_path, 'JPEG', quality=95)

    except Exception as e:
        raise Exception(f"Background removal failed: {str(e)}")
