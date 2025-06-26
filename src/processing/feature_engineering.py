import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from scipy import signal
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)

class FeatureEngineer:
    """Feature engineering for CME detection"""
    
    def __init__(self, config: Dict):
        self.moving_avg_windows = config.get('detection.features.moving_average_windows', [5, 10, 30, 60])
        self.gradient_windows = config.get('detection.features.gradient_windows', [1, 5, 15])
        self.statistical_windows = config.get('detection.features.statistical_windows', [60, 180, 360])
        self.scaler = StandardScaler()
        
    def create_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create time-based features"""
        df = df.copy()
        
        # Extract time components
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_year'] = df['timestamp'].dt.dayofyear
        df['solar_cycle_phase'] = np.sin(2 * np.pi * df['day_of_year'] / 365.25)
        
        # Time since last measurement
        df['time_delta'] = df['timestamp'].diff().dt.total_seconds().fillna(0)
        
        return df
    
    def create_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create moving average features"""
        df = df.copy()
        
        for window in self.moving_avg_windows:
            window_str = f'{window}min'
            
            # Particle flux moving averages
            df[f'proton_flux_ma_{window}'] = df['proton_flux'].rolling(
                window=window, min_periods=1
            ).mean()
            df[f'electron_flux_ma_{window}'] = df['electron_flux'].rolling(
                window=window, min_periods=1
            ).mean()
            df[f'alpha_flux_ma_{window}'] = df['alpha_flux'].rolling(
                window=window, min_periods=1
            ).mean()
            
            # Solar wind parameter moving averages
            df[f'velocity_ma_{window}'] = df['velocity'].rolling(
                window=window, min_periods=1
            ).mean()
            df[f'temperature_ma_{window}'] = df['temperature'].rolling(
                window=window, min_periods=1
            ).mean()
            df[f'magnetic_field_ma_{window}'] = df['magnetic_field_magnitude'].rolling(
                window=window, min_periods=1
            ).mean()
        
        return df
    
    def create_gradients(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create gradient/derivative features"""
        df = df.copy()
        
        for window in self.gradient_windows:
            # Particle flux gradients
            df[f'proton_flux_grad_{window}'] = df['proton_flux'].diff(periods=window)
            df[f'electron_flux_grad_{window}'] = df['electron_flux'].diff(periods=window)
            df[f'alpha_flux_grad_{window}'] = df['alpha_flux'].diff(periods=window)
            
            # Solar wind parameter gradients
            df[f'velocity_grad_{window}'] = df['velocity'].diff(periods=window)
            df[f'temperature_grad_{window}'] = df['temperature'].diff(periods=window)
            df[f'magnetic_field_grad_{window}'] = df['magnetic_field_magnitude'].diff(periods=window)
        
        return df
    
    def create_statistical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create statistical features over different time windows"""
        df = df.copy()
        
        for window in self.statistical_windows:
            # Standard deviations
            df[f'proton_flux_std_{window}'] = df['proton_flux'].rolling(
                window=window, min_periods=1
            ).std()
            df[f'velocity_std_{window}'] = df['velocity'].rolling(
                window=window, min_periods=1
            ).std()
            
            # Ratios and relative changes
            df[f'proton_electron_ratio_{window}'] = (
                df[f'proton_flux_ma_{min(self.moving_avg_windows)}'] / 
                (df[f'electron_flux_ma_{min(self.moving_avg_windows)}'] + 1e-6)
            )
            
            # Percentile features
            df[f'proton_flux_p95_{window}'] = df['proton_flux'].rolling(
                window=window, min_periods=1
            ).quantile(0.95)
            df[f'velocity_p95_{window}'] = df['velocity'].rolling(
                window=window, min_periods=1
            ).quantile(0.95)
        
        return df
    
    def create_spectral_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create frequency domain features"""
        df = df.copy()
        
        # Power spectral density features
        for column in ['proton_flux', 'velocity', 'magnetic_field_magnitude']:
            if len(df) >= 64:  # Minimum length for meaningful FFT
                # Compute power spectral density
                freqs, psd = signal.welch(df[column].fillna(df[column].mean()), 
                                        nperseg=min(64, len(df)//4))
                
                # Extract dominant frequency and power
                dominant_freq_idx = np.argmax(psd[1:]) + 1  # Skip DC component
                df[f'{column}_dominant_freq'] = freqs[dominant_freq_idx]
                df[f'{column}_dominant_power'] = psd[dominant_freq_idx]
                df[f'{column}_total_power'] = np.sum(psd)
            else:
                df[f'{column}_dominant_freq'] = 0
                df[f'{column}_dominant_power'] = 0
                df[f'{column}_total_power'] = 0
        
        return df
    
    def create_anomaly_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create anomaly detection features"""
        df = df.copy()
        
        # Z-scores for anomaly detection
        for column in ['proton_flux', 'electron_flux', 'alpha_flux', 'velocity', 'temperature']:
            rolling_mean = df[column].rolling(window=60, min_periods=1).mean()
            rolling_std = df[column].rolling(window=60, min_periods=1).std()
            df[f'{column}_zscore'] = (df[column] - rolling_mean) / (rolling_std + 1e-6)
        
        # Mahalanobis distance for multivariate anomalies
        flux_columns = ['proton_flux', 'electron_flux', 'alpha_flux']
        if len(df) > len(flux_columns):
            try:
                flux_data = df[flux_columns].fillna(df[flux_columns].mean())
                cov_matrix = np.cov(flux_data.T)
                inv_cov_matrix = np.linalg.pinv(cov_matrix)
                mean_vector = flux_data.mean().values
                
                mahal_distances = []
                for _, row in flux_data.iterrows():
                    diff = row.values - mean_vector
                    mahal_dist = np.sqrt(diff.T @ inv_cov_matrix @ diff)
                    mahal_distances.append(mahal_dist)
                
                df['flux_mahalanobis_distance'] = mahal_distances
            except:
                df['flux_mahalanobis_distance'] = 0
        else:
            df['flux_mahalanobis_distance'] = 0
        
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all feature engineering steps"""
        logger.info(f"Starting feature engineering on {len(df)} data points")
        
        # Ensure timestamp is datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Apply all feature engineering steps
        df = self.create_time_features(df)
        df = self.create_moving_averages(df)
        df = self.create_gradients(df)
        df = self.create_statistical_features(df)
        df = self.create_spectral_features(df)
        df = self.create_anomaly_features(df)
        
        # Fill NaN values
        df = df.fillna(method='bfill').fillna(method='ffill').fillna(0)
        
        logger.info(f"Feature engineering completed. Created {len(df.columns)} features")
        return df
    
    def get_feature_importance_columns(self) -> List[str]:
        """Get list of most important feature columns for CME detection"""
        return [
            'proton_flux', 'electron_flux', 'alpha_flux',
            'velocity', 'temperature', 'magnetic_field_magnitude',
            'proton_flux_ma_5', 'proton_flux_ma_10', 'proton_flux_ma_30',
            'velocity_ma_5', 'velocity_ma_10', 'velocity_ma_30',
            'proton_flux_grad_1', 'proton_flux_grad_5', 'velocity_grad_1',
            'proton_flux_std_60', 'velocity_std_60',
            'proton_flux_zscore', 'velocity_zscore',
            'flux_mahalanobis_distance',
            'proton_electron_ratio_60'
        ]