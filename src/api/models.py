from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class ParticleDataResponse(BaseModel):
    """Response model for particle data"""
    id: int
    timestamp: datetime
    proton_flux: float
    electron_flux: float
    alpha_flux: float
    velocity: float
    temperature: float
    density: float
    magnetic_field_bx: float
    magnetic_field_by: float
    magnetic_field_bz: float
    magnetic_field_magnitude: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class CMEEventResponse(BaseModel):
    """Response model for CME events"""
    id: int
    external_id: str
    timestamp: datetime
    event_type: str
    velocity: float
    width: float
    position_angle: float
    acceleration: float
    source: str
    confidence: float
    status: str
    latitude: float
    longitude: float
    magnitude: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SystemStatusResponse(BaseModel):
    """Response model for system status"""
    timestamp: datetime
    swis_ingestion: str
    cactus_ingestion: str
    detection_status: str
    alerts_enabled: bool
    particle_data_points_last_hour: int
    cme_events_today: int
    high_confidence_events_today: int
    system_health: float

class AlertRequest(BaseModel):
    """Request model for sending alerts"""
    event_id: str
    alert_type: str
    recipients: Optional[list] = None
    message: Optional[str] = None

class DetectionConfigRequest(BaseModel):
    """Request model for updating detection configuration"""
    velocity_threshold: Optional[float] = None
    flux_threshold: Optional[float] = None
    confidence_threshold: Optional[float] = None
    temperature_threshold: Optional[float] = None
    magnetic_field_threshold: Optional[float] = None
    time_window: Optional[int] = None