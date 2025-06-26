import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import time
import asyncio
import logging

# Configure page
st.set_page_config(
    page_title="Aditya-L1 CME Detector",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3730a3 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin-bottom: 1rem;
    }
    .alert-card {
        background: #fef2f2;
        border: 1px solid #fecaca;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .success-card {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = "http://localhost:8000"

@st.cache_data(ttl=30)  # Cache for 30 seconds
def fetch_particle_data(hours=1):
    """Fetch particle data from API"""
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        response = requests.get(
            f"{API_BASE_URL}/api/v1/particle-data",
            params={
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "limit": 1000
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data)
        else:
            st.error(f"Failed to fetch particle data: {response.status_code}")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error fetching particle data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)  # Cache for 1 minute
def fetch_cme_events(days=7):
    """Fetch CME events from API"""
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        response = requests.get(
            f"{API_BASE_URL}/api/v1/cme-events",
            params={
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "limit": 100
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data)
        else:
            st.error(f"Failed to fetch CME events: {response.status_code}")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error fetching CME events: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=30)
def fetch_system_status():
    """Fetch system status from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/system-status", timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch system status: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Error fetching system status: {e}")
        return None

def create_particle_flux_chart(df):
    """Create particle flux time series chart"""
    if df.empty:
        return go.Figure()
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Particle Flux', 'Solar Wind Parameters'),
        vertical_spacing=0.1
    )
    
    # Particle flux
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['proton_flux'],
            name='Proton Flux',
            line=dict(color='#3b82f6', width=2)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['electron_flux'],
            name='Electron Flux',
            line=dict(color='#10b981', width=2)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['alpha_flux'],
            name='Alpha Flux',
            line=dict(color='#f59e0b', width=2)
        ),
        row=1, col=1
    )
    
    # Solar wind velocity
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['velocity'],
            name='Velocity (km/s)',
            line=dict(color='#8b5cf6', width=2)
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=600,
        title="SWIS-ASPEX Real-time Data Stream",
        showlegend=True,
        template="plotly_white"
    )
    
    fig.update_xaxes(title_text="Time", row=2, col=1)
    fig.update_yaxes(title_text="Flux (particles/cm²/s)", row=1, col=1)
    fig.update_yaxes(title_text="Velocity (km/s)", row=2, col=1)
    
    return fig

def create_cme_events_chart(df):
    """Create CME events visualization"""
    if df.empty:
        return go.Figure()
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Create scatter plot
    fig = px.scatter(
        df,
        x='timestamp',
        y='velocity',
        size='confidence',
        color='event_type',
        hover_data=['external_id', 'width', 'magnitude'],
        title="Detected CME Events",
        labels={
            'velocity': 'Velocity (km/s)',
            'timestamp': 'Detection Time',
            'event_type': 'CME Type'
        }
    )
    
    fig.update_layout(
        height=400,
        template="plotly_white"
    )
    
    return fig

def main():
    """Main dashboard application"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🛰️ Aditya-L1 CME Detection System</h1>
        <p>Real-time Coronal Mass Ejection Monitoring Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🔧 Dashboard Controls")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto Refresh (30s)", value=True)
    
    # Time range selection
    time_range = st.sidebar.selectbox(
        "Data Time Range",
        ["1 hour", "6 hours", "24 hours", "7 days"],
        index=0
    )
    
    hours_map = {"1 hour": 1, "6 hours": 6, "24 hours": 24, "7 days": 168}
    selected_hours = hours_map[time_range]
    
    # Fetch system status
    system_status = fetch_system_status()
    
    if system_status:
        # System Status Section
        st.header("📊 System Status")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "System Health",
                f"{system_status['system_health']:.1f}%",
                delta=None
            )
        
        with col2:
            status_color = "🟢" if system_status['swis_ingestion'] == 'online' else "🔴"
            st.metric(
                "SWIS Ingestion",
                f"{status_color} {system_status['swis_ingestion'].title()}",
                delta=None
            )
        
        with col3:
            status_color = "🟢" if system_status['cactus_ingestion'] == 'online' else "🔴"
            st.metric(
                "CACTUS Ingestion",
                f"{status_color} {system_status['cactus_ingestion'].title()}",
                delta=None
            )
        
        with col4:
            st.metric(
                "CME Events Today",
                system_status['cme_events_today'],
                delta=system_status['high_confidence_events_today']
            )
    
    # Real-time Data Section
    st.header("📈 Real-time Particle Data")
    
    # Fetch and display particle data
    particle_df = fetch_particle_data(selected_hours)
    
    if not particle_df.empty:
        # Convert timestamp to datetime
        particle_df['timestamp'] = pd.to_datetime(particle_df['timestamp'])
        
        # Create and display chart
        particle_chart = create_particle_flux_chart(particle_df)
        st.plotly_chart(particle_chart, use_container_width=True)
        
        # Latest readings
        st.subheader("Latest Readings")
        latest = particle_df.iloc[-1]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Proton Flux",
                f"{latest['proton_flux']:.0f}",
                delta=None,
                help="particles/cm²/s"
            )
        
        with col2:
            st.metric(
                "Solar Wind Velocity",
                f"{latest['velocity']:.0f} km/s",
                delta=None
            )
        
        with col3:
            st.metric(
                "Temperature",
                f"{latest['temperature']/1000:.0f}K",
                delta=None,
                help="×1000 K"
            )
        
        with col4:
            st.metric(
                "Magnetic Field",
                f"{latest['magnetic_field_magnitude']:.1f} nT",
                delta=None
            )
    else:
        st.warning("No particle data available")
    
    # CME Events Section
    st.header("🚨 Detected CME Events")
    
    # Fetch and display CME events
    cme_df = fetch_cme_events(7)  # Last 7 days
    
    if not cme_df.empty:
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Events (7 days)", len(cme_df))
        
        with col2:
            halo_events = len(cme_df[cme_df['event_type'] == 'halo'])
            st.metric("Halo CMEs", halo_events)
        
        with col3:
            high_conf = len(cme_df[cme_df['confidence'] > 0.8])
            st.metric("High Confidence", high_conf)
        
        # Events chart
        cme_chart = create_cme_events_chart(cme_df)
        st.plotly_chart(cme_chart, use_container_width=True)
        
        # Recent events table
        st.subheader("Recent Events")
        
        # Format the dataframe for display
        display_df = cme_df.copy()
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        display_df['confidence'] = (display_df['confidence'] * 100).round(1).astype(str) + '%'
        display_df['velocity'] = display_df['velocity'].round(0).astype(int)
        
        # Select columns to display
        columns_to_show = ['external_id', 'timestamp', 'event_type', 'velocity', 'confidence', 'source']
        st.dataframe(
            display_df[columns_to_show].head(10),
            use_container_width=True,
            column_config={
                'external_id': 'Event ID',
                'timestamp': 'Detection Time',
                'event_type': 'Type',
                'velocity': 'Velocity (km/s)',
                'confidence': 'Confidence',
                'source': 'Source'
            }
        )
    else:
        st.info("No CME events detected in the last 7 days")
    
    # Alerts Section
    st.header("🔔 System Alerts")
    
    # Test alert button
    if st.button("Send Test Alert"):
        try:
            response = requests.post(f"{API_BASE_URL}/api/v1/alerts/test", timeout=10)
            if response.status_code == 200:
                st.success("Test alert sent successfully!")
            else:
                st.error(f"Failed to send test alert: {response.status_code}")
        except Exception as e:
            st.error(f"Error sending test alert: {e}")
    
    # Model retraining section
    st.header("🤖 AI Model Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Retrain Models"):
            try:
                response = requests.post(f"{API_BASE_URL}/api/v1/detection/retrain", timeout=10)
                if response.status_code == 200:
                    st.success("Model retraining initiated!")
                else:
                    st.error(f"Failed to initiate retraining: {response.status_code}")
            except Exception as e:
                st.error(f"Error initiating retraining: {e}")
    
    with col2:
        st.info("Models are automatically retrained daily with new data")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; font-size: 0.9em;">
        <p>Aditya-L1 CME Detection System v1.0.0 | Indian Space Research Organisation (ISRO)</p>
        <p>Real-time space weather monitoring for solar-terrestrial research</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(30)
        st.rerun()

if __name__ == "__main__":
    main()