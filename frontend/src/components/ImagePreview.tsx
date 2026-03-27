/**
 * ImagePreview component - Side-by-side before/after comparison
 */

import { useState } from 'react';

interface ImagePreviewProps {
  originalFile: File;
  processedUrl: string;
  printLayoutUrl: string;
}

export default function ImagePreview({ originalFile, processedUrl, printLayoutUrl }: ImagePreviewProps) {
  const [viewMode, setViewMode] = useState<'single' | 'print'>('single');
  const [originalPreview, setOriginalPreview] = useState<string>('');

  // Create preview URL for original file
  if (!originalPreview && originalFile) {
    const reader = new FileReader();
    reader.onloadend = () => {
      setOriginalPreview(reader.result as string);
    };
    reader.readAsDataURL(originalFile);
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Results</h3>
        <div className="flex gap-2 bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setViewMode('single')}
            className={`px-4 py-1 rounded-md text-sm font-medium transition-colors ${
              viewMode === 'single'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Single Photo
          </button>
          <button
            onClick={() => setViewMode('print')}
            className={`px-4 py-1 rounded-md text-sm font-medium transition-colors ${
              viewMode === 'print'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Print Layout
          </button>
        </div>
      </div>

      {viewMode === 'single' ? (
        <div className="grid grid-cols-2 gap-4">
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Original Photo</h4>
            <div className="border border-gray-200 rounded-lg overflow-hidden bg-gray-50">
              {originalPreview && (
                <img
                  src={originalPreview}
                  alt="Original"
                  className="w-full h-auto"
                />
              )}
            </div>
          </div>

          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Passport Photo (2"×2")</h4>
            <div className="border border-gray-200 rounded-lg overflow-hidden bg-white">
              <img
                src={processedUrl}
                alt="Passport Photo"
                className="w-full h-auto"
              />
            </div>
            <p className="text-xs text-gray-500 mt-2">
              1200×1200px at 600 DPI
            </p>
          </div>
        </div>
      ) : (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Print Layout (4"×6")</h4>
          <div className="border border-gray-200 rounded-lg overflow-hidden bg-white max-w-2xl mx-auto">
            <img
              src={printLayoutUrl}
              alt="Print Layout"
              className="w-full h-auto"
            />
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            1200×1800px at 300 DPI - Six 2"×2" photos ready for printing
          </p>
        </div>
      )}
    </div>
  );
}
