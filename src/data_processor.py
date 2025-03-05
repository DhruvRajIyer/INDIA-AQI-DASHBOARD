# src/data_processor.py
import pandas as pd
from datetime import datetime
import logging
from typing import Dict, Optional, Union

logger = logging.getLogger(__name__)

def calculate_aqi(pm25: pd.Series) -> pd.Series:
    """Calculate AQI from PM2.5 values"""
    try:
        aqi = pd.cut(pm25,
                    bins=[0, 12, 35.4, 55.4, 150.4, 250.4, 500.4, float('inf')],
                    labels=[25, 50, 100, 150, 200, 300, 500])
        return aqi.astype(float)
    except Exception as e:
        logger.error(f"AQI calculation error: {str(e)}")
        return pd.Series(index=pm25.index)

def process_temporal_data(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Process temporal patterns"""
    try:
        # Verify AQI column exists
        if 'AQI' not in df.columns:
            logger.error("AQI column not found in dataframe")
            return {}
            
        # Add time features
        df = df.copy()
        df['hour'] = df['Timestamp'].dt.hour
        df['day'] = df['Timestamp'].dt.day_name()
        df['month'] = df['Timestamp'].dt.month
        df['season'] = pd.cut(df['Timestamp'].dt.month,
                            bins=[0,2,5,8,11,12],
                            labels=['Winter','Spring','Summer','Fall','Winter'],
                            ordered=False)
        
        # Aggregate data
        aggregations = {
            'hourly': df.groupby(['City', 'hour'])['AQI'].mean().reset_index(),
            'daily': df.groupby(['City', 'day'])['AQI'].mean().reset_index(),
            'seasonal': df.groupby(['City', 'season'])['AQI'].mean().reset_index()
        }
        
        return aggregations
        
    except Exception as e:
        logger.error(f"Temporal processing error: {str(e)}")
        return {}
