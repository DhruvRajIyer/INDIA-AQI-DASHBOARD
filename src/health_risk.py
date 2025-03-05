import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

def get_risk_category(aqi):
    """Determine health risk category based on AQI"""
    if aqi <= 50:
        return "Good", "#00e400", "Air quality is satisfactory, and air pollution poses little or no risk."
    elif aqi <= 100:
        return "Moderate", "#ffff00", "Acceptable air quality, but some pollutants may be moderate health concern for sensitive individuals."
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "#ff7e00", "Members of sensitive groups may experience health effects. General public less likely to be affected."
    elif aqi <= 200:
        return "Unhealthy", "#ff0000", "Everyone may begin to experience health effects. Sensitive groups may experience more serious effects."
    elif aqi <= 300:
        return "Very Unhealthy", "#8f3f97", "Health alert: The risk of health effects is increased for everyone."
    else:
        return "Hazardous", "#7e0023", "Health warning of emergency conditions. Entire population is likely to be affected."

def create_gauge_chart(aqi_value: float) -> go.Figure:
    """Create a gauge chart for AQI visualization"""
    category, color, _ = get_risk_category(aqi_value)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=aqi_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 500]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 50], 'color': "#00e400"},
                {'range': [51, 100], 'color': "#ffff00"},
                {'range': [101, 150], 'color': "#ff7e00"},
                {'range': [151, 200], 'color': "#ff0000"},
                {'range': [201, 300], 'color': "#8f3f97"},
                {'range': [301, 500], 'color': "#7e0023"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': aqi_value
            }
        },
        title={'text': f"Current AQI Level: {category}"}
    ))
    
    return fig

def create_historical_trend(df: pd.DataFrame, city: str) -> go.Figure:
    """Create an enhanced AQI trend visualization with adaptive moving averages"""
    # Data preparation
    city_data = df[df['City'] == city].copy()
    city_data['Timestamp'] = pd.to_datetime(city_data['Timestamp'])
    
    # Calculate date range span
    date_span = (city_data['Timestamp'].max() - city_data['Timestamp'].min()).days
    
    # Resample to daily data with aggregations
    daily_data = city_data.resample('D', on='Timestamp').agg({
        'AQI': ['min', 'max', 'mean']
    }).reset_index()
    daily_data.columns = ['Timestamp', 'AQI_min', 'AQI_max', 'AQI_mean']
    
    # Adaptive SMA calculation based on date range
    if date_span >= 365:
        ma_window = 30
        ma_label = '30-day Moving Average'
    else:
        ma_window = 7
        ma_label = '7-day Moving Average'
    
    daily_data['AQI_MA'] = daily_data['AQI_mean'].rolling(window=ma_window).mean()
    
    fig = go.Figure()
    
    # Add AQI category zones
    categories = [
        (0, 50, "#00e400", "Good"),
        (51, 100, "#ffff00", "Moderate"),
        (101, 150, "#ff7e00", "Unhealthy for Sensitive Groups"),
        (151, 200, "#ff0000", "Unhealthy"),
        (201, 300, "#8f3f97", "Very Unhealthy"),
        (301, 500, "#7e0023", "Hazardous")
    ]
    
    for start, end, color, name in categories:
        fig.add_hrect(
            y0=start, y1=end,
            fillcolor=color,
            opacity=0.2,
            line=dict(width=0),
            name=name,
            showlegend=True
        )
    
    # Add daily range area
    fig.add_trace(go.Scatter(
        x=daily_data['Timestamp'],
        y=daily_data['AQI_max'],
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_data['Timestamp'],
        y=daily_data['AQI_min'],
        mode='lines',
        fill='tonexty',
        fillcolor='rgba(0, 255, 255, 0.1)',
        line=dict(width=0),
        name='Daily Range',
        hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br>" +
                     "<b>Range</b>: %{y:.0f} - %{text:.0f}<br>" +
                     "<extra></extra>",
        text=daily_data['AQI_max']
    ))
    
    # Add moving average
    fig.add_trace(go.Scatter(
        x=daily_data['Timestamp'],
        y=daily_data['AQI_MA'],
        mode='lines',
        name=ma_label,
        line=dict(color='#ff47ff', width=2.5),
        hovertemplate=f"<b>Date</b>: %{{x|%Y-%m-%d}}<br>" +
                     f"<b>{ma_label}</b>: %{{y:.0f}}<br>" +
                     "<extra></extra>"
    ))
    
    # Layout updates
        # Layout updates
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(25,25,25,1)',
        paper_bgcolor='rgba(25,25,25,1)',
        title=dict(
            text=f"AQI Trend Analysis - {city}",
            font=dict(size=20, color='#ffffff'),
            x=0.5,
            y=0.95
        ),
        xaxis=dict(
            title="Date",
            title_font=dict(size=14, color='#ffffff'),
            tickfont=dict(size=12, color='#ffffff'),
            gridcolor='rgba(255,255,255,0.1)',
            showgrid=True,
            rangeslider=dict(visible=True),
            rangeselector=dict(
                buttons=list([
                    dict(count=7, label="1W", step="day", stepmode="backward"),
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all", label="All")
                ]),
                bgcolor='rgba(55,55,55,0.9)',
                font=dict(color='#ffffff'),
                activecolor='#00ffff',
                y=1.1
            )
        ),
        yaxis=dict(
            title="Air Quality Index (AQI)",
            title_font=dict(size=14, color='#ffffff'),
            tickfont=dict(size=12, color='#ffffff'),
            gridcolor='rgba(255,255,255,0.1)',
            showgrid=True,
            range=[0, max(500, daily_data['AQI_max'].max() * 1.1)]
        ),
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(0,0,0,0.8)',
            font=dict(color='#ffffff'),
            bordercolor='rgba(255,255,255,0.2)',
            borderwidth=1
        ),
        margin=dict(l=60, r=30, t=80, b=60)  # Reduced bottom margin since we removed explanation
    )
    
    return fig




