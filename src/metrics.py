# src/metrics.py
import pandas as pd
import streamlit as st

def display_current_metrics(df: pd.DataFrame):
    """Display current air quality metrics"""
    if df.empty:
        st.warning("No data available to display metrics.")
        return
        
    # Get the latest timestamp for each city
    latest_data = df.loc[df.groupby('City')['Timestamp'].idxmax()]
    
    if latest_data.empty:
        st.warning("No current metrics available.")
        return
    
    # Create three columns for metrics
    col1, col2, col3 = st.columns(3)
    
    try:
        # Worst affected city
        worst_city = latest_data.loc[latest_data['AQI'].idxmax()]
        with col1:
            st.metric(
                "Worst Affected City",
                worst_city['City'],
                f"AQI: {worst_city['AQI']:.1f}"
            )
        
        # Best air quality city
        best_city = latest_data.loc[latest_data['AQI'].idxmin()]
        with col2:
            st.metric(
                "Best Air Quality City",
                best_city['City'],
                f"AQI: {best_city['AQI']:.1f}"
            )
        
        # Average AQI across cities
        avg_aqi = latest_data['AQI'].mean()
        with col3:
            st.metric(
                "Average AQI",
                f"{avg_aqi:.1f}",
                "Across selected cities"
            )
    except Exception as e:
        st.error(f"Error calculating metrics: {str(e)}")