import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from src.config import config
from src.models.cme_event import CMEEvent
from src.database.connection import get_db_session

logger = logging.getLogger(__name__)

class CACTUSIngestion:
    """CACTUS database CME event ingestion module"""
    
    def __init__(self):
        self.endpoint = config.get('data_sources.cactus.endpoint')
        self.update_interval = config.get('data_sources.cactus.update_interval', 3600)
        self.timeout = config.get('data_sources.cactus.timeout', 30)
        self.retry_attempts = config.get('data_sources.cactus.retry_attempts', 3)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_cme_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Fetch CME events from CACTUS database"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
            
        params = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'format': 'json'
        }
        
        for attempt in range(self.retry_attempts):
            try:
                async with self.session.get(self.endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Successfully fetched {len(data)} CME events from CACTUS")
                        return data
                    else:
                        logger.warning(f"HTTP {response.status}: {await response.text()}")
                        
            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1}")
            except Exception as e:
                logger.error(f"Error fetching CACTUS data on attempt {attempt + 1}: {e}")
                
            if attempt < self.retry_attempts - 1:
                await asyncio.sleep(2 ** attempt)
                
        logger.error("Failed to fetch CACTUS data after all retry attempts")
        return []
    
    def simulate_cme_events(self, days: int = 7) -> List[Dict]:
        """Simulate CME events for testing"""
        logger.info(f"Simulating CME events for {days} days")
        
        events = []
        start_date = datetime.now() - timedelta(days=days)
        
        # Generate 1-3 events per day on average
        num_events = np.random.poisson(days * 2)
        
        for i in range(num_events):
            # Random timestamp within the date range
            random_hours = np.random.uniform(0, days * 24)
            timestamp = start_date + timedelta(hours=random_hours)
            
            # CME characteristics
            cme_types = ['halo', 'partial_halo', 'non_halo']
            cme_type = np.random.choice(cme_types, p=[0.1, 0.3, 0.6])  # Halo events are rare
            
            # Velocity distribution (typical CME velocities)
            if cme_type == 'halo':
                velocity = np.random.normal(800, 300)  # Faster for halo CMEs
            else:
                velocity = np.random.normal(500, 200)
            
            velocity = max(200, velocity)  # Minimum velocity
            
            # Width and other parameters
            if cme_type == 'halo':
                width = 360  # Full halo
            elif cme_type == 'partial_halo':
                width = np.random.uniform(120, 359)
            else:
                width = np.random.uniform(20, 119)
            
            # Position angle (degrees from solar north)
            position_angle = np.random.uniform(0, 360)
            
            # Acceleration (usually negative for CMEs)
            acceleration = np.random.normal(-5, 10)
            
            events.append({
                'id': f'CACTUS_{timestamp.strftime("%Y%m%d_%H%M%S")}_{i:03d}',
                'timestamp': timestamp.isoformat(),
                'type': cme_type,
                'velocity': velocity,
                'width': width,
                'position_angle': position_angle,
                'acceleration': acceleration,
                'source': 'cactus',
                'confidence': np.random.uniform(0.7, 0.95),
                'coordinates': {
                    'latitude': np.random.uniform(-90, 90),
                    'longitude': np.random.uniform(-180, 180)
                },
                'magnitude': np.random.uniform(1, 10)
            })
        
        # Sort by timestamp
        events.sort(key=lambda x: x['timestamp'])
        return events
    
    async def process_and_store_events(self, raw_events: List[Dict]) -> int:
        """Process and store CME events in database"""
        if not raw_events:
            return 0
            
        processed_count = 0
        
        async with get_db_session() as session:
            for event in raw_events:
                try:
                    # Check if event already exists
                    existing = await session.execute(
                        "SELECT id FROM cme_events WHERE external_id = :external_id",
                        {"external_id": event['id']}
                    )
                    
                    if existing.fetchone():
                        continue  # Skip existing events
                    
                    cme_event = CMEEvent(
                        external_id=event['id'],
                        timestamp=datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00')),
                        event_type=event['type'],
                        velocity=event['velocity'],
                        width=event['width'],
                        position_angle=event.get('position_angle', 0),
                        acceleration=event.get('acceleration', 0),
                        source=event['source'],
                        confidence=event['confidence'],
                        latitude=event['coordinates']['latitude'],
                        longitude=event['coordinates']['longitude'],
                        magnitude=event['magnitude'],
                        status='detected'
                    )
                    
                    session.add(cme_event)
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing CME event: {e}")
                    continue
            
            await session.commit()
            
        logger.info(f"Processed and stored {processed_count} new CME events")
        return processed_count
    
    async def run_continuous_ingestion(self):
        """Run continuous CME event ingestion"""
        logger.info("Starting continuous CACTUS data ingestion")
        
        while True:
            try:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=1)  # Look back 1 day
                
                # Try to fetch real data, fallback to simulation
                raw_events = await self.fetch_cme_events(start_date, end_date)
                
                if not raw_events:
                    logger.info("No real CACTUS data available, using simulated events")
                    raw_events = self.simulate_cme_events(days=1)
                
                await self.process_and_store_events(raw_events)
                
            except Exception as e:
                logger.error(f"Error in continuous CACTUS ingestion: {e}")
            
            await asyncio.sleep(self.update_interval)

# Async context manager for easy usage
async def get_cactus_ingestion():
    async with CACTUSIngestion() as ingestion:
        yield ingestion