"""Validation service for US passport photo requirements."""

import cv2
from typing import Dict, Any
from app import config


def validate_passport_photo(face_data: Dict[str, Any], image_path: str) -> Dict[str, Any]:
    """
    Validate photo against US passport requirements.

    Args:
        face_data: Face detection results from face_detection.detect_face()
        image_path: Path to the image file

    Returns:
        Dictionary with validation results and pass/fail for each check
    """
    # Load image to get actual dimensions
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Failed to load image for validation")

    height, width = image.shape[:2]

    validation_results = {
        'passed': True,
        'checks': {}
    }

    # Extract data from face_data
    key_landmarks = face_data['key_landmarks']
    face_center = face_data['face_center']
    head_height_normalized = face_data['head_height_normalized']

    # 1. Resolution Check
    resolution_ok = width >= config.MIN_RESOLUTION and height >= config.MIN_RESOLUTION
    validation_results['checks']['resolution'] = {
        'passed': resolution_ok,
        'message': f'Resolution: {width}x{height}px (minimum: {config.MIN_RESOLUTION}x{config.MIN_RESOLUTION}px)',
        'actual': {'width': width, 'height': height},
        'required': {'width': config.MIN_RESOLUTION, 'height': config.MIN_RESOLUTION}
    }

    # 2. Head Size Check
    # Head height should be 50-68.75% of image height
    head_size_ok = (
        config.HEAD_HEIGHT_MIN_PERCENT <= head_height_normalized <= config.HEAD_HEIGHT_MAX_PERCENT
    )
    head_height_px = int(head_height_normalized * height)
    target_min_px = int(config.HEAD_HEIGHT_MIN_PERCENT * height)
    target_max_px = int(config.HEAD_HEIGHT_MAX_PERCENT * height)

    validation_results['checks']['head_size'] = {
        'passed': head_size_ok,
        'message': f'Head height: {head_height_px}px (target: {target_min_px}-{target_max_px}px)',
        'head_height_px': head_height_px,
        'target_range': [target_min_px, target_max_px],
        'percentage': round(head_height_normalized * 100, 1)
    }

    # 3. Face Centered Check
    # Face center should be within 40-60% horizontally
    face_centered = (
        config.FACE_CENTER_MIN_X <= face_center['x'] <= config.FACE_CENTER_MAX_X
    )
    validation_results['checks']['face_centered'] = {
        'passed': face_centered,
        'message': 'Face is centered' if face_centered else 'Face should be more centered',
        'face_center_x': round(face_center['x'], 3),
        'target_range': [config.FACE_CENTER_MIN_X, config.FACE_CENTER_MAX_X]
    }

    # 4. Eyes Level Check
    # Eyes should be at 55-70% from bottom (or 30-45% from top)
    avg_eye_y = (key_landmarks['left_eye'][1] + key_landmarks['right_eye'][1]) / 2
    eyes_level_ok = config.EYES_LEVEL_MIN_Y <= avg_eye_y <= config.EYES_LEVEL_MAX_Y

    validation_results['checks']['eyes_level'] = {
        'passed': eyes_level_ok,
        'message': 'Eyes at correct level' if eyes_level_ok else 'Eyes should be positioned at proper level',
        'eyes_y_position': round(avg_eye_y, 3),
        'target_range': [config.EYES_LEVEL_MIN_Y, config.EYES_LEVEL_MAX_Y]
    }

    # 5. Face Forward Check (angle/symmetry)
    # Compare left/right eye distances from nose
    nose_x = key_landmarks['nose'][0]
    left_eye_x = key_landmarks['left_eye'][0]
    right_eye_x = key_landmarks['right_eye'][0]

    left_dist = abs(nose_x - left_eye_x)
    right_dist = abs(nose_x - right_eye_x)

    if max(left_dist, right_dist) > 0:
        asymmetry_ratio = abs(left_dist - right_dist) / max(left_dist, right_dist)
    else:
        asymmetry_ratio = 0

    face_forward = asymmetry_ratio < config.FACE_ANGLE_ASYMMETRY_MAX

    validation_results['checks']['face_forward'] = {
        'passed': face_forward,
        'message': 'Face is forward' if face_forward else 'Face should face more directly forward',
        'asymmetry_ratio': round(asymmetry_ratio, 3),
        'max_allowed': config.FACE_ANGLE_ASYMMETRY_MAX
    }

    # Overall pass/fail - all checks must pass
    validation_results['passed'] = all(
        check['passed'] for check in validation_results['checks'].values()
    )

    return validation_results
