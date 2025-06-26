from sqlalchemy import Column, Integer, Float, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ParticleData(Base):
    """Particle data model for SWIS-ASPEX payload data"""
    
    __tablename__ = 'particle_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Particle flux measurements (particles/cm²/s)
    proton_flux = Column(Float, nullable=False)
    electron_flux = Column(Float, nullable=False)
    alpha_flux = Column(Float, nullable=False)
    
    # Solar wind parameters
    velocity = Column(Float, nullable=False)  # km/s
    temperature = Column(Float, nullable=False)  # K
    density = Column(Float, nullable=False)  # particles/cm³
    
    # Magnetic field components (nT)
    magnetic_field_bx = Column(Float, nullable=False)
    magnetic_field_by = Column(Float, nullable=False)
    magnetic_field_bz = Column(Float, nullable=False)
    magnetic_field_magnitude = Column(Float, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_timestamp_flux', 'timestamp', 'proton_flux'),
        Index('idx_timestamp_velocity', 'timestamp', 'velocity'),
    )
    
    def __repr__(self):
        return f"<ParticleData(timestamp={self.timestamp}, proton_flux={self.proton_flux})>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'proton_flux': self.proton_flux,
            'electron_flux': self.electron_flux,
            'alpha_flux': self.alpha_flux,
            'velocity': self.velocity,
            'temperature': self.temperature,
            'density': self.density,
            'magnetic_field': {
                'bx': self.magnetic_field_bx,
                'by': self.magnetic_field_by,
                'bz': self.magnetic_field_bz,
                'magnitude': self.magnetic_field_magnitude
            },
            'created_at': self.created_at.isoformat()
        }