import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color?: 'blue' | 'green' | 'purple' | 'amber' | 'red';
  isLoading?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  icon: Icon,
  trend,
  color = 'blue',
  isLoading = false
}) => {
  const colorClasses = {
    blue: {
      bg: 'bg-blue-500/10',
      icon: 'text-blue-400',
      border: 'border-blue-500/20',
      glow: 'shadow-blue-500/20'
    },
    green: {
      bg: 'bg-green-500/10',
      icon: 'text-green-400',
      border: 'border-green-500/20',
      glow: 'shadow-green-500/20'
    },
    purple: {
      bg: 'bg-purple-500/10',
      icon: 'text-purple-400',
      border: 'border-purple-500/20',
      glow: 'shadow-purple-500/20'
    },
    amber: {
      bg: 'bg-amber-500/10',
      icon: 'text-amber-400',
      border: 'border-amber-500/20',
      glow: 'shadow-amber-500/20'
    },
    red: {
      bg: 'bg-red-500/10',
      icon: 'text-red-400',
      border: 'border-red-500/20',
      glow: 'shadow-red-500/20'
    }
  };

  const colors = colorClasses[color];

  return (
    <div className={`
      relative overflow-hidden
      bg-slate-800/50 backdrop-blur-sm 
      border ${colors.border}
      rounded-xl p-6 
      transition-all duration-300 ease-out
      hover:scale-105 hover:shadow-xl hover:${colors.glow}
      group cursor-pointer
    `}>
      {/* Animated background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <div className={`p-3 rounded-lg ${colors.bg} transition-transform duration-300 group-hover:scale-110`}>
            <Icon className={`w-6 h-6 ${colors.icon}`} />
          </div>
          
          {trend && (
            <div className={`flex items-center space-x-1 text-sm ${
              trend.isPositive ? 'text-green-400' : 'text-red-400'
            }`}>
              <span>{trend.isPositive ? '↗' : '↘'}</span>
              <span>{Math.abs(trend.value)}%</span>
            </div>
          )}
        </div>
        
        <div className="space-y-1">
          <p className="text-sm text-gray-400 font-medium">{title}</p>
          <div className="flex items-baseline space-x-2">
            {isLoading ? (
              <div className="h-8 w-20 bg-slate-700/50 rounded animate-pulse" />
            ) : (
              <p className="text-2xl font-bold text-white transition-all duration-300 group-hover:text-3xl">
                {value}
              </p>
            )}
          </div>
        </div>
      </div>
      
      {/* Pulse animation for active metrics */}
      <div className="absolute inset-0 rounded-xl border-2 border-transparent group-hover:border-white/10 transition-all duration-300" />
    </div>
  );
};