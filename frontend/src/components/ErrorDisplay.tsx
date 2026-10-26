import React from 'react';

interface ErrorDisplayProps {
  message: string;
  onRetry?: () => void;
  title?: string;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  message,
  onRetry,
  title,
}) => {
  const isSarvamOrApiKey =
    /sarvam|api[ _-]?key/i.test(message) ||
    /unauthorized|authentication|forbidden/i.test(message);
  const isNetwork =
    /network|failed to fetch|connection refused|econnrefused/i.test(message);
  const isNotFound = /not found|404/i.test(message);

  let badgeColor = 'bg-red-50 border-red-200 text-red-800';
  let defaultTitle = 'An error occurred';

  if (isSarvamOrApiKey) {
    badgeColor = 'bg-amber-50 border-amber-300 text-amber-900';
    defaultTitle = 'API Configuration Required';
  } else if (isNetwork) {
    badgeColor = 'bg-orange-50 border-orange-200 text-orange-900';
    defaultTitle = 'Backend Connection Error';
  } else if (isNotFound) {
    badgeColor = 'bg-blue-50 border-blue-200 text-blue-900';
    defaultTitle = 'Resource Not Found';
  }

  return (
    <div
      role="alert"
      className={`rounded-xl border p-5 max-w-lg mx-auto my-4 shadow-xs ${badgeColor}`}
    >
      <div className="flex items-start gap-3">
        <div className="shrink-0 mt-0.5">
          {isSarvamOrApiKey ? (
            <svg
              className="w-6 h-6 text-amber-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          ) : isNetwork ? (
            <svg
              className="w-6 h-6 text-orange-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 4.243a9 9 0 01-12.728 0m0 0l2.829-2.829m-2.829 2.829L3 21m2.828-12.536a5 5 0 017.072 0l-2.829 2.829"
              />
            </svg>
          ) : (
            <svg
              className="w-6 h-6 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          )}
        </div>

        <div className="flex-1">
          <h3 className="text-base font-semibold">{title || defaultTitle}</h3>
          <p className="mt-1 text-sm leading-relaxed">{message}</p>

          {isSarvamOrApiKey && (
            <div className="mt-3 p-3 bg-white/80 rounded-lg border border-amber-200 text-xs font-mono text-gray-800 space-y-1">
              <p className="font-semibold text-gray-700 font-sans">Setup Instructions:</p>
              <p>1. Get an API key from Sarvam AI console</p>
              <p>2. Set environment variable: <span className="text-orange-600 font-bold">SARVAM_API_KEY=your_key_here</span></p>
              <p>3. Restart the backend service</p>
            </div>
          )}

          {isNetwork && (
            <p className="mt-2 text-xs text-orange-800">
              Check if the backend server is running on <code className="bg-white/80 px-1 py-0.5 rounded font-mono">http://localhost:8000</code>.
            </p>
          )}

          {onRetry && (
            <div className="mt-4">
              <button
                type="button"
                onClick={onRetry}
                className="inline-flex items-center justify-center min-h-[44px] px-4 py-2 text-sm font-semibold text-white bg-orange-600 hover:bg-orange-700 active:bg-orange-800 rounded-lg shadow-xs transition-colors focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2"
              >
                <svg
                  className="w-4 h-4 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
                Retry
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ErrorDisplay;
