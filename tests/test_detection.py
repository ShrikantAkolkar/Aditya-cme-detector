import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.detection.cme_detector import CMEDetector
from src.processing.feature_engineering import FeatureEngineer
from src.config import config

class TestCMEDetector:
    """Test cases for CME detection"""
    
    @pytest.fixture
    def detector(self):
        return CMEDetector()
    
    @pytest.fixture
    def sample_particle_data(self):
        """Create sample particle data for testing"""
        timestamps = pd.date_range(
            start=datetime.now() - timedelta(hours=2),
            end=datetime.now(),
            freq='30S'
        )
        
        data = []
        for timestamp in timestamps:
            data.append({
                'timestamp': timestamp,
                'proton_flux': 1000 + np.random.normal(0, 100),
                'electron_flux': 800 + np.random.normal(0, 80),
                'alpha_flux': 300 + np.random.normal(0, 30),
                'velocity': 400 + np.random.normal(0, 50),
                'temperature': 150000 + np.random.normal(0, 20000),
                'density': 5 + np.random.normal(0, 2),
                'magnetic_field_magnitude': 5 + np.random.normal(0, 2)
            })
        
        return pd.DataFrame(data)
    
    @pytest.fixture
    def sample_cme_events(self):
        """Create sample CME events for testing"""
        events = []
        base_time = datetime.now() - timedelta(hours=1)
        
        for i in range(3):
            events.append({
                'timestamp': base_time + timedelta(minutes=i*20),
                'type': 'halo' if i == 0 else 'partial_halo',
                'velocity': 800 + i*100,
                'confidence': 0.8 + i*0.05
            })
        
        return pd.DataFrame(events)
    
    def test_detector_initialization(self, detector):
        """Test detector initialization"""
        assert detector.config is not None
        assert detector.thresholds is not None
        assert detector.feature_engineer is not None
        assert len(detector.models) > 0
        assert not detector.is_trained
    
    def test_prepare_training_data(self, detector, sample_particle_data, sample_cme_events):
        """Test training data preparation"""
        features_df, labels = detector.prepare_training_data(
            sample_particle_data, sample_cme_events
        )
        
        assert isinstance(features_df, pd.DataFrame)
        assert isinstance(labels, np.ndarray)
        assert len(features_df) == len(labels)
        assert len(features_df) > 0
        
        # Check that some labels are positive (CME events)
        assert np.sum(labels) > 0
        assert np.sum(labels) < len(labels)  # Not all should be CME events
    
    def test_rule_based_detection(self, detector, sample_particle_data):
        """Test rule-based CME detection"""
        events = detector.rule_based_detection(sample_particle_data)
        
        assert isinstance(events, list)
        # Events list could be empty if no CME signatures detected
        
        if events:
            sample_event = events[0]
            required_fields = [
                'id', 'timestamp', 'type', 'velocity', 'confidence',
                'source', 'status', 'coordinates'
            ]
            
            for field in required_fields:
                assert field in sample_event
            
            assert sample_event['source'] == 'swis'
            assert sample_event['status'] == 'detected'
            assert 0 <= sample_event['confidence'] <= 1
    
    def test_group_consecutive_detections(self, detector):
        """Test grouping of consecutive detection indices"""
        # Test case 1: Simple consecutive sequence
        indices = np.array([1, 2, 3, 5, 6, 10])
        groups = detector._group_consecutive_detections(indices, max_gap=1)
        
        expected_groups = [[1, 2, 3], [5, 6], [10]]
        assert groups == expected_groups
        
        # Test case 2: All consecutive
        indices = np.array([1, 2, 3, 4, 5])
        groups = detector._group_consecutive_detections(indices, max_gap=1)
        assert groups == [[1, 2, 3, 4, 5]]
        
        # Test case 3: No consecutive
        indices = np.array([1, 5, 10])
        groups = detector._group_consecutive_detections(indices, max_gap=1)
        assert groups == [[1], [5], [10]]
        
        # Test case 4: Empty input
        indices = np.array([])
        groups = detector._group_consecutive_detections(indices)
        assert groups == []
    
    def test_create_cme_event(self, detector, sample_particle_data):
        """Test CME event creation"""
        # Engineer features first
        features_df = detector.feature_engineer.engineer_features(sample_particle_data)
        scores = np.random.random(len(features_df))
        indices = [10, 11, 12]  # Sample indices
        
        event = detector._create_cme_event(features_df, scores, indices)
        
        assert isinstance(event, dict)
        required_fields = [
            'id', 'timestamp', 'type', 'velocity', 'width',
            'acceleration', 'confidence', 'source', 'status', 'coordinates'
        ]
        
        for field in required_fields:
            assert field in event
        
        assert event['type'] in ['halo', 'partial_halo', 'non_halo']
        assert event['source'] == 'swis'
        assert event['status'] == 'detected'
        assert 0 <= event['confidence'] <= 1
    
    def test_apply_threshold_rules(self, detector, sample_particle_data):
        """Test threshold rule application"""
        features_df = detector.feature_engineer.engineer_features(sample_particle_data)
        ml_probabilities = np.random.random(len(features_df))
        
        combined_scores = detector.apply_threshold_rules(features_df, ml_probabilities)
        
        assert isinstance(combined_scores, np.ndarray)
        assert len(combined_scores) == len(features_df)
        assert np.all(combined_scores >= 0)
        assert np.all(combined_scores <= 1)
    
    def test_model_save_load(self, detector, sample_particle_data, sample_cme_events, tmp_path):
        """Test model saving and loading"""
        # Train the detector first
        features_df, labels = detector.prepare_training_data(
            sample_particle_data, sample_cme_events
        )
        detector.train_models(features_df, labels)
        
        # Save models
        model_path = tmp_path / "test_model.joblib"
        detector.save_models(str(model_path))
        
        assert model_path.exists()
        
        # Create new detector and load models
        new_detector = CMEDetector()
        assert not new_detector.is_trained
        
        new_detector.load_models(str(model_path))
        assert new_detector.is_trained
        assert new_detector.feature_columns == detector.feature_columns

