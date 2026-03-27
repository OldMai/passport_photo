"""Shared fixtures for the passport photo test suite."""

import pytest
from unittest.mock import MagicMock


def _make_landmark(x: float, y: float, z: float = 0.0):
    """Create a mock MediaPipe landmark."""
    lm = MagicMock()
    lm.x = x
    lm.y = y
    lm.z = z
    return lm


@pytest.fixture
def valid_face_data():
    """A face_data dict that passes all validation checks."""
    # Build a minimal mock landmarks container with 468 points
    landmarks_mock = MagicMock()
    coords = {
        10: (0.50, 0.10),   # crown
        152: (0.50, 0.70),  # chin  → head_height = 0.60 (within 50-68.75%)
        33: (0.42, 0.40),   # left_eye
        263: (0.58, 0.40),  # right_eye
        1: (0.50, 0.52),    # nose
        234: (0.25, 0.45),  # left_ear
        454: (0.75, 0.45),  # right_ear
    }
    landmarks_mock.landmark = {
        idx: _make_landmark(x, y) for idx, (x, y) in coords.items()
    }

    return {
        "bbox": {"xmin": 0.3, "ymin": 0.1, "width": 0.4, "height": 0.6},
        "landmarks": landmarks_mock,
        "key_landmarks": {
            "crown":      (0.50, 0.10, 0.0),
            "chin":       (0.50, 0.70, 0.0),
            # eyes_y=0.62 → within valid range 0.55–0.70
            "left_eye":   (0.42, 0.62, 0.0),
            "right_eye":  (0.58, 0.62, 0.0),
            # nose symmetric between eyes → asymmetry ≈ 0
            "nose":       (0.50, 0.66, 0.0),
            "left_ear":   (0.25, 0.62, 0.0),
            "right_ear":  (0.75, 0.62, 0.0),
        },
        "face_center": {"x": 0.50, "y": 0.62},
        "head_height_normalized": 0.60,
        "image_shape": {"width": 800, "height": 1000},
    }
