"""Failure-case tests for the validation service."""

import copy
import pytest
from unittest.mock import patch
import numpy as np


def _make_image_array(width=800, height=1000):
    return np.zeros((height, width, 3), dtype="uint8")


class TestValidationFailureCases:

    @patch("cv2.imread")
    def test_image_not_loadable_raises(self, mock_imread, valid_face_data):
        """cv2.imread returning None → ValueError."""
        mock_imread.return_value = None
        from app.services.validation import validate_passport_photo

        with pytest.raises(ValueError, match="Failed to load image"):
            validate_passport_photo(valid_face_data, "/nonexistent.jpg")

    @patch("cv2.imread")
    def test_resolution_too_low_fails(self, mock_imread, valid_face_data):
        """Image smaller than MIN_RESOLUTION (600px) → resolution check fails."""
        mock_imread.return_value = _make_image_array(400, 400)
        from app.services.validation import validate_passport_photo

        result = validate_passport_photo(valid_face_data, "photo.jpg")

        assert result["checks"]["resolution"]["passed"] is False
        assert result["passed"] is False

    @patch("cv2.imread")
    def test_head_too_small_fails(self, mock_imread, valid_face_data):
        """Head height below 50% of image height → head_size check fails."""
        mock_imread.return_value = _make_image_array(800, 1000)
        face_data = copy.deepcopy(valid_face_data)
        # head_height_normalized = 0.30 < 0.50 minimum
        face_data["head_height_normalized"] = 0.30
        face_data["key_landmarks"]["crown"] = (0.50, 0.20, 0.0)
        face_data["key_landmarks"]["chin"] = (0.50, 0.50, 0.0)

        from app.services.validation import validate_passport_photo

        result = validate_passport_photo(face_data, "photo.jpg")

        assert result["checks"]["head_size"]["passed"] is False
        assert result["passed"] is False

    @patch("cv2.imread")
    def test_head_too_large_fails(self, mock_imread, valid_face_data):
        """Head height above 68.75% of image height → head_size check fails."""
        mock_imread.return_value = _make_image_array(800, 1000)
        face_data = copy.deepcopy(valid_face_data)
        # head_height_normalized = 0.80 > 0.6875 maximum
        face_data["head_height_normalized"] = 0.80
        face_data["key_landmarks"]["crown"] = (0.50, 0.05, 0.0)
        face_data["key_landmarks"]["chin"] = (0.50, 0.85, 0.0)

        from app.services.validation import validate_passport_photo

        result = validate_passport_photo(face_data, "photo.jpg")

        assert result["checks"]["head_size"]["passed"] is False
        assert result["passed"] is False

    @patch("cv2.imread")
    def test_face_not_centered_fails(self, mock_imread, valid_face_data):
        """Face center X outside 40-60% → face_centered check fails."""
        mock_imread.return_value = _make_image_array(800, 1000)
        face_data = copy.deepcopy(valid_face_data)
        # Push face to the far right
        face_data["face_center"]["x"] = 0.80

        from app.services.validation import validate_passport_photo

        result = validate_passport_photo(face_data, "photo.jpg")

        assert result["checks"]["face_centered"]["passed"] is False
        assert result["passed"] is False

    @patch("cv2.imread")
    def test_eyes_too_high_fails(self, mock_imread, valid_face_data):
        """Average eye Y above 55% (too high in the frame) → eyes_level check fails."""
        mock_imread.return_value = _make_image_array(800, 1000)
        face_data = copy.deepcopy(valid_face_data)
        # avg_eye_y = 0.20 < 0.55 minimum
        face_data["key_landmarks"]["left_eye"] = (0.42, 0.20, 0.0)
        face_data["key_landmarks"]["right_eye"] = (0.58, 0.20, 0.0)

        from app.services.validation import validate_passport_photo

        result = validate_passport_photo(face_data, "photo.jpg")

        assert result["checks"]["eyes_level"]["passed"] is False
        assert result["passed"] is False

    @patch("cv2.imread")
    def test_eyes_too_low_fails(self, mock_imread, valid_face_data):
        """Average eye Y below 70% (too low in the frame) → eyes_level check fails."""
        mock_imread.return_value = _make_image_array(800, 1000)
        face_data = copy.deepcopy(valid_face_data)
        # avg_eye_y = 0.80 > 0.70 maximum
        face_data["key_landmarks"]["left_eye"] = (0.42, 0.80, 0.0)
        face_data["key_landmarks"]["right_eye"] = (0.58, 0.80, 0.0)

        from app.services.validation import validate_passport_photo

        result = validate_passport_photo(face_data, "photo.jpg")

        assert result["checks"]["eyes_level"]["passed"] is False
        assert result["passed"] is False

    @patch("cv2.imread")
    def test_face_turned_sideways_fails(self, mock_imread, valid_face_data):
        """High asymmetry ratio (face turned) → face_forward check fails."""
        mock_imread.return_value = _make_image_array(800, 1000)
        face_data = copy.deepcopy(valid_face_data)
        # Nose near the right edge → asymmetry > 0.15 threshold
        # nose_x=0.58, left_eye_x=0.40, right_eye_x=0.60
        # left_dist=|0.58-0.40|=0.18, right_dist=|0.58-0.60|=0.02
        # asymmetry = |0.18-0.02| / 0.18 = 0.89
        face_data["key_landmarks"]["nose"] = (0.58, 0.52, 0.0)
        face_data["key_landmarks"]["left_eye"] = (0.40, 0.40, 0.0)
        face_data["key_landmarks"]["right_eye"] = (0.60, 0.40, 0.0)

        from app.services.validation import validate_passport_photo

        result = validate_passport_photo(face_data, "photo.jpg")

        assert result["checks"]["face_forward"]["passed"] is False
        assert result["passed"] is False

    @patch("cv2.imread")
    def test_multiple_checks_can_fail_independently(self, mock_imread, valid_face_data):
        """Two independent check failures are both reported."""
        mock_imread.return_value = _make_image_array(400, 400)  # too small
        face_data = copy.deepcopy(valid_face_data)
        face_data["face_center"]["x"] = 0.85  # not centered

        from app.services.validation import validate_passport_photo

        result = validate_passport_photo(face_data, "photo.jpg")

        assert result["checks"]["resolution"]["passed"] is False
        assert result["checks"]["face_centered"]["passed"] is False
        assert result["passed"] is False

    @patch("cv2.imread")
    def test_valid_photo_passes_all_checks(self, mock_imread, valid_face_data):
        """A well-formed face_data with adequate resolution passes every check."""
        mock_imread.return_value = _make_image_array(800, 1000)

        from app.services.validation import validate_passport_photo

        result = validate_passport_photo(valid_face_data, "photo.jpg")

        assert result["passed"] is True
        for check_name, check in result["checks"].items():
            assert check["passed"] is True, f"Expected {check_name} to pass"
