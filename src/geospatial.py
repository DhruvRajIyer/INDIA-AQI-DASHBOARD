# src/geospatial.py
import folium
from folium import plugins
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd

def get_aqi_color(aqi):
    """Return color based on AQI value"""
    if aqi <= 50: return 'green'
    elif aqi <= 100: return 'yellow'
    elif aqi <= 150: return 'orange'
    elif aqi <= 200: return 'red'
    elif aqi <= 300: return 'purple'
    else: return 'maroon'

def create_map(df: pd.DataFrame):
    """Create a Folium map with AQI markers"""
    if df.empty:
        st.warning("No data available for map visualization.")
        return
        
    if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
        st.error("Geographical coordinates not found in the data.")
        return
        
    # Get latest data for each city
    latest_data = df.loc[df.groupby('City')['Timestamp'].idxmax()]
    
    # Create base map centered on mean coordinates
    center_lat = latest_data['Latitude'].mean()
    center_lon = latest_data['Longitude'].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=4)
    
    # Add markers for each city
    for _, row in latest_data.iterrows():
        color = get_aqi_color(row['AQI'])
        popup_text = f"""
            <b>{row['City']}</b><br>
            AQI: {row['AQI']:.1f}<br>
            PM2.5: {row.get('PM2.5', 'N/A')}<br>
            PM10: {row.get('PM10', 'N/A')}<br>
            Last Updated: {row['Timestamp']}
        """
        
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=10,
            popup=folium.Popup(popup_text, max_width=200),
            color=color,
            fill=True,
            fill_color=color
        ).add_to(m)
    
    # Add legend
    legend_html = (
        '<div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; '
        'background-color: white; padding: 10px; border: 2px solid grey; border-radius: 5px">'
        '<p><b>AQI Levels</b></p>'
        '<p><span style="color: green;">●</span> Good (0-50)</p>'
        '<p><span style="color: yellow;">●</span> Moderate (51-100)</p>'
        '<p><span style="color: orange;">●</span> Unhealthy for Sensitive Groups (101-150)</p>'
        '<p><span style="color: red;">●</span> Unhealthy (151-200)</p>'
        '<p><span style="color: purple;">●</span> Very Unhealthy (201-300)</p>'
        '<p><span style="color: maroon;">●</span> Hazardous (>300)</p>'
        '</div>'
    )

    m.get_root().html.add_child(folium.Element(legend_html))