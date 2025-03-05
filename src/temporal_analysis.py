import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from typing import Optional
import calendar

def prepare_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract temporal features from timestamp column"""
    if 'Timestamp' not in df.columns:  # Fixed capitalization
        return df
        
    df = df.copy()
    df['Date'] = pd.to_datetime(df['Timestamp']).dt.date
    df['Day'] = pd.to_datetime(df['Timestamp']).dt.day_name()
    df['Month'] = pd.to_datetime(df['Timestamp']).dt.month
    df['Year'] = pd.to_datetime(df['Timestamp']).dt.year
    return df

def create_daily_trend(df: pd.DataFrame) -> Optional[go.Figure]:
    """Create daily AQI trend visualization using line plot"""
    df = prepare_temporal_features(df)
    
    if df.empty or 'Day' not in df.columns or 'AQI' not in df.columns:
        return None
        
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                  'Friday', 'Saturday', 'Sunday']
    
    daily_data = df.groupby(['City', 'Day'])['AQI'].agg(['mean', 'std']).reset_index()
    daily_data['Day'] = pd.Categorical(daily_data['Day'], categories=days_order, ordered=True)
    
    fig = go.Figure()
    
    for city in daily_data['City'].unique():
        city_data = daily_data[daily_data['City'] == city].sort_values('Day')
        fig.add_trace(go.Scatter(
            x=city_data['Day'],
            y=city_data['mean'],
            name=city,
            mode='lines+markers',
            line=dict(width=2),
            error_y=dict(
                type='data',
                array=city_data['std'],
                visible=True,
                thickness=1.5,
                width=3
            )
        ))
    
    fig.update_layout(
        title='Daily AQI Patterns by City',
        xaxis_title='Day of Week',
        yaxis_title='Average AQI',
        hovermode='x unified',
        showlegend=True
    )
    return fig

def create_monthly_trend(df: pd.DataFrame) -> Optional[go.Figure]:
    """Create monthly AQI trend visualization"""
    df = prepare_temporal_features(df)
    
    if df.empty or 'Month' not in df.columns:
        return None
        
    monthly_data = df.groupby(['City', 'Month'])['AQI'].mean().reset_index()
    
    # Convert month numbers to names for better readability
    monthly_data['Month_Name'] = monthly_data['Month'].apply(lambda x: calendar.month_name[x])
    
    fig = px.line(
        monthly_data,
        x='Month',
        y='AQI',
        color='City',
        title='Monthly AQI Trends',
        labels={'Month': 'Month', 'AQI': 'Average AQI'}
    )
    
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            ticktext=monthly_data['Month_Name'].unique(),
            tickvals=monthly_data['Month'].unique(),
            title='Month'
        ),
        hovermode='x unified'
    )
    return fig

def create_yearly_trend(df: pd.DataFrame) -> Optional[go.Figure]:
    """Create yearly trend with rolling average"""
    df = prepare_temporal_features(df)
    
    if df.empty or 'Timestamp' not in df.columns:  # Fixed capitalization
        return None
        
    df_daily = df.set_index('Timestamp').groupby('City')['AQI'].resample('D').mean()
    df_rolling = df_daily.groupby('City').transform(
        lambda x: x.rolling(window=30, min_periods=1).mean()
    )
    
    fig = go.Figure()
    
    for city in df_daily.index.get_level_values(0).unique():
        city_data = df_daily[city].reset_index()
        city_rolling = df_rolling[city].reset_index()
        
        fig.add_trace(go.Scatter(
            x=city_data['Timestamp'],
            y=city_data['AQI'],
            name=f"{city} (Daily)",
            opacity=0.2,
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=city_rolling['Timestamp'],
            y=city_rolling['AQI'],
            name=f"{city} (30-day avg)",
            line=dict(width=3)
        ))
    
    fig.update_layout(
        title='Yearly AQI Trends with 30-day Rolling Average',
        xaxis_title='Date',
        yaxis_title='AQI',
        hovermode='x unified'
    )
    return fig

def show_temporal_analysis(df: pd.DataFrame):
    """Display temporal analysis visualizations with enhanced filtering"""
    st.subheader("📊 Temporal Analysis of Air Quality")
    
    if df.empty:
        st.warning("No data available for the selected filters.")
        return
    
    # Prepare temporal features
    df = prepare_temporal_features(df)
    
    analysis_type = st.radio(
        "Select Time Period",
        ["Daily", "Monthly", "Yearly"],
        horizontal=True
    )
    
    if analysis_type == "Daily":
        # Add year and month filters
        col1, col2 = st.columns(2)
        
        # Year selector
        available_years = sorted(df['Year'].unique())
        selected_year = col1.selectbox(
            "Select Year",
            options=available_years,
            index=len(available_years)-1  # Default to latest year
        )
        
        # Month selector - show only months with data for selected year
        available_months = sorted(df[df['Year'] == selected_year]['Month'].unique())
        selected_month = col2.selectbox(
            "Select Month",
            options=available_months,
            format_func=lambda x: calendar.month_name[x],
            index=len(available_months)-1  # Default to latest month
        )
        
        # Filter data based on selection
        filtered_df = df[
            (df['Year'] == selected_year) & 
            (df['Month'] == selected_month)
        ]
        
        if filtered_df.empty:
            st.warning(f"No data available for {calendar.month_name[selected_month]} {selected_year}")
        else:
            fig = create_daily_trend(filtered_df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                with st.expander("💡 Daily Pattern Analysis"):
                    st.write(f"""
                    - Line plot shows average AQI by day of week for {calendar.month_name[selected_month]} {selected_year}
                    - Error bands show variation in measurements
                    - Compare weekday vs weekend patterns
                    """)
                
    elif analysis_type == "Monthly":
        # Year selector for monthly trends
        available_years = sorted(df['Year'].unique())
        selected_year = st.selectbox(
            "Select Year",
            options=available_years,
            index=len(available_years)-1
        )
        
        # Filter data for selected year
        filtered_df = df[df['Year'] == selected_year]
        
        if filtered_df.empty:
            st.warning(f"No data available for year {selected_year}")
        else:
            fig = create_monthly_trend(filtered_df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                st.write(f"Monthly AQI trends for {selected_year}")
            
    else:  # Yearly
        fig = create_yearly_trend(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            with st.expander("💡 Yearly Trend Analysis"):
                st.write("""
                - Solid lines show 30-day rolling averages
                - Transparent lines show daily variations
                - Compare long-term trends across cities
                """)
