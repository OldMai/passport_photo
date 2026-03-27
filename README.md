# US Passport Photo Processor

A web application that automatically converts your headshot photos into US passport-compliant photos with background removal, validation, and print-ready layouts.

## Features

- **Automatic Face Detection**: Uses Google MediaPipe for precise face landmark detection
- **Background Removal**: Replaces any background with pure white using deep learning (rembg/U2-Net)
- **Validation**: Checks against all US passport photo requirements
- **Smart Cropping**: Automatically crops and positions face to meet 2"×2" passport specifications
- **Print Layouts**: Generates 4"×6" layouts with six 2"×2" photos ready for printing
- **Modern Web UI**: Clean, responsive interface with drag-and-drop upload

## US Passport Photo Requirements

The application processes photos to meet these official requirements:

- **Size**: 2"×2" (51mm × 51mm)
- **Resolution**: Minimum 600×600 pixels (this app generates 1200×1200 at 600 DPI)
- **Background**: Plain white (#FFFFFF)
- **Head Size**: 1"–1⅜" from chin to crown (50-68.75% of image height)
- **Face Position**: Centered, looking directly at camera
- **Eyes**: Positioned at approximately 60% from bottom
- **Recent**: Photo taken within last 6 months
- **Expression**: Neutral, eyes open, mouth closed

## Technology Stack

### Backend (Python)
- **FastAPI**: Modern async web framework
- **MediaPipe**: Face detection and landmark extraction
- **rembg**: AI-powered background removal
- **Pillow**: Image processing and manipulation
- **OpenCV**: Computer vision utilities

### Frontend (React + TypeScript)
- **React 18**: UI component library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool
- **Tailwind CSS**: Utility-first styling
- **Axios**: HTTP client

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 20+
- npm or yarn

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python -m uvicorn app.main:app --reload
```

The backend will run on http://localhost:8000

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will run on http://localhost:5173

## Usage

1. **Open the application** in your browser at http://localhost:5173
2. **Upload a photo** by:
   - Dragging and dropping it onto the upload area, or
   - Clicking "Select File" to browse
3. **Wait for processing** (5-10 seconds):
   - Face detection
   - Background removal
   - Validation checks
   - Photo cropping
   - Print layout generation
4. **View results**:
   - Validation results showing all requirement checks
   - Side-by-side comparison of original and processed photos
   - Print layout preview (4"×6" with six photos)
5. **Download**:
   - Single passport photo (1200×1200px, 2"×2" at 600 DPI)
   - Print layout (1200×1800px, 4"×6" at 300 DPI)

## Project Structure

```
passport_photo/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application and routes
│   │   ├── config.py               # Configuration settings
│   │   └── services/
│   │       ├── face_detection.py   # MediaPipe face detection
│   │       ├── background_removal.py  # Background removal with rembg
│   │       ├── validation.py       # Passport requirements validation
│   │       ├── image_processing.py # Cropping and resizing
│   │       └── print_layout.py     # Print layout generation
│   ├── storage/                    # Temporary file storage
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx                 # Main application component
│   │   ├── components/             # React components
│   │   ├── services/               # API client
│   │   └── types/                  # TypeScript types
│   ├── package.json
│   └── vite.config.ts
├── sample_photos/                  # Test photos
│   ├── jing_photo.jpg
│   └── yue_photo.jpg
└── README.md
```

## API Endpoints

### POST /api/upload
Upload an image file.
- **Input**: multipart/form-data with image file
- **Output**: `{ upload_id, filename, preview_url }`

### POST /api/process
Process uploaded image into passport photo.
- **Input**: `{ upload_id }`
- **Output**: `{ job_id, status, processed_url, print_layout_url, validation }`

### GET /api/download/{job_id}/single
Download single 2"×2" passport photo.

### GET /api/download/{job_id}/print_layout
Download 4"×6" print layout with six photos.

### GET /api/health
Health check endpoint.

## Configuration

### Backend (.env)
Copy `.env.example` to `.env` and adjust if needed:

```env
HOST=0.0.0.0
PORT=8000
DPI=600
PASSPORT_SIZE_INCHES=2
MAX_FILE_SIZE_MB=10
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend (vite.config.ts)
API proxy is pre-configured to forward `/api` requests to `http://localhost:8000`.

## Testing

### Test with Sample Photos

The project includes two sample photos in `sample_photos/`:
- `jing_photo.jpg`
- `yue_photo.jpg`

These are high-quality portrait photos perfect for testing the application.

### Backend Testing

```bash
cd backend
python ../test_backend.py
```

This will test both sample photos through the API and display validation results.

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

### Frontend Development
```bash
cd frontend
npm run dev
```

Hot module replacement (HMR) is enabled for instant updates during development.

## Troubleshooting

### Backend Issues

**ModuleNotFoundError**: Make sure you activated the virtual environment and installed all dependencies.

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Port 8000 already in use**: Change the port in `.env` or kill the process using port 8000.

### Frontend Issues

**CORS errors**: Ensure the backend is running and `ALLOWED_ORIGINS` in backend `.env` includes the frontend URL.

**Build errors**: Try deleting `node_modules` and reinstalling:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Limitations

- Maximum file size: 10MB
- Supported formats: JPEG, PNG
- Requires clear frontal face photo
- Single person per photo
- Processing time: 5-10 seconds per photo

## Future Enhancements

- Batch processing multiple photos
- Additional export formats (PDF, different sizes)
- Real-time camera capture
- Mobile app version
- Cloud deployment with AWS/GCP
- Docker containerization
- Additional passport photo standards (EU, Canada, etc.)

## License

This project is for educational purposes. Please ensure you have the right to process and modify any photos you upload.

## Acknowledgments

- [MediaPipe](https://mediapipe.dev/) for face detection
- [rembg](https://github.com/danielgatis/rembg) for background removal
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [React](https://react.dev/) and [Vite](https://vitejs.dev/) for the frontend
- [US Department of State](https://travel.state.gov/content/travel/en/passports/how-apply/photos.html) for passport photo specifications

## Contact

For questions or issues, please create an issue in the repository.
