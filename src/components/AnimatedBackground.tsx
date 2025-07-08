import React from 'react';

export const AnimatedBackground: React.FC = () => {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none">
      {/* Animated particles */}
      <div className="absolute inset-0">
        {[...Array(50)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-blue-400/20 rounded-full animate-pulse"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${2 + Math.random() * 3}s`,
            }}
          />
        ))}
      </div>
      
      {/* Orbital paths */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="relative">
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              className="absolute border border-purple-500/10 rounded-full animate-spin"
              style={{
                width: `${300 + i * 200}px`,
                height: `${300 + i * 200}px`,
                left: `${-150 - i * 100}px`,
                top: `${-150 - i * 100}px`,
                animationDuration: `${20 + i * 10}s`,
                animationDirection: i % 2 === 0 ? 'normal' : 'reverse',
              }}
            >
              <div
                className="absolute w-2 h-2 bg-purple-400/40 rounded-full"
                style={{
                  top: '50%',
                  right: '0',
                  transform: 'translateY(-50%)',
                }}
              />
            </div>
          ))}
        </div>
      </div>
      
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900/50 via-transparent to-purple-900/20" />
    </div>
  );
};