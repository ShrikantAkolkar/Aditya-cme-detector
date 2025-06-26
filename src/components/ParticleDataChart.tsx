import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { ParticleData } from '../types/cme';
import { format } from 'date-fns';
import { TrendingUp } from 'lucide-react';

interface ParticleDataChartProps {
  data: ParticleData[];
}

export const ParticleDataChart: React.FC<ParticleDataChartProps> = ({ data }) => {
  const chartData = data.slice(-30).map((item, index) => ({
    time: format(item.timestamp, 'HH:mm:ss'),
    protonFlux: Math.round(item.protonFlux),
    electronFlux: Math.round(item.electronFlux),
    alphaFlux: Math.round(item.alphaFlux),
    velocity: Math.round(item.velocity),
    temperature: Math.round(item.temperature / 1000), // Convert to thousands
    magneticField: Math.round(item.magneticField.magnitude * 10) / 10
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-800 border border-slate-600 rounded-lg p-3 shadow-lg">
          <p className="text-white font-medium mb-2">{`Time: ${label}`}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {`${entry.dataKey}: ${entry.value}${
                entry.dataKey.includes('Flux') ? ' particles/cm²/s' :
                entry.dataKey === 'velocity' ? ' km/s' :
                entry.dataKey === 'temperature' ? 'K (×1000)' :
                entry.dataKey === 'magneticField' ? ' nT' : ''
              }`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
      <div className="flex items-center space-x-3 mb-6">
        <TrendingUp className="w-5 h-5 text-blue-400" />
        <h3 className="text-lg font-semibold text-white">SWIS-ASPEX Particle Data Stream</h3>
        <div className="flex items-center space-x-2 ml-auto">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-400">Live</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="h-80">
          <h4 className="text-sm font-medium text-gray-300 mb-3">Particle Flux (particles/cm²/s)</h4>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="time" 
                stroke="#9CA3AF" 
                fontSize={12}
                tick={{ fill: '#9CA3AF' }}
              />
              <YAxis 
                stroke="#9CA3AF" 
                fontSize={12}
                tick={{ fill: '#9CA3AF' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="protonFlux" 
                stroke="#3B82F6" 
                strokeWidth={2}
                dot={false}
                name="Proton Flux"
              />
              <Line 
                type="monotone" 
                dataKey="electronFlux" 
                stroke="#10B981" 
                strokeWidth={2}
                dot={false}
                name="Electron Flux"
              />
              <Line 
                type="monotone" 
                dataKey="alphaFlux" 
                stroke="#F59E0B" 
                strokeWidth={2}
                dot={false}
                name="Alpha Flux"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="h-80">
          <h4 className="text-sm font-medium text-gray-300 mb-3">Environmental Parameters</h4>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="time" 
                stroke="#9CA3AF" 
                fontSize={12}
                tick={{ fill: '#9CA3AF' }}
              />
              <YAxis 
                stroke="#9CA3AF" 
                fontSize={12}
                tick={{ fill: '#9CA3AF' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="velocity" 
                stroke="#7C3AED" 
                strokeWidth={2}
                dot={false}
                name="Solar Wind Velocity"
              />
              <Line 
                type="monotone" 
                dataKey="temperature" 
                stroke="#EF4444" 
                strokeWidth={2}
                dot={false}
                name="Temperature (×1000K)"
              />
              <Line 
                type="monotone" 
                dataKey="magneticField" 
                stroke="#F97316" 
                strokeWidth={2}
                dot={false}
                name="Magnetic Field"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};