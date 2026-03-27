/**
 * ImageUpload component - Drag-and-drop file upload interface
 */

import { useCallback, useState } from 'react';

interface ImageUploadProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
}

export default function ImageUpload({ onFileSelect, disabled }: ImageUploadProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    if (disabled) return;

    const files = Array.from(e.dataTransfer.files);
    const imageFile = files.find(file => file.type.startsWith('image/'));

    if (imageFile) {
      onFileSelect(imageFile);
    }
  }, [onFileSelect, disabled]);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (!disabled) {
      setIsDragging(true);
    }
  }, [disabled]);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onFileSelect(files[0]);
    }
  }, [onFileSelect]);

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
        isDragging
          ? 'border-blue-500 bg-blue-50'
          : disabled
          ? 'border-gray-300 bg-gray-50 cursor-not-allowed'
          : 'border-gray-400 bg-white hover:border-blue-400 hover:bg-blue-50 cursor-pointer'
      }`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      <div className="flex flex-col items-center gap-4">
        <svg
          className={`w-16 h-16 ${disabled ? 'text-gray-400' : 'text-gray-500'}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>

        <div>
          <p className={`text-lg font-medium ${disabled ? 'text-gray-500' : 'text-gray-700'}`}>
            {disabled ? 'Processing...' : 'Drop your photo here'}
          </p>
          <p className={`text-sm ${disabled ? 'text-gray-400' : 'text-gray-500'}`}>
            or click to browse
          </p>
        </div>

        <input
          type="file"
          accept="image/jpeg,image/png"
          onChange={handleFileInput}
          disabled={disabled}
          className="hidden"
          id="file-input"
        />

        <label
          htmlFor="file-input"
          className={`px-6 py-2 rounded-lg font-medium transition-colors ${
            disabled
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700 cursor-pointer'
          }`}
        >
          Select File
        </label>

        <p className="text-xs text-gray-500 mt-2">
          Supported formats: JPEG, PNG (max 10MB)
        </p>
      </div>
    </div>
  );
}
