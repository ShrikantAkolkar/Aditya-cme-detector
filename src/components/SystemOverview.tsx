import React from 'react';
import { Activity, Zap, Database, Shield, Clock } from 'lucide-react';
import { SystemStatus } from '../types/cme';
import { format } from 'date-fns';

interface SystemOverviewProps {
  systemStatus: SystemStatus;
}

export const SystemOverview: React.FC<SystemOverviewProps> = ({ systemStatus }) => {
  const stats = [
    {
      label: 'System Health',
      value: `${systemStatus.systemHealth.toFixed(1)}%`,
      icon: Activity,
      color: systemStatus.systemHealth > 95 ? 'text-green-400' : systemStatus.systemHealth > 85 ? 'text-amber-400' : 'text-red-400',
      bgColor: systemStatus.systemHealth > 95 ? 'bg-green-400/10' : systemStatus.systemHealth > 85 ? 'bg-amber-400/10' : 'bg-red-400/10'
    },
    {
      label: 'Detection Status',
      value: systemStatus.detection.toUpperCase(),
      icon: Zap,
      color: systemStatus.detection === 'active' ? 'text-green-400' : 'text-amber-400',
      bgColor: systemStatus.detection === 'active' ? 'bg-green-400/10' : 'bg-amber-400/10'
    },
    {
      label: 'Data Ingestion',
      value: 'STREAMING',
      icon: Database,
      color: 'text-blue-400',
      bgColor: 'bg-blue-400/10'
    },
    {
      label: 'Alert System',
      value: systemStatus.alerts.toUpperCase(),
      icon: Shield,
      color: systemStatus.alerts === 'enabled' ? 'text-green-400' : 'text-gray-400',
      bgColor: systemStatus.alerts === 'enabled' ? 'bg-green-400/10' : 'bg-gray-400/10'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {stats.map((stat, index) => (
        <div key={index} className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
          <div className="flex items-center justify-between mb-4">
            <div className={`p-3 rounded-lg ${stat.bgColor}`}>
              <stat.icon className={`w-6 h-6 ${stat.color}`} />
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-400">{stat.label}</p>
              <p className={`text-xl font-semibold ${stat.color}`}>{stat.value}</p>
            </div>
          </div>
          {index === 0 && (
            <div className="w-full bg-slate-700 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-500 ${
                  systemStatus.systemHealth > 95 ? 'bg-green-400' : 
                  systemStatus.systemHealth > 85 ? 'bg-amber-400' : 'bg-red-400'
                }`}
                style={{ width: `${systemStatus.systemHealth}%` }}
              ></div>
            </div>
          )}
        </div>
      ))}
      
      <div className="md:col-span-2 lg:col-span-4 bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
        <div className="flex items-center space-x-3 mb-4">
          <Clock className="w-5 h-5 text-purple-400" />
          <h3 className="text-lg font-semibold text-white">System Status</h3>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
          <div>
            <span className="text-gray-400">Last Update:</span>
            <p className="text-white font-medium">{format(systemStatus.lastUpdate, 'HH:mm:ss')}</p>
          </div>
          <div>
            <span className="text-gray-400">Events Detected:</span>
            <p className="text-white font-medium">{systemStatus.eventsToday} today</p>
          </div>
          <div>
            <span className="text-gray-400">Uptime:</span>
            <p className="text-white font-medium">99.8%</p>
          </div>
        </div>
      </div>
    </div>
  );
};