import React from 'react';

interface MicrophoneButtonProps {
  isRecording: boolean;
  isProcessing: boolean;
  isSupported: boolean;
  onStartRecording: () => void;
  onStopRecording: () => void;
  disabled?: boolean;
}

export const MicrophoneButton: React.FC<MicrophoneButtonProps> = ({
  isRecording,
  isProcessing,
  isSupported,
  onStartRecording,
  onStopRecording,
  disabled = false,
}) => {
  const handleClick = () => {
    if (disabled || isProcessing || !isSupported) return;
    if (isRecording) {
      onStopRecording();
    } else {
      onStartRecording();
    }
  };

  const getStatusText = () => {
    if (!isSupported) return 'Voice input not supported in this browser';
    if (isProcessing) return 'Listening & processing order...';
    if (isRecording) return 'Recording... Tap to stop & send';
    return 'Tap to speak order';
  };

  return (
    <div className="flex flex-col items-center justify-center py-2">
      <div className="relative flex items-center justify-center">
        {/* Pulsing ring when recording */}
        {isRecording && (
          <span className="absolute w-24 h-24 rounded-full bg-red-400 opacity-75 animate-ping" />
        )}

        <button
          type="button"
          onClick={handleClick}
          disabled={disabled || isProcessing || !isSupported}
          aria-label={
            isRecording
              ? 'Stop recording voice order'
              : isProcessing
              ? 'Processing voice order'
              : 'Start recording voice order'
          }
          className={`relative z-10 flex items-center justify-center w-20 h-20 rounded-full shadow-lg transition-all transform active:scale-95 focus:outline-none focus:ring-4 focus:ring-orange-300 disabled:opacity-50 disabled:cursor-not-allowed ${
            isRecording
              ? 'bg-red-600 text-white animate-mic-pulse ring-4 ring-red-300'
              : isProcessing
              ? 'bg-amber-500 text-white cursor-wait'
              : 'bg-orange-600 hover:bg-orange-500 active:bg-orange-700 text-white shadow-orange-500/30'
          }`}
          title={!isSupported ? 'Microphone not supported' : undefined}
        >
          {isProcessing ? (
            <svg
              className="w-8 h-8 animate-spin"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          ) : isRecording ? (
            <div className="flex flex-col items-center">
              <span className="w-6 h-6 bg-white rounded-xs" />
            </div>
          ) : (
            <svg
              className="w-9 h-9"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
              <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
            </svg>
          )}
        </button>
      </div>

      <p className="mt-2 text-xs sm:text-sm font-medium text-gray-600 transition-colors">
        {getStatusText()}
      </p>
    </div>
  );
};

export default MicrophoneButton;
