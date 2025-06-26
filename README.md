# Aditya-L1 CME Detection System

A comprehensive AI-based system for detecting Halo Coronal Mass Ejection (CME) events using particle data from the Aditya-L1 SWIS-ASPEX payload and CME timestamps from the CACTUS database.

## 🛰️ Overview

The Aditya-L1 CME Detection System is a real-time space weather monitoring solution designed to detect and analyze Coronal Mass Ejection events. The system combines machine learning algorithms with rule-based detection methods to provide accurate and timely CME alerts for space weather research and operational forecasting.

### Key Features

- **Real-time Data Ingestion**: Continuous monitoring of SWIS-ASPEX particle data and CACTUS CME events
- **AI-Powered Detection**: Ensemble machine learning models for accurate CME detection
- **Multi-threshold Optimization**: Adaptive threshold tuning for different CME types
- **Real-time Dashboard**: Interactive Streamlit dashboard for monitoring and visualization
- **Alert System**: SMS/Email notifications via Twilio integration
- **RESTful API**: FastAPI-based API for integration with external systems
- **Comprehensive Testing**: Unit and integration tests for reliable operation
- **Docker Support**: Containerized deployment for easy scaling

## 🏗️ Architecture

```
├── src/
│   ├── api/                    # FastAPI REST API
│   ├── data_ingestion/         # SWIS and CACTUS data ingestion
│   ├── processing/             # Feature engineering and preprocessing
│   ├── detection/              # CME detection algorithms
│   ├── alerts/                 # Alert management system
│   ├── dashboard/              # Streamlit dashboard
│   ├── models/                 # Database models
│   └── database/               # Database connection and management
├── notebooks/                  # Jupyter notebooks for analysis
├── tests/                      # Test suite
├── scripts/                    # Utility scripts
├── data/                       # Data storage
├── models/                     # Trained ML models
└── logs/                       # Application logs
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd aditya-cme-detector
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize the database**
   ```bash
   python scripts/setup_database.py
   ```

### Running the System

#### Option 1: Using Scripts

1. **Start the API server**
   ```bash
   python scripts/run_api.py
   ```

2. **Start the dashboard** (in a new terminal)
   ```bash
   python scripts/run_dashboard.py
   ```

3. **Access the applications**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Dashboard: http://localhost:8501

#### Option 2: Using Docker Compose

```bash
docker-compose up -d
```

This will start all services including PostgreSQL, Redis, API, dashboard, and background workers.

## 📊 Dashboard Features

The Streamlit dashboard provides:

- **System Status**: Real-time monitoring of ingestion and detection services
- **Particle Data Visualization**: Live charts of SWIS-ASPEX measurements
- **CME Event Timeline**: Interactive timeline of detected events
- **Alert Management**: Configuration and testing of alert systems
- **Model Performance**: Metrics and retraining controls

## 🔧 API Endpoints

### Core Endpoints

- `GET /health` - System health check
- `GET /api/v1/particle-data` - Retrieve particle data
- `GET /api/v1/cme-events` - Get detected CME events
- `GET /api/v1/system-status` - System status and metrics
- `POST /api/v1/alerts/test` - Send test alert
- `POST /api/v1/detection/retrain` - Trigger model retraining

### Example Usage

```python
import requests

# Get recent CME events
response = requests.get('http://localhost:8000/api/v1/cme-events')
events = response.json()

# Get system status
response = requests.get('http://localhost:8000/api/v1/system-status')
status = response.json()
```

## 🧪 Testing

Run the test suite:

```bash
python scripts/run_tests.py
```

Or using pytest directly:

```bash
pytest tests/ -v --cov=src
```

## 📓 Jupyter Notebooks

The system includes analysis notebooks:

1. **Data Exploration** (`notebooks/01_data_exploration.ipynb`)
   - Particle data analysis
   - CME event characteristics
   - Feature correlation analysis

2. **Threshold Optimization** (`notebooks/02_threshold_optimization.ipynb`)
   - Single and multi-parameter optimization
   - ROC and Precision-Recall analysis
   - False positive analysis

## ⚙️ Configuration

### Main Configuration (`config.yaml`)

```yaml
system:
  name: "Aditya-CME-Detector"
  version: "1.0.0"
  environment: "development"

data_sources:
  swis:
    endpoint: "https://api.aditya-l1.isro.gov.in/swis/aspex"
    update_interval: 30
  cactus:
    endpoint: "https://wwwbis.sidc.be/cactus/catalog/LASCO"
    update_interval: 3600

detection:
  thresholds:
    velocity_threshold: 500
    flux_threshold: 1200
    confidence_threshold: 0.7
```

### Environment Variables (`.env`)

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/cme_detector
REDIS_URL=redis://localhost:6379/0
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
EMAIL_HOST=smtp.gmail.com
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

## 🚨 Alert System

The system supports multiple alert channels:

### Email Alerts
- SMTP configuration for email notifications
- HTML formatted alerts with event details
- Configurable recipient lists

### SMS Alerts
- Twilio integration for SMS notifications
- Critical event notifications
- International number support

### Webhook Alerts
- HTTP POST notifications to external systems
- JSON payload with event data
- Configurable endpoints

## 🔬 Machine Learning Models

The detection system uses an ensemble approach:

1. **Isolation Forest**: Anomaly detection for unusual particle signatures
2. **One-Class SVM**: Support vector machine for outlier detection
3. **Random Forest**: Supervised classification with labeled CME events

### Model Training

Models are automatically retrained daily with new data. Manual retraining can be triggered via:

```bash
curl -X POST http://localhost:8000/api/v1/detection/retrain
```

## 📈 Performance Metrics

The system tracks:

- **Detection Accuracy**: Precision, Recall, F1-score
- **False Positive Rate**: Monitoring of incorrect detections
- **System Uptime**: Service availability metrics
- **Data Ingestion Rate**: Real-time data processing statistics

## 🐳 Docker Deployment

### Production Deployment

1. **Build and deploy**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Scale services**
   ```bash
   docker-compose up -d --scale api=3 --scale celery-worker=2
   ```

3. **Monitor logs**
   ```bash
   docker-compose logs -f api
   ```

## 🔒 Security Considerations

- Environment variables for sensitive configuration
- Database connection encryption
- API rate limiting
- Input validation and sanitization
- Secure alert channel configuration

## 📚 Documentation

- **API Documentation**: Available at `/docs` when running the API
- **Code Documentation**: Inline docstrings and type hints
- **Architecture Diagrams**: In the `docs/` directory
- **Deployment Guide**: Step-by-step deployment instructions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **ISRO**: For the Aditya-L1 mission and SWIS-ASPEX payload data
- **SIDC**: For the CACTUS CME detection database
- **Space Weather Community**: For research and validation support

## 📞 Support

For questions and support:

- **Issues**: GitHub Issues for bug reports and feature requests
- **Documentation**: Check the `/docs` endpoint for API documentation
- **Community**: Join the space weather research community discussions

---

**Aditya-L1 CME Detection System v1.0.0**  
*Real-time space weather monitoring for solar-terrestrial research*  
*Indian Space Research Organisation (ISRO)*