import { useState, useEffect, useCallback } from 'react';
import { CMEEvent, ParticleData, SystemStatus } from '../types/cme';

// Simulated real-time data generation
export const useRealTimeData = () => {
  const [cmeEvents, setCMEEvents] = useState<CMEEvent[]>([]);
  const [particleData, setParticleData] = useState<ParticleData[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    swisIngestion: 'online',
    cactusIngestion: 'online',
    detection: 'active',
    alerts: 'enabled',
    lastUpdate: new Date(),
    eventsToday: 0,
    systemHealth: 98.5
  });

  const generateParticleData = useCallback((): ParticleData => {
    const now = new Date();
    const baseFlux = 1000;
    const noise = () => (Math.random() - 0.5) * 200;
    
    return {
      timestamp: now,
      protonFlux: baseFlux + noise() + Math.sin(now.getTime() / 10000) * 100,
      electronFlux: baseFlux * 0.8 + noise(),
      alphaFlux: baseFlux * 0.3 + noise(),
      temperature: 150000 + Math.random() * 50000,
      density: 5 + Math.random() * 10,
      velocity: 400 + Math.random() * 200,
      magneticField: {
        x: Math.random() * 10 - 5,
        y: Math.random() * 10 - 5,
        z: Math.random() * 10 - 5,
        magnitude: Math.random() * 15 + 5
      }
    };
  }, []);

  const generateCMEEvent = useCallback((): CMEEvent => {
    const types: CMEEvent['type'][] = ['halo', 'partial_halo', 'non_halo'];
    const sources: CMEEvent['source'][] = ['swis', 'cactus', 'combined'];
    
    return {
      id: `CME_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
      type: types[Math.floor(Math.random() * types.length)],
      velocity: 300 + Math.random() * 1200,
      width: 60 + Math.random() * 300,
      acceleration: -10 + Math.random() * 20,
      confidence: 0.6 + Math.random() * 0.4,
      source: sources[Math.floor(Math.random() * sources.length)],
      status: 'detected',
      coordinates: {
        latitude: Math.random() * 180 - 90,
        longitude: Math.random() * 360 - 180
      },
      magnitude: Math.random() * 10 + 1
    };
  }, []);

  useEffect(() => {
    // Simulate particle data updates every 2 seconds
    const particleInterval = setInterval(() => {
      const newData = generateParticleData();
      setParticleData(prev => [...prev.slice(-99), newData]);
    }, 2000);

    // Simulate CME events randomly (low probability)
    const cmeInterval = setInterval(() => {
      if (Math.random() < 0.1) { // 10% chance every 30 seconds
        const newEvent = generateCMEEvent();
        setCMEEvents(prev => [newEvent, ...prev.slice(0, 49)]);
        setSystemStatus(prev => ({
          ...prev,
          eventsToday: prev.eventsToday + 1,
          lastUpdate: new Date()
        }));
      }
    }, 30000);

    // System status updates
    const statusInterval = setInterval(() => {
      setSystemStatus(prev => ({
        ...prev,
        lastUpdate: new Date(),
        systemHealth: 95 + Math.random() * 5
      }));
    }, 10000);

    return () => {
      clearInterval(particleInterval);
      clearInterval(cmeInterval);
      clearInterval(statusInterval);
    };
  }, [generateParticleData, generateCMEEvent]);

  return { cmeEvents, particleData, systemStatus };
};