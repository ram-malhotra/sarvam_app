import React from 'react';

interface LoadingProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const Loading: React.FC<LoadingProps> = ({ message = 'Loading...', size = 'md' }) => {
  const sizeClasses = {
    sm: 'w-5 h-5 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
  }[size];

  return (
    <div
      role="status"
      aria-live="polite"
      className="flex flex-col items-center justify-center p-6 text-center"
    >
      <div
        className={`${sizeClasses} border-orange-500 border-t-transparent rounded-full animate-spin mb-3`}
      />
      {message && <p className="text-sm font-medium text-gray-600">{message}</p>}
      <span className="sr-only">Loading</span>
    </div>
  );
};

export default Loading;
