/**
 * ValidationResults component - Displays passport photo validation results
 */

import type { ValidationResults } from '../types';

interface ValidationResultsProps {
  validation: ValidationResults;
}

export default function ValidationResults({ validation }: ValidationResultsProps) {
  const checkEntries = Object.entries(validation.checks);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center gap-3 mb-4">
        {validation.passed ? (
          <>
            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">All Checks Passed</h3>
              <p className="text-sm text-gray-600">Your photo meets all passport requirements</p>
            </div>
          </>
        ) : (
          <>
            <div className="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Some Checks Failed</h3>
              <p className="text-sm text-gray-600">Photo processed, but may need adjustment</p>
            </div>
          </>
        )}
      </div>

      <div className="space-y-3">
        {checkEntries.map(([key, check]) => (
          <div
            key={key}
            className={`flex items-start gap-3 p-3 rounded-lg ${
              check.passed ? 'bg-green-50' : 'bg-yellow-50'
            }`}
          >
            <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${
              check.passed ? 'bg-green-100' : 'bg-yellow-100'
            }`}>
              {check.passed ? (
                <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg className="w-3 h-3 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              )}
            </div>
            <div className="flex-1">
              <p className={`text-sm font-medium ${
                check.passed ? 'text-green-900' : 'text-yellow-900'
              }`}>
                {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </p>
              <p className={`text-sm ${
                check.passed ? 'text-green-700' : 'text-yellow-700'
              }`}>
                {check.message}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
