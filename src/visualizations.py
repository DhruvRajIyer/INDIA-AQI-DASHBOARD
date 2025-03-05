import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Optional
import pandas as pd
import streamlit as st

def create_temporal_plots(temporal_data: Dict[str, pd.DataFrame]) -> Dict[str, go.Figure]:
    """Create temporal visualization plots"""
    plots = {}
    
    try:
        if 'hourly' in temporal_data and not temporal_data['hourly'].empty:
            daily_fig = px.line(
                temporal_data['hourly'],
                x='hour', 
                y='AQI',
                color='City',
                title='24-Hour Pollution Pattern'
            )
            plots['daily'] = daily_fig
            
        if 'daily' in temporal_data and not temporal_data['daily'].empty:
            # Ensure correct day order
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                        'Friday', 'Saturday', 'Sunday']
            temporal_data['daily']['day'] = pd.Categorical(
                temporal_data['daily']['day'],
                categories=day_order,
                ordered=True
            )
            weekly_fig = px.bar(
                temporal_data['daily'].sort_values('day'),
                x='day',
                y='AQI',
                color='City',
                title='Weekly Pollution Pattern'
            )
            plots['weekly'] = weekly_fig
            
        return plots
        
    except Exception as e:
        st.error(f"Error creating plots: {str(e)}")
        return {}

def display_plots(plots: Dict[str, go.Figure]):
    """Display plots with error handling"""
    if not plots:
        st.warning("No plots available to display")
        return
        
    for name, fig in plots.items():
        try:
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error displaying {name} plot: {str(e)}")