"""Quick test script for the passport photo backend."""

import requests
import json
from pathlib import Path

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_upload_and_process(image_path: str):
    """Test uploading and processing an image."""
    print(f"\n=== Testing with {image_path} ===\n")

    # 1. Upload image
    print("1. Uploading image...")
    with open(image_path, "rb") as f:
        files = {"file": (Path(image_path).name, f, "image/jpeg")}
        response = requests.post(f"{BASE_URL}/api/upload", files=files)

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
        f"{BASE_URL}/api/process",
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
    print(f"  Single photo: {BASE_URL}{process_data['processed_url']}")
    print(f"  Print layout: {BASE_URL}{process_data['print_layout_url']}")

    return process_data

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        for img in sys.argv[1:]:
            test_upload_and_process(img)
    else:
        test_upload_and_process("sample_photos/headshot.jpg")
