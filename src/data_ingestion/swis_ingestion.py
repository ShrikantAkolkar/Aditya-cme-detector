import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from src.config import config
from src.models.particle_data import ParticleData
from src.database.connection import get_db_session

logger = logging.getLogger(__name__)

class SWISIngestion:
    """SWIS-ASPEX payload data ingestion module"""
    
    def __init__(self):
        self.endpoint = config.get('data_sources.swis.endpoint')
        self.update_interval = config.get('data_sources.swis.update_interval', 30)
        self.timeout = config.get('data_sources.swis.timeout', 10)
        self.retry_attempts = config.get('data_sources.swis.retry_attempts', 3)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_particle_data(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Fetch particle data from SWIS-ASPEX payload"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
            
        params = {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'format': 'json'
        }
        
        for attempt in range(self.retry_attempts):
            try:
                async with self.session.get(self.endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Successfully fetched {len(data)} particle data points")
                        return data
                    else:
                        logger.warning(f"HTTP {response.status}: {await response.text()}")
                        
            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1}")
            except Exception as e:
                logger.error(f"Error fetching data on attempt {attempt + 1}: {e}")
                
            if attempt < self.retry_attempts - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
        logger.error("Failed to fetch particle data after all retry attempts")
        return []
    
    def simulate_particle_data(self, duration_minutes: int = 60) -> List[Dict]:
        """Simulate SWIS particle data for testing"""
        logger.info(f"Simulating {duration_minutes} minutes of particle data")
        
        timestamps = pd.date_range(
            start=datetime.now() - timedelta(minutes=duration_minutes),
            end=datetime.now(),
            freq='30S'  # 30-second intervals
        )
        
        data = []
        for i, timestamp in enumerate(timestamps):
            # Simulate realistic particle flux with some CME-like events
            base_proton_flux = 1000 + np.random.normal(0, 100)
            base_electron_flux = 800 + np.random.normal(0, 80)
            base_alpha_flux = 300 + np.random.normal(0, 30)
            
            # Add occasional CME-like spikes
            if np.random.random() < 0.02:  # 2% chance of spike
                spike_factor = np.random.uniform(2, 5)
                base_proton_flux *= spike_factor
                base_electron_flux *= spike_factor * 0.8
                base_alpha_flux *= spike_factor * 0.6
            
            # Solar wind parameters
            velocity = 400 + np.random.normal(0, 50) + np.sin(i * 0.1) * 20
            temperature = 150000 + np.random.normal(0, 20000)
            density = 5 + np.random.normal(0, 2)
            
            # Magnetic field components
            bx = np.random.normal(0, 3)
            by = np.random.normal(0, 3)
            bz = np.random.normal(0, 3)
            b_magnitude = np.sqrt(bx**2 + by**2 + bz**2)
            
            data.append({
                'timestamp': timestamp.isoformat(),
                'proton_flux': max(0, base_proton_flux),
                'electron_flux': max(0, base_electron_flux),
                'alpha_flux': max(0, base_alpha_flux),
                'velocity': max(200, velocity),
                'temperature': max(50000, temperature),
                'density': max(0.1, density),
                'magnetic_field': {
                    'bx': bx,
                    'by': by,
                    'bz': bz,
                    'magnitude': b_magnitude
                }
            })
        
        return data
    
    async def process_and_store_data(self, raw_data: List[Dict]) -> int:
        """Process and store particle data in database"""
        if not raw_data:
            return 0
            
        processed_count = 0
        
        async with get_db_session() as session:
            for item in raw_data:
                try:
                    particle_data = ParticleData(
                        timestamp=datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00')),
                        proton_flux=item['proton_flux'],
                        electron_flux=item['electron_flux'],
                        alpha_flux=item['alpha_flux'],
                        velocity=item['velocity'],
                        temperature=item['temperature'],
                        density=item['density'],
                        magnetic_field_bx=item['magnetic_field']['bx'],
                        magnetic_field_by=item['magnetic_field']['by'],
                        magnetic_field_bz=item['magnetic_field']['bz'],
                        magnetic_field_magnitude=item['magnetic_field']['magnitude']
                    )
                    
                    session.add(particle_data)
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing particle data item: {e}")
                    continue
            
            await session.commit()
            
        logger.info(f"Processed and stored {processed_count} particle data points")
        return processed_count
    
    async def run_continuous_ingestion(self):
        """Run continuous data ingestion"""
        logger.info("Starting continuous SWIS data ingestion")
        
        while True:
            try:
                end_time = datetime.now()
                start_time = end_time - timedelta(seconds=self.update_interval * 2)
                
                # Try to fetch real data, fallback to simulation
                raw_data = await self.fetch_particle_data(start_time, end_time)
                
                if not raw_data:
                    logger.info("No real data available, using simulated data")
                    raw_data = self.simulate_particle_data(duration_minutes=1)
                
                await self.process_and_store_data(raw_data)
                
            except Exception as e:
                logger.error(f"Error in continuous ingestion: {e}")
            
            await asyncio.sleep(self.update_interval)

# Async context manager for easy usage
async def get_swis_ingestion():
    async with SWISIngestion() as ingestion:
        yield ingestion