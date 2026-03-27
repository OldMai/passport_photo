"""
Demo script: Upload a headshot image, process it into a passport photo,
download the results, and print validation details.
"""

import requests
import json
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"
OUTPUT_DIR = Path("demo_output")
OUTPUT_DIR.mkdir(exist_ok=True)


def run_demo(image_path: str):
    print(f"\n{'='*60}")
    print(f"  Passport Photo Demo")
    print(f"  Input: {image_path}")
    print(f"{'='*60}\n")

    # Step 1: Upload
    print("[Step 1] Uploading image...")
    with open(image_path, "rb") as f:
        files = {"file": (Path(image_path).name, f, "image/jpeg")}
        resp = requests.post(f"{BASE_URL}/api/upload", files=files)

    if resp.status_code != 200:
        print(f"  FAILED: {resp.status_code} - {resp.text}")
        return
    upload_data = resp.json()
    upload_id = upload_data["upload_id"]
    print(f"  OK - Upload ID: {upload_id}")

    # Step 2: Process
    print("\n[Step 2] Processing image (face detection, background removal, crop, print layout)...")
    resp = requests.post(f"{BASE_URL}/api/process", json={"upload_id": upload_id})

    if resp.status_code != 200:
        print(f"  FAILED: {resp.status_code} - {resp.text}")
        return
    process_data = resp.json()
    job_id = process_data["job_id"]
    print(f"  OK - Job ID: {job_id}")
    print(f"  Status: {process_data['status']}")

    # Step 3: Validation results
    print("\n[Step 3] Validation Results:")
    val = process_data["validation"]
    overall = "PASSED" if val["passed"] else "FAILED"
    print(f"  Overall: {overall}")
    for name, check in val["checks"].items():
        status = "PASS" if check["passed"] else "FAIL"
        print(f"    [{status}] {name}: {check['message']}")

    # Step 4: Download single passport photo
    print("\n[Step 4] Downloading passport photo...")
    resp = requests.get(f"{BASE_URL}{process_data['processed_url']}")
    if resp.status_code == 200:
        single_path = OUTPUT_DIR / "passport_photo.jpg"
        single_path.write_bytes(resp.content)
        print(f"  Saved: {single_path} ({len(resp.content) / 1024:.1f} KB)")
    else:
        print(f"  FAILED: {resp.status_code}")

    # Step 5: Download print layout
    print("\n[Step 5] Downloading print layout (4x6 with 6 photos)...")
    resp = requests.get(f"{BASE_URL}{process_data['print_layout_url']}")
    if resp.status_code == 200:
        layout_path = OUTPUT_DIR / "print_layout.jpg"
        layout_path.write_bytes(resp.content)
        print(f"  Saved: {layout_path} ({len(resp.content) / 1024:.1f} KB)")
    else:
        print(f"  FAILED: {resp.status_code}")

    # Summary
    print(f"\n{'='*60}")
    print(f"  Demo Complete!")
    print(f"  Output files in: {OUTPUT_DIR.resolve()}")
    print(f"    - passport_photo.jpg  (2x2 inch at 600 DPI = 1200x1200 px)")
    print(f"    - print_layout.jpg    (4x6 inch at 300 DPI = 1200x1800 px)")
    print(f"{'='*60}\n")

    return process_data


if __name__ == "__main__":
    image = sys.argv[1] if len(sys.argv) > 1 else "sample_photos/headshot.jpg"
    if not Path(image).exists():
        print(f"Error: Image not found at {image}")
        sys.exit(1)
    run_demo(image)
