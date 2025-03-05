# src/data_loader.py
import pandas as pd
import streamlit as st
import logging
from typing import Optional
import os
from pathlib import Path

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
        # Get the absolute path to the data file
        root_dir = Path(__file__).parent.parent
        data_path = os.path.join(root_dir, 'data', 'all_cities_aqi_combined.csv')
        
        # Add debug information
        st.write(f"Current working directory: {os.getcwd()}")
        st.write(f"Attempting to load from: {data_path}")
        st.write(f"File exists: {os.path.exists(data_path)}")
        
        if not os.path.exists(data_path):
            # Try relative path as fallback
            data_path = 'data/all_cities_aqi_combined.csv'
            if not os.path.exists(data_path):
                raise FileNotFoundError(f"Data file not found in either location")
        
        df = pd.read_csv(data_path, parse_dates=['Timestamp'])
        
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
        
        # Add time components
        df['Day'] = df['Timestamp'].dt.day_name()
        df['Month'] = df['Timestamp'].dt.month
        df['Year'] = df['Timestamp'].dt.year
        
        if df.empty:
            raise DataValidationError("No valid data after preprocessing")
            
        return df
        
    except Exception as e:
        logger.error(f"Data loading error: {str(e)}")
        st.error(f"Error loading data: {str(e)}")
        return None
