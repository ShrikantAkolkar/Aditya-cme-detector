import React from 'react';
import { CMEEvent } from '../types/cme';
import { AlertCircle, Eye, Zap, Clock, MapPin } from 'lucide-react';
import { format } from 'date-fns';

interface CMEEventsListProps {
  events: CMEEvent[];
}

export const CMEEventsList: React.FC<CMEEventsListProps> = ({ events }) => {
  const getEventTypeColor = (type: CMEEvent['type']) => {
    switch (type) {
      case 'halo':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'partial_halo':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
      case 'non_halo':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-400';
    if (confidence >= 0.6) return 'text-amber-400';
    return 'text-red-400';
  };

  const getSourceIcon = (source: CMEEvent['source']) => {
    switch (source) {
      case 'swis':
        return <Zap className="w-4 h-4 text-blue-400" />;
      case 'cactus':
        return <Eye className="w-4 h-4 text-purple-400" />;
      case 'combined':
        return <AlertCircle className="w-4 h-4 text-green-400" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 text-red-400" />
          <h3 className="text-lg font-semibold text-white">Recent CME Events</h3>
        </div>
        <div className="text-sm text-gray-400">
          {events.length} events detected
        </div>
      </div>

      <div className="space-y-4 max-h-96 overflow-y-auto">
        {events.length === 0 ? (
          <div className="text-center py-8">
            <AlertCircle className="w-12 h-12 text-gray-500 mx-auto mb-3" />
            <p className="text-gray-400">No CME events detected yet</p>
            <p className="text-sm text-gray-500 mt-1">The system is actively monitoring for events</p>
          </div>
        ) : (
          events.map((event) => (
            <div
              key={event.id}
              className="bg-slate-700/30 rounded-lg p-4 border border-slate-600/50 hover:border-slate-500/50 transition-colors"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  {getSourceIcon(event.source)}
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-white font-medium">{event.id}</span>
                      <span className={`px-2 py-1 rounded-full text-xs border ${getEventTypeColor(event.type)}`}>
                        {event.type.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>
                    <div className="flex items-center space-x-4 mt-2 text-sm text-gray-400">
                      <div className="flex items-center space-x-1">
                        <Clock className="w-3 h-3" />
                        <span>{format(event.timestamp, 'HH:mm:ss dd/MM')}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <MapPin className="w-3 h-3" />
                        <span>{event.coordinates.latitude.toFixed(1)}°, {event.coordinates.longitude.toFixed(1)}°</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-lg font-semibold ${getConfidenceColor(event.confidence)}`}>
                    {(event.confidence * 100).toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-400">confidence</div>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-400">Velocity:</span>
                  <p className="text-white font-medium">{event.velocity.toFixed(0)} km/s</p>
                </div>
                <div>
                  <span className="text-gray-400">Width:</span>
                  <p className="text-white font-medium">{event.width.toFixed(0)}°</p>
                </div>
                <div>
                  <span className="text-gray-400">Acceleration:</span>
                  <p className="text-white font-medium">{event.acceleration.toFixed(1)} m/s²</p>
                </div>
                <div>
                  <span className="text-gray-400">Magnitude:</span>
                  <p className="text-white font-medium">{event.magnitude.toFixed(1)}</p>
                </div>
              </div>

              <div className="mt-3 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${
                    event.status === 'detected' ? 'bg-amber-400' :
                    event.status === 'validated' ? 'bg-green-400' : 'bg-red-400'
                  }`}></div>
                  <span className="text-xs text-gray-400 uppercase">{event.status.replace('_', ' ')}</span>
                </div>
                <button className="text-xs text-blue-400 hover:text-blue-300 transition-colors">
                  View Details →
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};