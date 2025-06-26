export interface CMEEvent {
  id: string;
  timestamp: Date;
  type: 'halo' | 'partial_halo' | 'non_halo';
  velocity: number;
  width: number;
  acceleration: number;
  confidence: number;
  source: 'swis' | 'cactus' | 'combined';
  status: 'detected' | 'validated' | 'false_positive';
  coordinates: {
    latitude: number;
    longitude: number;
  };
  magnitude: number;
}

export interface ParticleData {
  timestamp: Date;
  protonFlux: number;
  electronFlux: number;
  alphaFlux: number;
  temperature: number;
  density: number;
  velocity: number;
  magneticField: {
    x: number;
    y: number;
    z: number;
    magnitude: number;
  };
}

export interface SystemStatus {
  swisIngestion: 'online' | 'offline' | 'error';
  cactusIngestion: 'online' | 'offline' | 'error';
  detection: 'active' | 'paused' | 'error';
  alerts: 'enabled' | 'disabled';
  lastUpdate: Date;
  eventsToday: number;
  systemHealth: number;
}

export interface DetectionThresholds {
  velocityThreshold: number;
  fluxThreshold: number;
  confidenceThreshold: number;
  temperatureThreshold: number;
  magneticFieldThreshold: number;
  timeWindow: number;
}

export interface AlertConfig {
  email: {
    enabled: boolean;
    recipients: string[];
  };
  sms: {
    enabled: boolean;
    recipients: string[];
  };
  webhook: {
    enabled: boolean;
    url: string;
  };
  severity: 'low' | 'medium' | 'high' | 'critical';
}