def show_health_risk_assessment(df: pd.DataFrame):
    """Display enhanced health risk assessment with additional features"""
    if df.empty:
        st.warning("No data available for health risk assessment.")
        return
        
    st.write("## 🏥 Health Risk Assessment Dashboard")
    
    # Add health condition selector
    health_conditions = [
        "None",
        "Asthma",
        "Heart Disease",
        "Lung Disease",
        "Elderly",
        "Children",
        "Pregnant"
    ]
    
    with st.sidebar:
        st.write("### Personal Settings")
        selected_condition = st.multiselect(
            "Select Health Conditions",
            health_conditions
        )
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Current Status", "Historical Trends", "City Comparison"])
    
    # Get latest data for each city
    latest_data = df.loc[df.groupby('City')['Timestamp'].idxmax()]
    
    with tab1:
        st.write("### Current Air Quality Status")
        
        # Create columns for city cards
        cols = st.columns(3)
        
        # Track cities needing alerts
        alerts = []
        
        for idx, (_, row) in enumerate(latest_data.iterrows()):
            category, color, recommendation = get_risk_category(row['AQI'])
            
            # Check if alert needed
            if row['AQI'] > 150:
                alerts.append(f"⚠️ {row['City']}: {category} AQI level")
            
            with cols[idx % 3]:
                # Create gauge chart
                gauge_fig = create_gauge_chart(row['AQI'])
                st.plotly_chart(gauge_fig, use_container_width=True)
                
                st.markdown(
                    f"""
                    <div style="padding: 10px; border-radius: 5px; border: 1px solid {color};">
                    <h4>{row['City']}</h4>
                    <p style="color: {color};"><b>{category}</b></p>
                    <p><small>{recommendation}</small></p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        # Show alerts if any
        if alerts:
            st.error("### ⚠️ High Risk Alerts\n" + "\n".join(alerts))
        
        # Show personalized recommendations
        if selected_condition:
            st.info("### 👤 Personalized Recommendations")
            for condition in selected_condition:
                if condition == "Asthma":
                    st.write("- Keep rescue inhaler readily available")
                    st.write("- Monitor breathing patterns closely")
                elif condition in ["Heart Disease", "Lung Disease"]:
                    st.write("- Limit outdoor activities")
                    st.write("- Stay in air-conditioned environments")
                elif condition in ["Elderly", "Children", "Pregnant"]:
                    st.write("- Avoid prolonged outdoor exposure")
                    st.write("- Wear appropriate masks when outside")
    
    with tab2:
        st.write("### Historical AQI Trends")
        
        # Add city selector and date range
        selected_city = st.selectbox("Select City", df['City'].unique())
        
        # Create date range selector
        date_range = st.slider(
            "Select Date Range",
            min_value=df['Timestamp'].min().date(),
            max_value=df['Timestamp'].max().date(),
            value=(
                df['Timestamp'].max().date() - timedelta(days=30),
                df['Timestamp'].max().date()
            )
        )
        
        # Filter data and create trend chart
        mask = (
            (df['City'] == selected_city) &
            (pd.to_datetime(df['Timestamp']).dt.date >= date_range[0]) &
            (pd.to_datetime(df['Timestamp']).dt.date <= date_range[1])
        )
        filtered_df = df[mask]
        
        if not filtered_df.empty:
            trend_fig = create_historical_trend(filtered_df, selected_city)
            st.plotly_chart(trend_fig, use_container_width=True)
            
            # Add statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average AQI", f"{filtered_df['AQI'].mean():.1f}")
            with col2:
                st.metric("Maximum AQI", f"{filtered_df['AQI'].max():.1f}")
            with col3:
                st.metric("Minimum AQI", f"{filtered_df['AQI'].min():.1f}")
    
    with tab3:
        st.write("### City Comparison")
        
        # Create ranking
        ranking_df = latest_data.sort_values('AQI', ascending=False)
        
        # Show ranking table with color coding
        st.write("#### Current AQI Rankings")
        
        for _, row in ranking_df.iterrows():
            category, color, _ = get_risk_category(row['AQI'])
            st.markdown(
                f"""
                <div style="padding: 5px; margin: 2px; background-color: {color}30;">
                <b>{row['City']}</b>: {row['AQI']:.1f} ({category})
                </div>
                """,
                unsafe_allow_html=True
            )
    
    with st.expander("📊 How to Read This Chart", expanded=True):
                st.markdown("""
                ### Understanding Your Air Quality Chart

                **Chart Elements:**
                - Shaded Area: Shows the daily range between highest and lowest AQI values
                - Purple Line: Shows the trend over time
                  - 7-day moving average for periods less than 1 year
                  - 30-day moving average for periods of 1 year or more

                **AQI Categories:**
                🟢 0-50: Good - Air quality is satisfactory
                🟡 51-100: Moderate - Acceptable but may affect sensitive individuals
                🟠 101-150: Unhealthy for Sensitive Groups - Elderly/children may be affected
                🔴 151-200: Unhealthy - Everyone may experience health effects
                🟣 201-300: Very Unhealthy - Health warnings, avoid outdoor activities
                🟤 301+: Hazardous - Emergency conditions

                **Interactive Features:**
                - Use the range slider below the chart to zoom into specific time periods
                - Click and drag to zoom into specific areas
                - Use the buttons above the chart for preset time ranges
                """)

