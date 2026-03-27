"""Quick test script for the passport photo backend."""

import argparse
import sys
from pathlib import Path

import requests

# Base URL for the API
BASE_URL = "http://localhost:8000"
REPO_ROOT = Path(__file__).resolve().parent

def test_upload_and_process(image_path: str, base_url: str = BASE_URL):
    """Test uploading and processing an image."""
    base = base_url.rstrip("/")
    print(f"\n=== Testing with {image_path} ===\n")

    # 1. Upload image
    print("1. Uploading image...")
    with open(image_path, "rb") as f:
        files = {"file": (Path(image_path).name, f, "image/jpeg")}
        response = requests.post(f"{base}/api/upload", files=files)

    if response.status_code != 200:
        print(f"Upload failed: {response.text}")
        return

    upload_data = response.json()
    print(f"✓ Upload successful!")
    print(f"  Upload ID: {upload_data['upload_id']}")
    print(f"  Filename: {upload_data['filename']}")

    # 2. Process image
    print("\n2. Processing image...")
    process_response = requests.post(
        f"{base}/api/process",
        json={"upload_id": upload_data['upload_id']}
    )

    if process_response.status_code != 200:
        print(f"Processing failed: {process_response.text}")
        return

    process_data = process_response.json()
    print(f"✓ Processing successful!")
    print(f"  Job ID: {process_data['job_id']}")
    print(f"  Status: {process_data['status']}")

    # 3. Print validation results
    print("\n3. Validation Results:")
    validation = process_data['validation']
    print(f"  Overall: {'✓ PASSED' if validation['passed'] else '✗ FAILED'}")
    print("\n  Individual checks:")
    for check_name, check_data in validation['checks'].items():
        status = "✓" if check_data['passed'] else "✗"
        print(f"    {status} {check_name}: {check_data['message']}")

    # 4. Download URLs
    print("\n4. Download URLs:")
    print(f"  Single photo: {base}{process_data['processed_url']}")
    print(f"  Print layout: {base}{process_data['print_layout_url']}")

    return process_data


def _default_image_paths():
    """Prefer explicit sample files; always include demo_headshot if present."""
    candidates = [
        REPO_ROOT / "sample_photos" / "demo_headshot.jpg",
        REPO_ROOT / "sample_photos" / "jing_photo.jpg",
        REPO_ROOT / "sample_photos" / "yue_photo.jpg",
    ]
    return [p for p in candidates if p.is_file()]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload and process images via the passport photo API.")
    parser.add_argument(
        "images",
        nargs="*",
        type=Path,
        help="Image paths (JPEG/PNG). Defaults to sample_photos in the repo when omitted.",
    )
    parser.add_argument(
        "--base-url",
        default=BASE_URL,
        help=f"API base URL (default: {BASE_URL})",
    )
    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    paths = [p.resolve() for p in args.images] if args.images else _default_image_paths()
    if not paths:
        print("No images found. Add files under sample_photos/ or pass paths on the command line.", file=sys.stderr)
        sys.exit(1)

    for p in paths:
        if not p.is_file():
            print(f"Not a file: {p}", file=sys.stderr)
            sys.exit(1)
        test_upload_and_process(str(p), base_url=base)
