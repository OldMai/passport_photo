"""Main FastAPI application for passport photo processing."""

import uuid
import shutil
from pathlib import Path
from typing import Dict, Any
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from app import config
from app.services import face_detection, background_removal, validation, image_processing, print_layout

# Initialize FastAPI app
app = FastAPI(
    title="Passport Photo Processor",
    description="API for processing photos into US passport-compliant images",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ProcessRequest(BaseModel):
    upload_id: str

class UploadResponse(BaseModel):
    upload_id: str
    filename: str
    preview_url: str

class ProcessResponse(BaseModel):
    job_id: str
    status: str
    processed_url: str
    print_layout_url: str
    validation: Dict[str, Any]


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "passport-photo-processor"}


# Upload endpoint
@app.post("/api/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image file for processing.

    Args:
        file: Image file (JPEG or PNG)

    Returns:
        Upload ID, filename, and preview URL
    """
    # Validate file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in config.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(config.ALLOWED_EXTENSIONS)}"
        )

    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > config.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {config.MAX_FILE_SIZE_MB}MB"
        )

    # Generate unique ID
    upload_id = str(uuid.uuid4())
    file_path = config.UPLOAD_DIR / f"{upload_id}.{file_ext}"

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    return UploadResponse(
        upload_id=upload_id,
        filename=file.filename,
        preview_url=f"/api/preview/{upload_id}"
    )


# Preview endpoint
@app.get("/api/preview/{upload_id}")
async def get_preview(upload_id: str):
    """Get preview of uploaded image."""
    # Find file with any extension
    for ext in config.ALLOWED_EXTENSIONS:
        file_path = config.UPLOAD_DIR / f"{upload_id}.{ext}"
        if file_path.exists():
            return FileResponse(file_path)

    raise HTTPException(status_code=404, detail="Image not found")


# Process endpoint
@app.post("/api/process", response_model=ProcessResponse)
async def process_image(request: ProcessRequest):
    """
    Process uploaded image into passport photo.

    Args:
        request: Process request with upload_id

    Returns:
        Processing results with job_id, status, URLs, and validation results
    """
    upload_id = request.upload_id

    # Find uploaded file
    upload_path = None
    for ext in config.ALLOWED_EXTENSIONS:
        potential_path = config.UPLOAD_DIR / f"{upload_id}.{ext}"
        if potential_path.exists():
            upload_path = potential_path
            break

    if not upload_path:
        raise HTTPException(status_code=404, detail="Uploaded image not found")

    try:
        # Generate job ID
        job_id = str(uuid.uuid4())

        # Step 1: Face detection
        face_data = face_detection.detect_face(str(upload_path))

        # Step 2: Background removal
        bg_removed_path = config.PROCESSED_DIR / f"{job_id}_bg_removed.jpg"
        background_removal.remove_background(str(upload_path), str(bg_removed_path))

        # Step 3: Validation
        validation_results = validation.validate_passport_photo(face_data, str(bg_removed_path))

        # Step 4: Crop and resize to passport size
        passport_path = config.PROCESSED_DIR / f"{job_id}_passport.jpg"
        image_processing.crop_to_passport_size(
            str(bg_removed_path),
            face_data,
            str(passport_path)
        )

        # Step 5: Generate print layout
        print_layout_path = config.PRINT_LAYOUTS_DIR / f"{job_id}_print_layout.jpg"
        print_layout.generate_print_layout(str(passport_path), str(print_layout_path))

        # Return response
        return ProcessResponse(
            job_id=job_id,
            status="completed",
            processed_url=f"/api/download/{job_id}/single",
            print_layout_url=f"/api/download/{job_id}/print_layout",
            validation=validation_results
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


# Download endpoints
@app.get("/api/download/{job_id}/single")
async def download_single(job_id: str):
    """Download single passport photo."""
    file_path = config.PROCESSED_DIR / f"{job_id}_passport.jpg"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Processed image not found")

    return FileResponse(
        file_path,
        media_type="image/jpeg",
        filename=f"passport_photo_{job_id}.jpg"
    )


@app.get("/api/download/{job_id}/print_layout")
async def download_print_layout(job_id: str):
    """Download print layout (4x6 with six 2x2 photos)."""
    file_path = config.PRINT_LAYOUTS_DIR / f"{job_id}_print_layout.jpg"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Print layout not found")

    return FileResponse(
        file_path,
        media_type="image/jpeg",
        filename=f"passport_photo_print_layout_{job_id}.jpg"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)
