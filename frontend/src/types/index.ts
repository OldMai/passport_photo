/**
 * TypeScript types for the passport photo application
 */

export interface UploadResponse {
  upload_id: string;
  filename: string;
  preview_url: string;
}

export interface ValidationCheck {
  passed: boolean;
  message: string;
  [key: string]: any;  // Allow additional properties
}

export interface ValidationResults {
  passed: boolean;
  checks: {
    resolution: ValidationCheck;
    head_size: ValidationCheck;
    face_centered: ValidationCheck;
    eyes_level: ValidationCheck;
    face_forward: ValidationCheck;
  };
}

export interface ProcessResponse {
  job_id: string;
  status: string;
  processed_url: string;
  print_layout_url: string;
  validation: ValidationResults;
}

export type ProcessingStatus = 'idle' | 'uploading' | 'processing' | 'completed' | 'error';

export interface AppState {
  status: ProcessingStatus;
  uploadedFile: File | null;
  uploadResponse: UploadResponse | null;
  processResponse: ProcessResponse | null;
  error: string | null;
}
