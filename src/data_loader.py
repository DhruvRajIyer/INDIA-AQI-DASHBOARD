# src/data_loader.py
import pandas as pd
import streamlit as st
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DataValidationError(Exception):
    pass

def calculate_aqi(pm25: float) -> float:
    """Calculate AQI from PM2.5 values using EPA standards"""
    aqi_breakpoints = [
        (0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.4, 301, 500)
    ]
    
    for low_pm25, high_pm25, low_aqi, high_aqi in aqi_breakpoints:
        if low_pm25 <= pm25 <= high_pm25:
            return ((high_aqi - low_aqi) / (high_pm25 - low_pm25) * (pm25 - low_pm25) + low_aqi)
    return 500

@st.cache_data(ttl=3600)
def load_data() -> Optional[pd.DataFrame]:
    """Load and preprocess data with enhanced validation"""
    try:
        df = pd.read_csv('data/all_cities_aqi_combined.csv', parse_dates=['Timestamp'])
        
        # Validation
        required_columns = ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'City', 'Timestamp']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise DataValidationError(f"Missing columns: {', '.join(missing_columns)}")
        
        # Enhanced preprocessing
        df['Timestamp'] = pd.to_datetime(df['Timestamp']).dt.tz_localize(None)
        df = df.dropna(subset=['PM2.5'])
        
        # Calculate AQI
        df['AQI'] = df['PM2.5'].apply(calculate_aqi)
        
        # Add health risk categories
        df['Risk_Category'] = pd.cut(
            df['AQI'],
            bins=[0, 50, 100, 150, 200, 300, 500],
            labels=['Good', 'Moderate', 'Unhealthy for Sensitive Groups', 
                   'Unhealthy', 'Very Unhealthy', 'Hazardous']
        )
        
        # Add time componentsr
        df['Day'] = df['Timestamp'].dt.day_name()
        df['Month'] = df['Timestamp'].dt.month
        df['Year'] = df['Timestamp'].dt.year
        
        if df.empty:
            raise DataValidationError("No valid data after preprocessing")
            
        return df
        
    except Exception as e:
        logger.error(f"Data loading error: {str(e)}")
        return None
