# app.py
import streamlit as st
from src.data_loader import load_data
from src.metrics import display_current_metrics
from src.correlation_analysis import show_correlation_analysis
from src.temporal_analysis import show_temporal_analysis
import logging
from src.geospatial import create_map
from src.health_risk import show_health_risk_assessment

logging.basicConfig(level=logging.INFO)

# app.py

def main():
    

    st.set_page_config(
        page_title="Enhanced Air Quality Analytics",
        layout="wide",
        page_icon="🌫️"
    )
    
    st.title("🌍 Air Quality Analytics Dashboard")
    
    # Load data
    df = load_data()
    if df is None or df.empty:
        st.error("Failed to load data. Please check the data source.")
        return
        
    # Sidebar filters
    st.sidebar.header("Filters")
    selected_cities = st.sidebar.multiselect(
        "Select Cities",
        options=sorted(df['City'].unique()),
        default=sorted(df['City'].unique())[:3]
    )

    st.markdown("""
    <style>
    @import url('/.streamlit/custom_theme.css');
    </style>
    """, unsafe_allow_html=True)

    def toggle_theme():
        current_bg = st.get_option("theme.backgroundColor")
        new_theme = "dark" if current_bg == "#FFFFFF" else "light"
        st.experimental_set_query_params(theme=new_theme)
        st.experimental_rerun()

    # Add button to sidebar
    with st.sidebar:
        st.button("Toggle Theme", on_click=toggle_theme)
    
    # Set min and max dates from data
    min_date = df['Timestamp'].min().date()
    max_date = df['Timestamp'].max().date()
    
    try:
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Handle single date selection
        if isinstance(date_range, tuple):
            start_date, end_date = date_range if len(date_range) == 2 else (date_range[0], date_range[0])
        else:
            start_date = end_date = date_range
            
    except Exception:
        start_date, end_date = min_date, max_date
        st.sidebar.warning("Using default date range due to invalid selection")
    
    # Filter data
    filtered_df = df[
        (df['City'].isin(selected_cities)) &
        (df['Timestamp'].dt.date >= start_date) &
        (df['Timestamp'].dt.date <= end_date)
    ]
    
    if filtered_df.empty:
        st.warning("No data available for the selected filters. Please adjust your selection.")
        return
        
    # Display metrics
    display_current_metrics(filtered_df)
    
    # Tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
    "Temporal Analysis", 
    "Correlation Analysis",
    "Geographic Visualization",
    "Health Risk Assessment"])
    
    with tab1:
        show_temporal_analysis(filtered_df)
        
    with tab2:
        st.header("🔄 Pollutant Correlations")
        show_correlation_analysis(filtered_df)
    with tab3:
        st.header("🗺️ Geographic Distribution")
        create_map(filtered_df)
    with tab4:
        show_health_risk_assessment(filtered_df)



if __name__ == "__main__":
    main()

