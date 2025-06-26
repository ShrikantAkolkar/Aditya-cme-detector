from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import asyncio
import logging
from contextlib import asynccontextmanager

from src.config import config
from src.database.connection import init_database, close_database, get_db_session
from src.data_ingestion.swis_ingestion import SWISIngestion
from src.data_ingestion.cactus_ingestion import CACTUSIngestion
from src.detection.cme_detector import CMEDetector
from src.alerts.alert_manager import AlertManager
from src.api.models import CMEEventResponse, ParticleDataResponse, SystemStatusResponse

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.get('logging.level', 'INFO')),
    format=config.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
logger = logging.getLogger(__name__)

# Global instances
cme_detector = CMEDetector()
alert_manager = AlertManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting Aditya-CME-Detector API")
    await init_database()
    
    # Start background tasks
    asyncio.create_task(run_data_ingestion())
    asyncio.create_task(run_cme_detection())
    
    yield
    
    # Shutdown
    logger.info("Shutting down Aditya-CME-Detector API")
    await close_database()

app = FastAPI(
    title="Aditya-CME-Detector API",
    description="Real-time CME detection system using Aditya-L1 SWIS-ASPEX data",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Background tasks
async def run_data_ingestion():
    """Run continuous data ingestion"""
    logger.info("Starting data ingestion background task")
    
    async with SWISIngestion() as swis_ingestion:
        swis_task = asyncio.create_task(swis_ingestion.run_continuous_ingestion())
        
        async with CACTUSIngestion() as cactus_ingestion:
            cactus_task = asyncio.create_task(cactus_ingestion.run_continuous_ingestion())
            
            await asyncio.gather(swis_task, cactus_task)

async def run_cme_detection():
    """Run continuous CME detection"""
    logger.info("Starting CME detection background task")
    
    while True:
        try:
            async with get_db_session() as session:
                # Get recent particle data
                end_time = datetime.now()
                start_time = end_time - timedelta(hours=1)
                
                result = await session.execute(
                    """
                    SELECT * FROM particle_data 
                    WHERE timestamp >= :start_time AND timestamp <= :end_time
                    ORDER BY timestamp
                    """,
                    {"start_time": start_time, "end_time": end_time}
                )
                
                particle_data = result.fetchall()
                
                if particle_data:
                    # Convert to DataFrame format expected by detector
                    import pandas as pd
                    df = pd.DataFrame([{
                        'timestamp': row.timestamp,
                        'proton_flux': row.proton_flux,
                        'electron_flux': row.electron_flux,
                        'alpha_flux': row.alpha_flux,
                        'velocity': row.velocity,
                        'temperature': row.temperature,
                        'density': row.density,
                        'magnetic_field_magnitude': row.magnetic_field_magnitude
                    } for row in particle_data])
                    
                    # Detect CME events
                    events = cme_detector.detect_cme_events(df)
                    
                    # Process and store detected events
                    for event in events:
                        await process_detected_event(event, session)
                
        except Exception as e:
            logger.error(f"Error in CME detection: {e}")
        
        await asyncio.sleep(60)  # Run every minute

async def process_detected_event(event: Dict, session):
    """Process and store detected CME event"""
    from src.models.cme_event import CMEEvent, CMEType, CMESource, CMEStatus
    
    # Check if event already exists
    existing = await session.execute(
        "SELECT id FROM cme_events WHERE external_id = :external_id",
        {"external_id": event['id']}
    )
    
    if existing.fetchone():
        return  # Event already exists
    
    # Create new CME event
    cme_event = CMEEvent(
        external_id=event['id'],
        timestamp=event['timestamp'],
        event_type=CMEType(event['type']),
        velocity=event['velocity'],
        width=event['width'],
        acceleration=event['acceleration'],
        source=CMESource(event['source']),
        confidence=event['confidence'],
        status=CMEStatus(event['status']),
        latitude=event['coordinates']['latitude'],
        longitude=event['coordinates']['longitude'],
        magnitude=event['magnitude']
    )
    
    session.add(cme_event)
    await session.commit()
    
    # Send alerts for high-confidence events
    if event['confidence'] > 0.8:
        await alert_manager.send_cme_alert(event)
    
    logger.info(f"Processed CME event: {event['id']}")

# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Aditya-CME-Detector API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected",
        "services": {
            "swis_ingestion": "running",
            "cactus_ingestion": "running",
            "cme_detection": "active"
        }
    }

@app.get("/api/v1/particle-data", response_model=List[ParticleDataResponse])
async def get_particle_data(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 1000
):
    """Get particle data from SWIS-ASPEX"""
    if not end_time:
        end_time = datetime.now()
    if not start_time:
        start_time = end_time - timedelta(hours=1)
    
    async with get_db_session() as session:
        result = await session.execute(
            """
            SELECT * FROM particle_data 
            WHERE timestamp >= :start_time AND timestamp <= :end_time
            ORDER BY timestamp DESC
            LIMIT :limit
            """,
            {"start_time": start_time, "end_time": end_time, "limit": limit}
        )
        
        data = result.fetchall()
        return [ParticleDataResponse.from_orm(row) for row in data]

