import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import logging
from src.config import config
from src.processing.feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)

class CMEDetector:
    """AI-based CME detection system"""
    
    def __init__(self):
        self.config = config.get('detection', {})
        self.thresholds = self.config.get('thresholds', {})
        self.feature_engineer = FeatureEngineer(config._config)
        
        # Initialize models
        self.models = {
            'isolation_forest': IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            ),
            'svm': OneClassSVM(
                kernel='rbf',
                gamma='scale',
                nu=0.1
            ),
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                class_weight='balanced'
            )
        }
        
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = []
        
    def prepare_training_data(self, particle_df: pd.DataFrame, cme_events_df: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray]:
        """Prepare training data by labeling CME events"""
        logger.info("Preparing training data for CME detection")
        
        # Engineer features
        features_df = self.feature_engineer.engineer_features(particle_df)
        
        # Create labels based on CME events
        labels = np.zeros(len(features_df))
        
        for _, cme_event in cme_events_df.iterrows():
            cme_time = pd.to_datetime(cme_event['timestamp'])
            
            # Define time window around CME event (±30 minutes)
            start_time = cme_time - timedelta(minutes=30)
            end_time = cme_time + timedelta(minutes=30)
            
            # Mark data points within this window as CME events
            mask = (features_df['timestamp'] >= start_time) & (features_df['timestamp'] <= end_time)
            labels[mask] = 1
        
        logger.info(f"Created training data: {len(labels)} samples, {np.sum(labels)} CME events")
        return features_df, labels
    
    def train_models(self, features_df: pd.DataFrame, labels: np.ndarray):
        """Train all detection models"""
        logger.info("Training CME detection models")
        
        # Select important features
        self.feature_columns = self.feature_engineer.get_feature_importance_columns()
        available_columns = [col for col in self.feature_columns if col in features_df.columns]
        
        if not available_columns:
            raise ValueError("No feature columns available for training")
        
        X = features_df[available_columns].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train models
        for name, model in self.models.items():
            logger.info(f"Training {name} model")
            
            if name == 'random_forest':
                # Supervised learning - needs labels
                model.fit(X_scaled, labels)
            else:
                # Unsupervised anomaly detection - train on normal data
                normal_data = X_scaled[labels == 0]
                if len(normal_data) > 0:
                    model.fit(normal_data)
                else:
                    logger.warning(f"No normal data available for {name}")
        
        self.is_trained = True
        logger.info("Model training completed")
    
    def predict_cme_probability(self, features_df: pd.DataFrame) -> np.ndarray:
        """Predict CME probability using ensemble of models"""
        if not self.is_trained:
            raise ValueError("Models must be trained before prediction")
        
        available_columns = [col for col in self.feature_columns if col in features_df.columns]
        X = features_df[available_columns].values
        X_scaled = self.scaler.transform(X)
        
        predictions = []
        
        for name, model in self.models.items():
            if name == 'random_forest':
                # Get probability of CME class
                prob = model.predict_proba(X_scaled)[:, 1] if hasattr(model, 'predict_proba') else model.predict(X_scaled)
            else:
                # Convert anomaly scores to probabilities
                scores = model.decision_function(X_scaled)
                # Normalize scores to [0, 1] range
                prob = (scores - scores.min()) / (scores.max() - scores.min() + 1e-6)
                # Invert for anomaly detection (higher score = more anomalous)
                prob = 1 - prob
            
            predictions.append(prob)
        
        # Ensemble prediction (average)
        ensemble_prob = np.mean(predictions, axis=0)
        return ensemble_prob
    
    def apply_threshold_rules(self, features_df: pd.DataFrame, ml_probabilities: np.ndarray) -> np.ndarray:
        """Apply rule-based thresholds in addition to ML predictions"""
        
        # Rule-based detection criteria
        velocity_threshold = self.thresholds.get('velocity_threshold', 500)
        flux_threshold = self.thresholds.get('flux_threshold', 1200)
        temperature_threshold = self.thresholds.get('temperature_threshold', 200000)
        magnetic_field_threshold = self.thresholds.get('magnetic_field_threshold', 10)
        
        rule_based_scores = np.zeros(len(features_df))
        
        # Velocity criterion
        if 'velocity' in features_df.columns:
            velocity_score = np.where(features_df['velocity'] > velocity_threshold, 0.3, 0)
            rule_based_scores += velocity_score
        
        # Flux criterion
        if 'proton_flux' in features_df.columns:
            flux_score = np.where(features_df['proton_flux'] > flux_threshold, 0.3, 0)
            rule_based_scores += flux_score
        
        # Temperature criterion
        if 'temperature' in features_df.columns:
            temp_score = np.where(features_df['temperature'] > temperature_threshold, 0.2, 0)
            rule_based_scores += temp_score
        
        # Magnetic field criterion
        if 'magnetic_field_magnitude' in features_df.columns:
            mag_score = np.where(features_df['magnetic_field_magnitude'] > magnetic_field_threshold, 0.2, 0)
            rule_based_scores += mag_score
        
        # Combine ML and rule-based scores
        combined_scores = 0.7 * ml_probabilities + 0.3 * rule_based_scores
        return np.clip(combined_scores, 0, 1)
    
    def detect_cme_events(self, particle_df: pd.DataFrame) -> List[Dict]:
        """Detect CME events in particle data"""
        if not self.is_trained:
            logger.warning("Models not trained. Using rule-based detection only.")
            return self.rule_based_detection(particle_df)
        
        logger.info(f"Detecting CME events in {len(particle_df)} data points")
        
        # Engineer features
        features_df = self.feature_engineer.engineer_features(particle_df)
        
        # Get ML predictions
        ml_probabilities = self.predict_cme_probability(features_df)
        
        # Apply threshold rules
        final_scores = self.apply_threshold_rules(features_df, ml_probabilities)
        
        # Identify CME events
        confidence_threshold = self.thresholds.get('confidence_threshold', 0.7)
        cme_mask = final_scores > confidence_threshold
        
        # Extract events
        events = []
        if np.any(cme_mask):
            cme_indices = np.where(cme_mask)[0]
            
            # Group consecutive detections
            event_groups = self._group_consecutive_detections(cme_indices)
            
            for group in event_groups:
                event_data = self._create_cme_event(features_df, final_scores, group)
                events.append(event_data)
        
        logger.info(f"Detected {len(events)} CME events")
        return events
    
    def rule_based_detection(self, particle_df: pd.DataFrame) -> List[Dict]:
        """Fallback rule-based CME detection"""
        logger.info("Using rule-based CME detection")
        
        features_df = self.feature_engineer.engineer_features(particle_df)
        
        # Simple rule-based criteria
        velocity_threshold = self.thresholds.get('velocity_threshold', 500)
        flux_threshold = self.thresholds.get('flux_threshold', 1200)
        
        cme_mask = (
            (features_df.get('velocity', 0) > velocity_threshold) &
            (features_df.get('proton_flux', 0) > flux_threshold)
        )
        
        events = []
        if np.any(cme_mask):
            cme_indices = np.where(cme_mask)[0]
            event_groups = self._group_consecutive_detections(cme_indices)
            
            for group in event_groups:
                event_data = self._create_cme_event(features_df, np.ones(len(features_df)) * 0.8, group)
                events.append(event_data)
        
        return events
    
    def _group_consecutive_detections(self, indices: np.ndarray, max_gap: int = 10) -> List[List[int]]:
        """Group consecutive detection indices"""
        if len(indices) == 0:
            return []
        
        groups = []
        current_group = [indices[0]]
        
        for i in range(1, len(indices)):
            if indices[i] - indices[i-1] <= max_gap:
                current_group.append(indices[i])
            else:
                groups.append(current_group)
                current_group = [indices[i]]
        
        groups.append(current_group)
        return groups
    
    def _create_cme_event(self, features_df: pd.DataFrame, scores: np.ndarray, indices: List[int]) -> Dict:
        """Create CME event dictionary from detection indices"""
        
        # Get peak detection point
        peak_idx = indices[np.argmax(scores[indices])]
        peak_data = features_df.iloc[peak_idx]
        
        # Calculate event characteristics
        velocity = peak_data.get('velocity', 400)
        proton_flux = peak_data.get('proton_flux', 1000)
        confidence = scores[peak_idx]
        
        # Estimate CME type based on characteristics
        if velocity > 800 and proton_flux > 2000:
            cme_type = 'halo'
            width = 360
        elif velocity > 600 and proton_flux > 1500:
            cme_type = 'partial_halo'
            width = np.random.uniform(120, 359)
        else:
            cme_type = 'non_halo'
            width = np.random.uniform(20, 119)
        
        return {
            'id': f'SWIS_{peak_data["timestamp"].strftime("%Y%m%d_%H%M%S")}',
            'timestamp': peak_data['timestamp'],
            'type': cme_type,
            'velocity': velocity,
            'width': width,
            'acceleration': np.random.normal(-5, 10),
            'confidence': confidence,
            'source': 'swis',
            'status': 'detected',
            'coordinates': {
                'latitude': np.random.uniform(-90, 90),
                'longitude': np.random.uniform(-180, 180)
            },
            'magnitude': min(10, velocity / 100)
        }
    
    def save_models(self, filepath: str):
        """Save trained models to disk"""
        if not self.is_trained:
            raise ValueError("No trained models to save")
        
        model_data = {
            'models': self.models,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'config': self.config
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Models saved to {filepath}")
    
    def load_models(self, filepath: str):
        """Load trained models from disk"""
        model_data = joblib.load(filepath)
        
        self.models = model_data['models']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        self.is_trained = True
        
        logger.info(f"Models loaded from {filepath}")