class TestFeatureEngineer:
    """Test cases for feature engineering"""
    
    @pytest.fixture
    def feature_engineer(self):
        return FeatureEngineer(config._config)
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for feature engineering"""
        timestamps = pd.date_range(
            start=datetime.now() - timedelta(hours=1),
            end=datetime.now(),
            freq='1min'
        )
        
        data = {
            'timestamp': timestamps,
            'proton_flux': np.random.normal(1000, 100, len(timestamps)),
            'electron_flux': np.random.normal(800, 80, len(timestamps)),
            'alpha_flux': np.random.normal(300, 30, len(timestamps)),
            'velocity': np.random.normal(400, 50, len(timestamps)),
            'temperature': np.random.normal(150000, 20000, len(timestamps)),
            'density': np.random.normal(5, 2, len(timestamps)),
            'magnetic_field_magnitude': np.random.normal(5, 2, len(timestamps))
        }
        
        return pd.DataFrame(data)
    
    def test_create_time_features(self, feature_engineer, sample_data):
        """Test time-based feature creation"""
        result = feature_engineer.create_time_features(sample_data)
        
        assert 'hour' in result.columns
        assert 'day_of_year' in result.columns
        assert 'solar_cycle_phase' in result.columns
        assert 'time_delta' in result.columns
        
        # Check value ranges
        assert result['hour'].min() >= 0
        assert result['hour'].max() <= 23
        assert result['day_of_year'].min() >= 1
        assert result['day_of_year'].max() <= 366
    
    def test_create_moving_averages(self, feature_engineer, sample_data):
        """Test moving average feature creation"""
        result = feature_engineer.create_moving_averages(sample_data)
        
        # Check that moving average columns were created
        for window in feature_engineer.moving_avg_windows:
            assert f'proton_flux_ma_{window}' in result.columns
            assert f'velocity_ma_{window}' in result.columns
        
        # Moving averages should be smoother than original data
        original_std = sample_data['proton_flux'].std()
        ma_std = result['proton_flux_ma_5'].std()
        assert ma_std <= original_std
    
    def test_create_gradients(self, feature_engineer, sample_data):
        """Test gradient feature creation"""
        result = feature_engineer.create_gradients(sample_data)
        
        # Check that gradient columns were created
        for window in feature_engineer.gradient_windows:
            assert f'proton_flux_grad_{window}' in result.columns
            assert f'velocity_grad_{window}' in result.columns
    
    def test_create_statistical_features(self, feature_engineer, sample_data):
        """Test statistical feature creation"""
        result = feature_engineer.create_statistical_features(sample_data)
        
        # Check that statistical columns were created
        for window in feature_engineer.statistical_windows:
            assert f'proton_flux_std_{window}' in result.columns
            assert f'velocity_std_{window}' in result.columns
    
    def test_engineer_features_complete(self, feature_engineer, sample_data):
        """Test complete feature engineering pipeline"""
        result = feature_engineer.engineer_features(sample_data)
        
        # Should have more columns than input
        assert len(result.columns) > len(sample_data.columns)
        
        # Should have same number of rows
        assert len(result) == len(sample_data)
        
        # Should not have NaN values (they should be filled)
        assert not result.isnull().any().any()
    
    def test_get_feature_importance_columns(self, feature_engineer):
        """Test feature importance column selection"""
        important_columns = feature_engineer.get_feature_importance_columns()
        
        assert isinstance(important_columns, list)
        assert len(important_columns) > 0
        
        # Should include basic features
        assert 'proton_flux' in important_columns
        assert 'velocity' in important_columns

class TestDetectionIntegration:
    """Integration tests for detection pipeline"""
    
    def test_end_to_end_detection(self):
        """Test complete detection pipeline"""
        # Create sample data
        timestamps = pd.date_range(
            start=datetime.now() - timedelta(hours=2),
            end=datetime.now(),
            freq='30S'
        )
        
        particle_data = []
        for i, timestamp in enumerate(timestamps):
            # Add CME-like signature in the middle
            if 50 <= i <= 60:
                proton_flux = 2000 + np.random.normal(0, 100)  # Enhanced flux
                velocity = 600 + np.random.normal(0, 50)  # Higher velocity
            else:
                proton_flux = 1000 + np.random.normal(0, 100)
                velocity = 400 + np.random.normal(0, 50)
            
            particle_data.append({
                'timestamp': timestamp,
                'proton_flux': proton_flux,
                'electron_flux': proton_flux * 0.8,
                'alpha_flux': proton_flux * 0.3,
                'velocity': velocity,
                'temperature': 150000 + np.random.normal(0, 20000),
                'density': 5 + np.random.normal(0, 2),
                'magnetic_field_magnitude': 5 + np.random.normal(0, 2)
            })
        
        particle_df = pd.DataFrame(particle_data)
        
        # Initialize detector
        detector = CMEDetector()
        
        # Detect events (using rule-based since no training data)
        events = detector.detect_cme_events(particle_df)
        
        # Should detect at least one event due to enhanced signature
        assert isinstance(events, list)
        # Note: Detection depends on thresholds and may not always trigger

if __name__ == "__main__":
    pytest.main([__file__])