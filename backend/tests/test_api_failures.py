"""Failure-case tests for the FastAPI endpoints in main.py."""

import io
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from app.main import app
    return TestClient(app)


# ---------------------------------------------------------------------------
# /api/upload – failure cases
# ---------------------------------------------------------------------------

class TestUploadEndpointFailures:

    def test_upload_no_file_returns_422(self, client):
        """POST /api/upload with no file body → 422 Unprocessable Entity."""
        response = client.post("/api/upload")
        assert response.status_code == 422

    def test_upload_disallowed_extension_returns_400(self, client):
        """Uploading a .gif file → 400 with 'Invalid file type' detail."""
        data = io.BytesIO(b"GIF89a fake gif content")
        response = client.post(
            "/api/upload",
            files={"file": ("photo.gif", data, "image/gif")},
        )
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

    def test_upload_file_too_large_returns_400(self, client):
        """File exceeding MAX_FILE_SIZE_BYTES → 400 with size error."""
        from app import config
        # Create a payload slightly over the limit
        oversized = io.BytesIO(b"x" * (config.MAX_FILE_SIZE_BYTES + 1))
        response = client.post(
            "/api/upload",
            files={"file": ("big.jpg", oversized, "image/jpeg")},
        )
        assert response.status_code == 400
        assert "too large" in response.json()["detail"].lower()

    def test_upload_empty_filename_is_rejected(self, client):
        """Empty filename is rejected (FastAPI returns 422 from form validation,
        our handler would return 400 — either way the request is not accepted)."""
        data = io.BytesIO(b"fake jpeg bytes")
        response = client.post(
            "/api/upload",
            files={"file": ("", data, "image/jpeg")},
        )
        assert response.status_code in (400, 422)


# ---------------------------------------------------------------------------
# /api/process – failure cases
# ---------------------------------------------------------------------------

class TestProcessEndpointFailures:

    def test_process_unknown_upload_id_returns_404(self, client):
        """Processing a non-existent upload_id → 404."""
        response = client.post(
            "/api/process",
            json={"upload_id": "00000000-0000-0000-0000-000000000000"},
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_process_no_face_detected_returns_400(self, client, tmp_path):
        """face_detection.detect_face raising ValueError → 400."""
        # Upload a valid-sized JPEG first so the file exists on disk
        tiny_jpeg = (
            b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
            b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t"
            b"\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a"
            b"\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\x1e"
            b"\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00"
            b"\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00"
            b"\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b"
            b"\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04"
            b"\xff\xd9"
        )
        upload_resp = client.post(
            "/api/upload",
            files={"file": ("face.jpg", io.BytesIO(tiny_jpeg), "image/jpeg")},
        )
        assert upload_resp.status_code == 200
        upload_id = upload_resp.json()["upload_id"]

        with patch(
            "app.services.face_detection.detect_face",
            side_effect=ValueError("No face detected in the image"),
        ):
            resp = client.post("/api/process", json={"upload_id": upload_id})

        assert resp.status_code == 400
        assert "No face detected" in resp.json()["detail"]

    def test_process_multiple_faces_returns_400(self, client):
        """Multiple faces raises ValueError → 400."""
        tiny_jpeg = b"\xff\xd8\xff\xd9"  # minimal JPEG marker pair

        upload_resp = client.post(
            "/api/upload",
            files={"file": ("group.jpg", io.BytesIO(tiny_jpeg), "image/jpeg")},
        )
        assert upload_resp.status_code == 200
        upload_id = upload_resp.json()["upload_id"]

        with patch(
            "app.services.face_detection.detect_face",
            side_effect=ValueError("Multiple faces detected. Please use an image with only one person"),
        ):
            resp = client.post("/api/process", json={"upload_id": upload_id})

        assert resp.status_code == 400
        assert "Multiple faces" in resp.json()["detail"]

    def test_process_face_mesh_failure_returns_400(self, client):
        """FaceMesh failure raises ValueError → 400."""
        tiny_jpeg = b"\xff\xd8\xff\xd9"

        upload_resp = client.post(
            "/api/upload",
            files={"file": ("blurry.jpg", io.BytesIO(tiny_jpeg), "image/jpeg")},
        )
        assert upload_resp.status_code == 200
        upload_id = upload_resp.json()["upload_id"]

        with patch(
            "app.services.face_detection.detect_face",
            side_effect=ValueError("Failed to extract face landmarks"),
        ):
            resp = client.post("/api/process", json={"upload_id": upload_id})

        assert resp.status_code == 400
        assert "landmarks" in resp.json()["detail"].lower()

    def test_process_unexpected_error_returns_500(self, client):
        """An unexpected exception in the pipeline → 500."""
        tiny_jpeg = b"\xff\xd8\xff\xd9"

        upload_resp = client.post(
            "/api/upload",
            files={"file": ("crash.jpg", io.BytesIO(tiny_jpeg), "image/jpeg")},
        )
        assert upload_resp.status_code == 200
        upload_id = upload_resp.json()["upload_id"]

        with patch(
            "app.services.face_detection.detect_face",
            side_effect=RuntimeError("unexpected GPU error"),
        ):
            resp = client.post("/api/process", json={"upload_id": upload_id})

        assert resp.status_code == 500
        assert "Processing failed" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# /api/download – failure cases
# ---------------------------------------------------------------------------

class TestDownloadEndpointFailures:

    def test_download_single_unknown_job_returns_404(self, client):
        """Downloading single photo with unknown job_id → 404."""
        resp = client.get("/api/download/nonexistent-job-id/single")
        assert resp.status_code == 404

    def test_download_print_layout_unknown_job_returns_404(self, client):
        """Downloading print layout with unknown job_id → 404."""
        resp = client.get("/api/download/nonexistent-job-id/print_layout")
        assert resp.status_code == 404

    def test_preview_unknown_upload_returns_404(self, client):
        """Fetching preview for non-existent upload → 404."""
        resp = client.get("/api/preview/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404
