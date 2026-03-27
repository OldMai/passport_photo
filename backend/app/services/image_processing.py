"""Image processing service for cropping and resizing to passport size."""

from PIL import Image
from typing import Dict, Any
from app import config


def crop_to_passport_size(input_path: str, face_data: Dict[str, Any], output_path: str):
    """
    Crop and resize image to US passport photo size (2x2" at 600 DPI).

    Args:
        input_path: Path to input image (background already removed)
        face_data: Face detection results from face_detection.detect_face()
        output_path: Path to save output image

    The function:
    1. Calculates target head size based on passport requirements
    2. Scales image to achieve correct head size
    3. Positions face with eyes at 40% from top
    4. Crops to exact 1200x1200 pixels (2" x 2" at 600 DPI)
    """
    # Load image
    img = Image.open(input_path)
    width, height = img.size

    # Extract key data
    key_landmarks = face_data['key_landmarks']
    crown_y = key_landmarks['crown'][1]  # Normalized (0-1)
    chin_y = key_landmarks['chin'][1]
    left_eye_y = key_landmarks['left_eye'][1]
    right_eye_y = key_landmarks['right_eye'][1]
    face_center_x = face_data['face_center']['x']

    # Calculate current head height in pixels
    head_height_normalized = chin_y - crown_y
    head_height_px = head_height_normalized * height

    # Target: Head should be ~59.375% of image height
    # (average of 50-68.75% range = 1.1875"/2" ratio)
    target_head_percent = (config.HEAD_HEIGHT_MIN_PERCENT + config.HEAD_HEIGHT_MAX_PERCENT) / 2
    target_head_height_px = config.PASSPORT_SIZE_PIXELS * target_head_percent

    # Calculate scale factor
    if head_height_px > 0:
        scale_factor = target_head_height_px / head_height_px
    else:
        scale_factor = 1.0

    # Scale image
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    img_scaled = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Calculate average eye position in scaled image
    avg_eye_y_normalized = (left_eye_y + right_eye_y) / 2
    eyes_y_scaled = avg_eye_y_normalized * new_height

    # Target: Eyes should be at 40% from top (or 60% from bottom)
    target_eyes_y = config.PASSPORT_SIZE_PIXELS * 0.40

    # Calculate crop box to position eyes correctly
    crop_top = int(eyes_y_scaled - target_eyes_y)
    crop_bottom = crop_top + config.PASSPORT_SIZE_PIXELS

    # Center face horizontally
    face_center_x_scaled = face_center_x * new_width
    crop_left = int(face_center_x_scaled - config.PASSPORT_SIZE_PIXELS / 2)
    crop_right = crop_left + config.PASSPORT_SIZE_PIXELS

    # Ensure crop box is within image bounds
    # Adjust if crop would go outside image
    if crop_top < 0:
        crop_bottom -= crop_top
        crop_top = 0
    if crop_left < 0:
        crop_right -= crop_left
        crop_left = 0
    if crop_bottom > new_height:
        diff = crop_bottom - new_height
        crop_top -= diff
        crop_bottom = new_height
        # Ensure crop_top doesn't go negative
        if crop_top < 0:
            crop_top = 0
    if crop_right > new_width:
        diff = crop_right - new_width
        crop_left -= diff
        crop_right = new_width
        if crop_left < 0:
            crop_left = 0

    # Handle case where image is still too small after scaling
    crop_width = crop_right - crop_left
    crop_height = crop_bottom - crop_top

    if crop_width < config.PASSPORT_SIZE_PIXELS or crop_height < config.PASSPORT_SIZE_PIXELS:
        # Need to add padding (white background)
        # First crop what we can
        img_cropped = img_scaled.crop((crop_left, crop_top, crop_right, crop_bottom))

        # Create white canvas of target size
        img_final = Image.new('RGB', (config.PASSPORT_SIZE_PIXELS, config.PASSPORT_SIZE_PIXELS), (255, 255, 255))

        # Paste cropped image centered on canvas
        paste_x = (config.PASSPORT_SIZE_PIXELS - crop_width) // 2
        paste_y = (config.PASSPORT_SIZE_PIXELS - crop_height) // 2
        img_final.paste(img_cropped, (paste_x, paste_y))
    else:
        # Crop image
        img_cropped = img_scaled.crop((crop_left, crop_top, crop_right, crop_bottom))

        # Resize to exact target size (should already be close)
        img_final = img_cropped.resize(
            (config.PASSPORT_SIZE_PIXELS, config.PASSPORT_SIZE_PIXELS),
            Image.Resampling.LANCZOS
        )

    # Save with high quality and DPI metadata
    img_final.save(output_path, 'JPEG', quality=95, dpi=(config.DPI, config.DPI))
