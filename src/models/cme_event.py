from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class CMEType(enum.Enum):
    HALO = "halo"
    PARTIAL_HALO = "partial_halo"
    NON_HALO = "non_halo"

class CMEStatus(enum.Enum):
    DETECTED = "detected"
    VALIDATED = "validated"
    FALSE_POSITIVE = "false_positive"

class CMESource(enum.Enum):
    SWIS = "swis"
    CACTUS = "cactus"
    COMBINED = "combined"

class CMEEvent(Base):
    """CME event model for detected and validated events"""
    
    __tablename__ = 'cme_events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(100), unique=True, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # CME characteristics
    event_type = Column(Enum(CMEType), nullable=False)
    velocity = Column(Float, nullable=False)  # km/s
    width = Column(Float, nullable=False)  # degrees
    position_angle = Column(Float, default=0)  # degrees from solar north
    acceleration = Column(Float, default=0)  # m/s²
    
    # Detection metadata
    source = Column(Enum(CMESource), nullable=False)
    confidence = Column(Float, nullable=False)  # 0-1
    status = Column(Enum(CMEStatus), default=CMEStatus.DETECTED)
    
    # Spatial coordinates
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    magnitude = Column(Float, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CMEEvent(id={self.external_id}, type={self.event_type.value}, velocity={self.velocity})>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.external_id,
            'timestamp': self.timestamp.isoformat(),
            'type': self.event_type.value,
            'velocity': self.velocity,
            'width': self.width,
            'position_angle': self.position_angle,
            'acceleration': self.acceleration,
            'source': self.source.value,
            'confidence': self.confidence,
            'status': self.status.value,
            'coordinates': {
                'latitude': self.latitude,
                'longitude': self.longitude
            },
            'magnitude': self.magnitude,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }