/**
 * ProcessingStatus component - Shows processing progress
 */

interface ProcessingStatusProps {
  status: 'uploading' | 'processing';
}

export default function ProcessingStatus({ status }: ProcessingStatusProps) {
  return (
    <div className="flex flex-col items-center gap-4 py-8">
      <div className="relative">
        <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
      </div>

      <div className="text-center">
        <h3 className="text-xl font-semibold text-gray-800">
          {status === 'uploading' ? 'Uploading photo...' : 'Processing photo...'}
        </h3>
        <p className="text-sm text-gray-600 mt-2">
          {status === 'uploading'
            ? 'Please wait while we upload your photo'
            : 'Detecting face, removing background, and creating passport photo'}
        </p>
      </div>

      <div className="flex flex-col gap-2 text-sm text-gray-500 mt-4">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${status === 'processing' ? 'bg-green-500' : 'bg-blue-500 animate-pulse'}`}></div>
          <span>{status === 'uploading' ? 'Uploading...' : 'Upload complete'}</span>
        </div>
        {status === 'processing' && (
          <>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
              <span>Detecting face...</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-gray-300"></div>
              <span>Removing background...</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-gray-300"></div>
              <span>Validating requirements...</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-gray-300"></div>
              <span>Creating passport photo...</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
