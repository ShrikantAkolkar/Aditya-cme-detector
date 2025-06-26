import React, { useState } from 'react';
import { X, Save, AlertTriangle, Mail, Phone, Webhook } from 'lucide-react';
import { DetectionThresholds, AlertConfig } from '../types/cme';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (thresholds: DetectionThresholds, alerts: AlertConfig) => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose, onSave }) => {
  const [thresholds, setThresholds] = useState<DetectionThresholds>({
    velocityThreshold: 500,
    fluxThreshold: 1200,
    confidenceThreshold: 0.7,
    temperatureThreshold: 200000,
    magneticFieldThreshold: 10,
    timeWindow: 300
  });

  const [alerts, setAlerts] = useState<AlertConfig>({
    email: {
      enabled: true,
      recipients: ['scientist@isro.gov.in']
    },
    sms: {
      enabled: false,
      recipients: ['+91XXXXXXXXXX']
    },
    webhook: {
      enabled: false,
      url: 'https://api.example.com/webhook'
    },
    severity: 'medium'
  });

  if (!isOpen) return null;

  const handleSave = () => {
    onSave(thresholds, alerts);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-800 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-slate-700">
        <div className="flex items-center justify-between p-6 border-b border-slate-700">
          <h2 className="text-xl font-semibold text-white">System Configuration</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-8">
          {/* Detection Thresholds */}
          <div>
            <h3 className="text-lg font-medium text-white mb-4 flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5 text-orange-400" />
              <span>Detection Thresholds</span>
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Velocity Threshold (km/s)
                </label>
                <input
                  type="number"
                  value={thresholds.velocityThreshold}
                  onChange={(e) => setThresholds({...thresholds, velocityThreshold: Number(e.target.value)})}
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Flux Threshold (particles/cm²/s)
                </label>
                <input
                  type="number"
                  value={thresholds.fluxThreshold}
                  onChange={(e) => setThresholds({...thresholds, fluxThreshold: Number(e.target.value)})}
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Confidence Threshold (0-1)
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="1"
                  value={thresholds.confidenceThreshold}
                  onChange={(e) => setThresholds({...thresholds, confidenceThreshold: Number(e.target.value)})}
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Time Window (seconds)
                </label>
                <input
                  type="number"
                  value={thresholds.timeWindow}
                  onChange={(e) => setThresholds({...thresholds, timeWindow: Number(e.target.value)})}
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
            </div>
          </div>

          {/* Alert Configuration */}
          <div>
            <h3 className="text-lg font-medium text-white mb-4 flex items-center space-x-2">
              <Mail className="w-5 h-5 text-blue-400" />
              <span>Alert Configuration</span>
            </h3>

            <div className="space-y-6">
              {/* Email Alerts */}
              <div className="bg-slate-700/30 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <Mail className="w-4 h-4 text-blue-400" />
                    <span className="font-medium text-white">Email Alerts</span>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={alerts.email.enabled}
                      onChange={(e) => setAlerts({
                        ...alerts,
                        email: {...alerts.email, enabled: e.target.checked}
                      })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                  </label>
                </div>
                <input
                  type="email"
                  placeholder="scientist@isro.gov.in"
                  value={alerts.email.recipients[0] || ''}
                  onChange={(e) => setAlerts({
                    ...alerts,
                    email: {...alerts.email, recipients: [e.target.value]}
                  })}
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  disabled={!alerts.email.enabled}
                />
              </div>

              {/* SMS Alerts */}
              <div className="bg-slate-700/30 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <Phone className="w-4 h-4 text-green-400" />
                    <span className="font-medium text-white">SMS Alerts</span>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={alerts.sms.enabled}
                      onChange={(e) => setAlerts({
                        ...alerts,
                        sms: {...alerts.sms, enabled: e.target.checked}
                      })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                  </label>
                </div>
                <input
                  type="tel"
                  placeholder="+91XXXXXXXXXX"
                  value={alerts.sms.recipients[0] || ''}
                  onChange={(e) => setAlerts({
                    ...alerts,
                    sms: {...alerts.sms, recipients: [e.target.value]}
                  })}
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  disabled={!alerts.sms.enabled}
                />
              </div>

              {/* Webhook */}
              <div className="bg-slate-700/30 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <Webhook className="w-4 h-4 text-purple-400" />
                    <span className="font-medium text-white">Webhook</span>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={alerts.webhook.enabled}
                      onChange={(e) => setAlerts({
                        ...alerts,
                        webhook: {...alerts.webhook, enabled: e.target.checked}
                      })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                  </label>
                </div>
                <input
                  type="url"
                  placeholder="https://api.example.com/webhook"
                  value={alerts.webhook.url}
                  onChange={(e) => setAlerts({
                    ...alerts,
                    webhook: {...alerts.webhook, url: e.target.value}
                  })}
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  disabled={!alerts.webhook.enabled}
                />
              </div>

              {/* Severity Level */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Alert Severity Level
                </label>
                <select
                  value={alerts.severity}
                  onChange={(e) => setAlerts({...alerts, severity: e.target.value as AlertConfig['severity']})}
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-end space-x-3 p-6 border-t border-slate-700">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>Save Configuration</span>
          </button>
        </div>
      </div>
    </div>
  );
};