"""Failure-case tests for the face_detection service.

mediapipe is not installed in the test environment, so we inject a full
stub into sys.modules before importing the service under test.
"""

import sys
import importlib
import types
from unittest.mock import MagicMock, patch
import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Build a minimal mediapipe stub that satisfies all top-level imports
# ---------------------------------------------------------------------------

def _build_mediapipe_stub():
    """Create a fake `mediapipe` package tree with the attributes the service uses."""
    mp_stub = types.ModuleType("mediapipe")

    # mediapipe.solutions namespace
    solutions = types.ModuleType("mediapipe.solutions")
    mp_stub.solutions = solutions

    # mediapipe.solutions.face_detection
    fd_mod = types.ModuleType("mediapipe.solutions.face_detection")
    fd_mod.FaceDetection = MagicMock()
    solutions.face_detection = fd_mod

    # mediapipe.solutions.face_mesh
    fm_mod = types.ModuleType("mediapipe.solutions.face_mesh")
    fm_mod.FaceMesh = MagicMock()
    solutions.face_mesh = fm_mod

    sys.modules["mediapipe"] = mp_stub
    sys.modules["mediapipe.solutions"] = solutions
    sys.modules["mediapipe.solutions.face_detection"] = fd_mod
    sys.modules["mediapipe.solutions.face_mesh"] = fm_mod

    return mp_stub


# Install the stub once, before any imports of the service module
_mp_stub = _build_mediapipe_stub()

# Force-reload the service so it picks up the stub (in case it was imported
# earlier in this process without the stub present)
if "app.services.face_detection" in sys.modules:
    del sys.modules["app.services.face_detection"]

from app.services.face_detection import detect_face  # noqa: E402


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------

def _make_detection_results(count: int):
    """Mock FaceDetection results with `count` detections."""
    results = MagicMock()
    if count == 0:
        results.detections = None
    else:
        results.detections = [MagicMock() for _ in range(count)]
        bbox = MagicMock()
        bbox.xmin = 0.2
        bbox.ymin = 0.1
        bbox.width = 0.4
        bbox.height = 0.6
        results.detections[0].location_data.relative_bounding_box = bbox
    return results


def _make_mesh_results(has_landmarks: bool):
    """Mock FaceMesh results."""
    results = MagicMock()
    if not has_landmarks:
        results.multi_face_landmarks = None
        return results

    lm_list = []
    for _ in range(468):
        lm = MagicMock()
        lm.x = 0.5
        lm.y = 0.5
        lm.z = 0.0
        lm_list.append(lm)

    overrides = {
        10: (0.50, 0.10),
        152: (0.50, 0.70),
        33: (0.42, 0.62),
        263: (0.58, 0.62),
        1: (0.50, 0.66),
        234: (0.25, 0.62),
        454: (0.75, 0.62),
    }
    for idx, (x, y) in overrides.items():
        lm_list[idx].x = x
        lm_list[idx].y = y

    face_landmarks = MagicMock()
    face_landmarks.landmark = lm_list
    results.multi_face_landmarks = [face_landmarks]
    return results


def _ctx(process_result):
    """Wrap a result in a context-manager mock."""
    inner = MagicMock()
    inner.process = MagicMock(return_value=process_result)
    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=inner)
    ctx.__exit__ = MagicMock(return_value=False)
    return ctx


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestDetectFaceFailureCases:

    @patch("cv2.imread", return_value=None)
    def test_image_not_found_raises(self, _mock_imread):
        """cv2.imread returning None → ValueError: Failed to load image."""
        with pytest.raises(ValueError, match="Failed to load image"):
            detect_face("/nonexistent/path/photo.jpg")

    @patch("cv2.cvtColor")
    @patch("cv2.imread")
    def test_no_face_detected_raises(self, mock_imread, mock_cvtcolor):
        """Zero detections → ValueError: No face detected."""
        img = np.zeros((100, 100, 3), dtype="uint8")
        mock_imread.return_value = img
        mock_cvtcolor.return_value = img

        _mp_stub.solutions.face_detection.FaceDetection.return_value = _ctx(
            _make_detection_results(0)
        )

        with pytest.raises(ValueError, match="No face detected"):
            detect_face("any.jpg")

    @patch("cv2.cvtColor")
    @patch("cv2.imread")
    def test_multiple_faces_raises(self, mock_imread, mock_cvtcolor):
        """Two detections → ValueError: Multiple faces detected."""
        img = np.zeros((100, 100, 3), dtype="uint8")
        mock_imread.return_value = img
        mock_cvtcolor.return_value = img

        _mp_stub.solutions.face_detection.FaceDetection.return_value = _ctx(
            _make_detection_results(2)
        )

        with pytest.raises(ValueError, match="Multiple faces detected"):
            detect_face("any.jpg")

    @patch("cv2.cvtColor")
    @patch("cv2.imread")
    def test_face_mesh_no_landmarks_raises(self, mock_imread, mock_cvtcolor):
        """FaceMesh returns no landmarks → ValueError: Failed to extract face landmarks."""
        img = np.zeros((100, 100, 3), dtype="uint8")
        mock_imread.return_value = img
        mock_cvtcolor.return_value = img

        _mp_stub.solutions.face_detection.FaceDetection.return_value = _ctx(
            _make_detection_results(1)
        )
        _mp_stub.solutions.face_mesh.FaceMesh.return_value = _ctx(
            _make_mesh_results(False)
        )

        with pytest.raises(ValueError, match="Failed to extract face landmarks"):
            detect_face("any.jpg")

    @patch("cv2.cvtColor")
    @patch("cv2.imread")
    def test_successful_detection_returns_expected_keys(self, mock_imread, mock_cvtcolor):
        """Happy-path: detect_face returns all expected dict keys."""
        img = np.zeros((200, 200, 3), dtype="uint8")
        mock_imread.return_value = img
        mock_cvtcolor.return_value = img

        _mp_stub.solutions.face_detection.FaceDetection.return_value = _ctx(
            _make_detection_results(1)
        )
        _mp_stub.solutions.face_mesh.FaceMesh.return_value = _ctx(
            _make_mesh_results(True)
        )

        result = detect_face("photo.jpg")

        expected_keys = {
            "bbox", "landmarks", "key_landmarks",
            "face_center", "head_height_normalized", "image_shape",
        }
        assert expected_keys == set(result.keys())
        assert set(result["key_landmarks"].keys()) == {
            "crown", "chin", "left_eye", "right_eye", "nose", "left_ear", "right_ear"
        }
