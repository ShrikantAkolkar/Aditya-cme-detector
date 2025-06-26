import React, { useState } from 'react';
import { Header } from './components/Header';
import { SystemOverview } from './components/SystemOverview';
import { ParticleDataChart } from './components/ParticleDataChart';
import { CMEEventsList } from './components/CMEEventsList';
import { SettingsModal } from './components/SettingsModal';
import { useRealTimeData } from './hooks/useRealTimeData';
import { ThresholdConfig } from './types/cme';

function App() {
  const { particleData, cmeEvents, systemStatus, metrics, setSystemStatus } = useRealTimeData();
  const [settingsOpen, setSettingsOpen] = useState(false);

  const handleSettingsSave = (config: ThresholdConfig) => {
    console.log('Updated threshold configuration:', config);
    // In a real app, this would update the backend configuration
  };

  const toggleAlerts = () => {
    setSystemStatus(prev => ({
      ...prev,
      alertsEnabled: !prev.alertsEnabled
    }));
  };

  return (
    <div className="min-h-screen bg-slate-900">
      <Header 
        systemStatus={systemStatus} 
        onSettingsClick={() => setSettingsOpen(true)}
      />
      
      <main className="container mx-auto px-6 py-8">
        <SystemOverview metrics={metrics} systemStatus={systemStatus} />
        
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          <div className="xl:col-span-2">
            <ParticleDataChart data={particleData} />
          </div>
          
          <div className="xl:col-span-1">
            <CMEEventsList events={cmeEvents} />
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-16 border-t border-slate-700 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center text-sm text-slate-400">
            <div className="mb-4 md:mb-0">
              <p>Aditya-L1 CME Detection System v1.0.0</p>
              <p>Indian Space Research Organisation (ISRO)</p>
            </div>
            
            <div className="flex space-x-6">
              <button
                onClick={toggleAlerts}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                  systemStatus.alertsEnabled 
                    ? 'bg-green-500/20 text-green-300 hover:bg-green-500/30' 
                    : 'bg-red-500/20 text-red-300 hover:bg-red-500/30'
                }`}
              >
                {systemStatus.alertsEnabled ? 'Alerts ON' : 'Alerts OFF'}
              </button>
              
              <div className="text-xs">
                <p>Mission Status: <span className="text-green-400">Operational</span></p>
                <p>Uptime: 247 days, 18:42:33</p>
              </div>
            </div>
          </div>
        </footer>
      </main>

      <SettingsModal
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        onSave={handleSettingsSave}
      />
    </div>
  );
}

export default App;