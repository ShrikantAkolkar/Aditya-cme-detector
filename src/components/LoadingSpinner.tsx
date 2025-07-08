import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: 'blue' | 'purple' | 'green' | 'white';
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  color = 'blue' 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  };

  const colorClasses = {
    blue: 'border-blue-500',
    purple: 'border-purple-500',
    green: 'border-green-500',
    white: 'border-white'
  };

  return (
    <div className="flex items-center justify-center">
      <div
        className={`${sizeClasses[size]} border-2 ${colorClasses[color]} border-t-transparent rounded-full animate-spin`}
      />
    </div>
  );
};