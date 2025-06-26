import React from 'react';
import { Satellite, Activity, AlertTriangle, Settings } from 'lucide-react';
import { SystemStatus } from '../types/cme';

interface HeaderProps {
  systemStatus: SystemStatus;
  onSettingsClick: () => void;
}

export const Header: React.FC<HeaderProps> = ({ systemStatus, onSettingsClick }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
      case 'active':
      case 'enabled':
        return 'text-green-400';
      case 'offline':
      case 'paused':
      case 'disabled':
        return 'text-amber-400';
      case 'error':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700/50 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <Satellite className="w-8 h-8 text-purple-500" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Aditya-CME-Detector</h1>
              <p className="text-sm text-gray-400">Real-time Coronal Mass Ejection Detection System</p>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-4 text-sm">
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-blue-400" />
              <span className="text-gray-300">SWIS:</span>
              <span className={getStatusColor(systemStatus.swisIngestion)}>
                {systemStatus.swisIngestion.toUpperCase()}
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-purple-400" />
              <span className="text-gray-300">CACTUS:</span>
              <span className={getStatusColor(systemStatus.cactusIngestion)}>
                {systemStatus.cactusIngestion.toUpperCase()}
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-orange-400" />
              <span className="text-gray-300">Events Today:</span>
              <span className="text-white font-semibold">{systemStatus.eventsToday}</span>
            </div>
          </div>

          <button
            onClick={onSettingsClick}
            className="p-2 text-gray-400 hover:text-white hover:bg-slate-700/50 rounded-lg transition-colors"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>
    </header>
  );
};