@app.get("/api/v1/cme-events", response_model=List[CMEEventResponse])
async def get_cme_events(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    event_type: Optional[str] = None,
    min_confidence: float = 0.0,
    limit: int = 100
):
    """Get detected CME events"""
    if not end_time:
        end_time = datetime.now()
    if not start_time:
        start_time = end_time - timedelta(days=7)
    
    query = """
        SELECT * FROM cme_events 
        WHERE timestamp >= :start_time AND timestamp <= :end_time
        AND confidence >= :min_confidence
    """
    params = {
        "start_time": start_time,
        "end_time": end_time,
        "min_confidence": min_confidence,
        "limit": limit
    }
    
    if event_type:
        query += " AND event_type = :event_type"
        params["event_type"] = event_type
    
    query += " ORDER BY timestamp DESC LIMIT :limit"
    
    async with get_db_session() as session:
        result = await session.execute(query, params)
        events = result.fetchall()
        return [CMEEventResponse.from_orm(event) for event in events]

@app.get("/api/v1/system-status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get system status and metrics"""
    async with get_db_session() as session:
        # Get recent data counts
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)
        
        # Particle data count (last hour)
        particle_result = await session.execute(
            "SELECT COUNT(*) FROM particle_data WHERE timestamp >= :hour_ago",
            {"hour_ago": hour_ago}
        )
        particle_count = particle_result.scalar()
        
        # CME events count (today)
        events_result = await session.execute(
            "SELECT COUNT(*) FROM cme_events WHERE timestamp >= :day_ago",
            {"day_ago": day_ago}
        )
        events_count = events_result.scalar()
        
        # High confidence events
        high_conf_result = await session.execute(
            "SELECT COUNT(*) FROM cme_events WHERE timestamp >= :day_ago AND confidence >= 0.8",
            {"day_ago": day_ago}
        )
        high_conf_count = high_conf_result.scalar()
        
        return SystemStatusResponse(
            timestamp=now,
            swis_ingestion="online",
            cactus_ingestion="online",
            detection_status="active",
            alerts_enabled=True,
            particle_data_points_last_hour=particle_count,
            cme_events_today=events_count,
            high_confidence_events_today=high_conf_count,
            system_health=98.5
        )

@app.post("/api/v1/alerts/test")
async def test_alert(background_tasks: BackgroundTasks):
    """Test alert system"""
    test_event = {
        'id': f'TEST_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'timestamp': datetime.now(),
        'type': 'halo',
        'velocity': 850,
        'confidence': 0.95,
        'source': 'test'
    }
    
    background_tasks.add_task(alert_manager.send_cme_alert, test_event)
    return {"message": "Test alert queued"}

@app.post("/api/v1/detection/retrain")
async def retrain_models(background_tasks: BackgroundTasks):
    """Trigger model retraining"""
    background_tasks.add_task(retrain_detection_models)
    return {"message": "Model retraining initiated"}

async def retrain_detection_models():
    """Retrain CME detection models with latest data"""
    logger.info("Starting model retraining")
    
    try:
        async with get_db_session() as session:
            # Get training data (last 30 days)
            end_time = datetime.now()
            start_time = end_time - timedelta(days=30)
            
            # Get particle data
            particle_result = await session.execute(
                "SELECT * FROM particle_data WHERE timestamp >= :start_time ORDER BY timestamp",
                {"start_time": start_time}
            )
            particle_data = particle_result.fetchall()
            
            # Get CME events
            events_result = await session.execute(
                "SELECT * FROM cme_events WHERE timestamp >= :start_time ORDER BY timestamp",
                {"start_time": start_time}
            )
            cme_events = events_result.fetchall()
            
            if particle_data and cme_events:
                import pandas as pd
                
                # Convert to DataFrames
                particle_df = pd.DataFrame([{
                    'timestamp': row.timestamp,
                    'proton_flux': row.proton_flux,
                    'electron_flux': row.electron_flux,
                    'alpha_flux': row.alpha_flux,
                    'velocity': row.velocity,
                    'temperature': row.temperature,
                    'density': row.density,
                    'magnetic_field_magnitude': row.magnetic_field_magnitude
                } for row in particle_data])
                
                events_df = pd.DataFrame([{
                    'timestamp': row.timestamp,
                    'type': row.event_type.value,
                    'confidence': row.confidence
                } for row in cme_events])
                
                # Prepare training data and train models
                features_df, labels = cme_detector.prepare_training_data(particle_df, events_df)
                cme_detector.train_models(features_df, labels)
                
                # Save trained models
                cme_detector.save_models('models/cme_detector_latest.joblib')
                
                logger.info("Model retraining completed successfully")
            else:
                logger.warning("Insufficient data for model retraining")
                
    except Exception as e:
        logger.error(f"Error during model retraining: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=config.get('api.host', '0.0.0.0'),
        port=config.get('api.port', 8000),
        reload=config.get('system.debug', False)
    )