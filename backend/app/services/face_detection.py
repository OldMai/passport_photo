"""Face detection and landmark extraction using MediaPipe."""

import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, Any


def detect_face(image_path: str) -> Dict[str, Any]:
    """
    Detect face and extract landmarks from image.

    Args:
        image_path: Path to the image file

    Returns:
        Dictionary containing face bounding box, landmarks, and image shape

    Raises:
        ValueError: If no face or multiple faces detected
    """
    # Initialize MediaPipe
    mp_face_detection = mp.solutions.face_detection
    mp_face_mesh = mp.solutions.face_mesh

    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Failed to load image")

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width = image.shape[:2]

    # Detect face bounding box
    with mp_face_detection.FaceDetection(
        model_selection=1,  # Full-range model (better for portraits)
        min_detection_confidence=0.5
    ) as face_detection:
        results = face_detection.process(image_rgb)

        if not results.detections:
            raise ValueError("No face detected in the image")

        if len(results.detections) > 1:
            raise ValueError("Multiple faces detected. Please use an image with only one person")

        detection = results.detections[0]
        bbox = detection.location_data.relative_bounding_box

    # Get detailed face landmarks (468 points)
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5
    ) as face_mesh:
        results = face_mesh.process(image_rgb)

        if not results.multi_face_landmarks:
            raise ValueError("Failed to extract face landmarks")

        landmarks = results.multi_face_landmarks[0]

    # Extract key landmark points (convert from normalized to pixel coordinates)
    def get_landmark_coords(landmark_idx: int) -> tuple:
        """Get pixel coordinates of a landmark."""
        lm = landmarks.landmark[landmark_idx]
        return (lm.x, lm.y, lm.z)

    # Key landmarks for passport photo processing:
    # - Crown (top of head): landmark 10
    # - Chin (bottom): landmark 152
    # - Left eye: landmark 33
    # - Right eye: landmark 263
    # - Nose tip: landmark 1
    # - Left ear: landmark 234
    # - Right ear: landmark 454

    key_landmarks = {
        'crown': get_landmark_coords(10),
        'chin': get_landmark_coords(152),
        'left_eye': get_landmark_coords(33),
        'right_eye': get_landmark_coords(263),
        'nose': get_landmark_coords(1),
        'left_ear': get_landmark_coords(234),
        'right_ear': get_landmark_coords(454)
    }

    # Calculate face center
    face_center_x = (key_landmarks['left_eye'][0] + key_landmarks['right_eye'][0]) / 2
    face_center_y = (key_landmarks['left_eye'][1] + key_landmarks['right_eye'][1]) / 2

    # Calculate head height (crown to chin)
    head_height = key_landmarks['chin'][1] - key_landmarks['crown'][1]

    return {
        'bbox': {
            'xmin': bbox.xmin,
            'ymin': bbox.ymin,
            'width': bbox.width,
            'height': bbox.height
        },
        'landmarks': landmarks,
        'key_landmarks': key_landmarks,
        'face_center': {'x': face_center_x, 'y': face_center_y},
        'head_height_normalized': head_height,
        'image_shape': {'width': width, 'height': height}
    }
