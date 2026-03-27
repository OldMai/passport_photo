"""Print layout generation service for passport photos."""

from PIL import Image, ImageDraw
from app import config


def generate_print_layout(passport_photo_path: str, output_path: str):
    """
    Generate 4x6" print layout with six 2x2" passport photos.

    Args:
        passport_photo_path: Path to the passport photo (1200x1200px at 600 DPI)
        output_path: Path to save the print layout

    Creates a standard 4x6" photo print layout at 300 DPI (1200x1800 pixels)
    with six 2x2" photos (600x600px at 300 DPI) arranged in a 2x3 grid.
    """
    # Load passport photo (1200x1200px at 600 DPI)
    passport_img = Image.open(passport_photo_path)

    # Create 4x6" canvas at 300 DPI
    canvas = Image.new('RGB', (config.PRINT_WIDTH_PIXELS, config.PRINT_HEIGHT_PIXELS), (255, 255, 255))

    # Resize passport photo to 2x2" at 300 DPI (600x600px)
    passport_img_resized = passport_img.resize(
        (config.PRINT_PHOTO_SIZE_PIXELS, config.PRINT_PHOTO_SIZE_PIXELS),
        Image.Resampling.LANCZOS
    )

    # Calculate positions for 2x3 grid (2 columns, 3 rows)
    # With margins and spacing
    margin = config.PRINT_MARGIN_PIXELS
    spacing = config.PRINT_MARGIN_PIXELS

    # Calculate positions
    positions = []
    for row in range(3):  # 3 rows
        for col in range(2):  # 2 columns
            x = margin + col * (config.PRINT_PHOTO_SIZE_PIXELS + spacing)
            y = margin + row * (config.PRINT_PHOTO_SIZE_PIXELS + spacing)
            positions.append((x, y))

    # Paste photos onto canvas
    for pos in positions:
        canvas.paste(passport_img_resized, pos)

    # Add cut line guides (light gray, dashed lines)
    draw = ImageDraw.Draw(canvas)
    line_color = (200, 200, 200)  # Light gray

    # Vertical cut lines (between columns)
    x_cut = margin + config.PRINT_PHOTO_SIZE_PIXELS + spacing // 2
    draw.line([(x_cut, 0), (x_cut, config.PRINT_HEIGHT_PIXELS)], fill=line_color, width=1)

    # Horizontal cut lines (between rows)
    for row in range(1, 3):
        y_cut = margin + row * (config.PRINT_PHOTO_SIZE_PIXELS + spacing) - spacing // 2
        draw.line([(0, y_cut), (config.PRINT_WIDTH_PIXELS, y_cut)], fill=line_color, width=1)

    # Save with print quality and DPI metadata
    canvas.save(output_path, 'JPEG', quality=95, dpi=(config.PRINT_DPI, config.PRINT_DPI))
