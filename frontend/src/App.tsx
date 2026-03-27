/**
 * Main App component for the Passport Photo Processor
 */

import { useState } from 'react';
import ImageUpload from './components/ImageUpload';
import ProcessingStatus from './components/ProcessingStatus';
import ValidationResults from './components/ValidationResults';
import ImagePreview from './components/ImagePreview';
import DownloadButton from './components/DownloadButton';
import { uploadImage, processImage } from './services/api';
import type { ProcessingStatus as Status, UploadResponse, ProcessResponse } from './types';

function App() {
  const [status, setStatus] = useState<Status>('idle');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadResponse, setUploadResponse] = useState<UploadResponse | null>(null);
  const [processResponse, setProcessResponse] = useState<ProcessResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = async (file: File) => {
    setUploadedFile(file);
    setError(null);
    setStatus('uploading');

    try {
      // Upload the file
      const uploadData = await uploadImage(file);
      setUploadResponse(uploadData);

      // Process the image
      setStatus('processing');
      const processData = await processImage(uploadData.upload_id);
      setProcessResponse(processData);

      setStatus('completed');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setStatus('error');
    }
  };

  const handleReset = () => {
    setStatus('idle');
    setUploadedFile(null);
    setUploadResponse(null);
    setProcessResponse(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            US Passport Photo Processor
          </h1>
          <p className="text-gray-600">
            Automatically convert your photo into a compliant US passport photo
          </p>
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {status === 'idle' && (
            <ImageUpload onFileSelect={handleFileSelect} />
          )}

          {(status === 'uploading' || status === 'processing') && (
            <ProcessingStatus status={status} />
          )}

          {status === 'error' && (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Processing Failed</h3>
              <p className="text-gray-600 mb-4">{error}</p>
              <button
                onClick={handleReset}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                Try Again
              </button>
            </div>
          )}

          {status === 'completed' && processResponse && uploadedFile && (
            <div className="space-y-6">
              {/* Validation Results */}
              <ValidationResults validation={processResponse.validation} />

              {/* Image Preview */}
              <ImagePreview
                originalFile={uploadedFile}
                processedUrl={processResponse.processed_url}
                printLayoutUrl={processResponse.print_layout_url}
              />

              {/* Download Buttons */}
              <DownloadButton
                singlePhotoUrl={processResponse.processed_url}
                printLayoutUrl={processResponse.print_layout_url}
                jobId={processResponse.job_id}
              />

              {/* Reset Button */}
              <div className="text-center pt-4 border-t border-gray-200">
                <button
                  onClick={handleReset}
                  className="px-6 py-2 text-gray-600 hover:text-gray-900 font-medium transition-colors"
                >
                  Process Another Photo
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-sm text-gray-600">
          <p>
            Photos are processed according to{' '}
            <a
              href="https://travel.state.gov/content/travel/en/passports/how-apply/photos.html"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 underline"
            >
              US Department of State requirements
            </a>
          </p>
          <p className="mt-2">
            Requirements: 2"×2" size, white background, recent photo with neutral expression
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
