import pytest
import asyncio
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

from src.data_ingestion.swis_ingestion import SWISIngestion
from src.data_ingestion.cactus_ingestion import CACTUSIngestion

class TestSWISIngestion:
    """Test cases for SWIS data ingestion"""
    
    @pytest.fixture
    def swis_ingestion(self):
        return SWISIngestion()
    
    def test_init(self, swis_ingestion):
        """Test SWIS ingestion initialization"""
        assert swis_ingestion.endpoint is not None
        assert swis_ingestion.update_interval > 0
        assert swis_ingestion.timeout > 0
        assert swis_ingestion.retry_attempts > 0
    
    def test_simulate_particle_data(self, swis_ingestion):
        """Test particle data simulation"""
        duration_minutes = 60
        data = swis_ingestion.simulate_particle_data(duration_minutes)
        
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check data structure
        sample = data[0]
        required_fields = [
            'timestamp', 'proton_flux', 'electron_flux', 'alpha_flux',
            'velocity', 'temperature', 'density', 'magnetic_field'
        ]
        
        for field in required_fields:
            assert field in sample
        
        # Check magnetic field structure
        assert 'bx' in sample['magnetic_field']
        assert 'by' in sample['magnetic_field']
        assert 'bz' in sample['magnetic_field']
        assert 'magnitude' in sample['magnetic_field']
        
        # Check data types and ranges
        assert isinstance(sample['proton_flux'], (int, float))
        assert sample['proton_flux'] >= 0
        assert isinstance(sample['velocity'], (int, float))
        assert sample['velocity'] >= 200  # Minimum solar wind velocity
    
    @pytest.mark.asyncio
    async def test_fetch_particle_data_timeout(self, swis_ingestion):
        """Test fetch particle data with timeout"""
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now()
        
        # Mock session that times out
        mock_session = AsyncMock()
        mock_session.get.side_effect = asyncio.TimeoutError()
        
        swis_ingestion.session = mock_session
        
        data = await swis_ingestion.fetch_particle_data(start_time, end_time)
        assert data == []
    
    @pytest.mark.asyncio
    async def test_process_and_store_data(self, swis_ingestion):
        """Test data processing and storage"""
        # Create sample data
        raw_data = swis_ingestion.simulate_particle_data(duration_minutes=5)
        
        # Mock database session
        with patch('src.data_ingestion.swis_ingestion.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            count = await swis_ingestion.process_and_store_data(raw_data)
            
            assert count == len(raw_data)
            assert mock_session.add.call_count == len(raw_data)
            mock_session.commit.assert_called_once()

class TestCACTUSIngestion:
    """Test cases for CACTUS data ingestion"""
    
    @pytest.fixture
    def cactus_ingestion(self):
        return CACTUSIngestion()
    
    def test_init(self, cactus_ingestion):
        """Test CACTUS ingestion initialization"""
        assert cactus_ingestion.endpoint is not None
        assert cactus_ingestion.update_interval > 0
        assert cactus_ingestion.timeout > 0
        assert cactus_ingestion.retry_attempts > 0
    
    def test_simulate_cme_events(self, cactus_ingestion):
        """Test CME event simulation"""
        days = 7
        events = cactus_ingestion.simulate_cme_events(days)
        
        assert isinstance(events, list)
        assert len(events) >= 0  # Could be zero events
        
        if events:  # If events were generated
            sample = events[0]
            required_fields = [
                'id', 'timestamp', 'type', 'velocity', 'width',
                'position_angle', 'acceleration', 'source', 'confidence',
                'coordinates', 'magnitude'
            ]
            
            for field in required_fields:
                assert field in sample
            
            # Check CME type validity
            assert sample['type'] in ['halo', 'partial_halo', 'non_halo']
            
            # Check coordinate structure
            assert 'latitude' in sample['coordinates']
            assert 'longitude' in sample['coordinates']
            
            # Check data ranges
            assert 0 <= sample['confidence'] <= 1
            assert sample['velocity'] >= 200
            assert 0 <= sample['width'] <= 360
    
    @pytest.mark.asyncio
    async def test_fetch_cme_events_success(self, cactus_ingestion):
        """Test successful CME event fetching"""
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = [
            {
                'id': 'TEST_CME_001',
                'timestamp': datetime.now().isoformat(),
                'type': 'halo',
                'velocity': 800,
                'width': 360
            }
        ]
        
        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        cactus_ingestion.session = mock_session
        
        data = await cactus_ingestion.fetch_cme_events(start_date, end_date)
        assert len(data) == 1
        assert data[0]['id'] == 'TEST_CME_001'
    
    @pytest.mark.asyncio
    async def test_process_and_store_events(self, cactus_ingestion):
        """Test CME event processing and storage"""
        # Create sample events
        raw_events = cactus_ingestion.simulate_cme_events(days=1)
        
        if raw_events:  # Only test if events were generated
            # Mock database session
            with patch('src.data_ingestion.cactus_ingestion.get_db_session') as mock_db:
                mock_session = AsyncMock()
                mock_session.execute.return_value.fetchone.return_value = None  # No existing events
                mock_db.return_value.__aenter__.return_value = mock_session
                
                count = await cactus_ingestion.process_and_store_events(raw_events)
                
                assert count == len(raw_events)
                assert mock_session.add.call_count == len(raw_events)
                mock_session.commit.assert_called_once()

class TestIngestionIntegration:
    """Integration tests for data ingestion"""
    
    @pytest.mark.asyncio
    async def test_swis_context_manager(self):
        """Test SWIS ingestion context manager"""
        async with SWISIngestion() as ingestion:
            assert ingestion.session is not None
        
        # Session should be closed after context
        # Note: In real implementation, we'd check if session is closed
    
    @pytest.mark.asyncio
    async def test_cactus_context_manager(self):
        """Test CACTUS ingestion context manager"""
        async with CACTUSIngestion() as ingestion:
            assert ingestion.session is not None
    
    def test_data_consistency(self):
        """Test data consistency between ingestion modules"""
        swis_ingestion = SWISIngestion()
        cactus_ingestion = CACTUSIngestion()
        
        # Generate data
        particle_data = swis_ingestion.simulate_particle_data(duration_minutes=60)
        cme_events = cactus_ingestion.simulate_cme_events(days=1)
        
        # Check timestamp consistency
        if particle_data and cme_events:
            particle_times = [pd.to_datetime(item['timestamp']) for item in particle_data]
            cme_times = [pd.to_datetime(event['timestamp']) for event in cme_events]
            
            # All timestamps should be within reasonable range
            now = datetime.now()
            day_ago = now - timedelta(days=1)
            
            for time in particle_times:
                assert day_ago <= time <= now
            
            for time in cme_times:
                assert day_ago <= time <= now

if __name__ == "__main__":
    pytest.main([__file__])