import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

def create_correlation_heatmap(df: pd.DataFrame, pollutants: list) -> go.Figure:
    """Create an enhanced correlation heatmap with annotations"""
    corr_df = df[pollutants].corr()
    
    # Create heatmap with annotations
    fig = go.Figure(data=go.Heatmap(
        z=corr_df,
        x=pollutants,
        y=pollutants,
        colorscale='RdBu',
        zmin=-1,
        zmax=1,
        text=np.round(corr_df, 2),
        texttemplate='%{text}',
        textfont={"size": 12},
        showscale=True
    ))
    
    fig.update_layout(
        title="Correlation Matrix of Air Pollutants",
        title_x=0.5,
        width=600,
        height=500,
        xaxis_title="Pollutants",
        yaxis_title="Pollutants"
    )
    return fig

def calculate_regression_stats(x: pd.Series, y: pd.Series) -> dict:
    """Calculate regression statistics"""
    mask = ~(np.isnan(x) | np.isnan(y))
    if mask.sum() < 2:
        return None
        
    slope, intercept, r_value, p_value, std_err = stats.linregress(x[mask], y[mask])
    r_squared = r_value ** 2
    
    return {
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_squared,
        'p_value': p_value
    }

def show_correlation_analysis(df: pd.DataFrame):
    """Display enhanced correlation analysis between pollutants"""
    st.write("### 📊 Air Pollutant Correlation Analysis")
    
    # Define pollutants with proper subscripts
    pollutants = {
        'PM2.5': 'PM₂.₅',
        'PM10': 'PM₁₀',
        'NO2': 'NO₂',
        'SO2': 'SO₂',
        'CO': 'CO'
    }
    
    # Add explanation in expander
    with st.expander("ℹ️ Understanding Correlation Analysis"):
        st.write("""
        - **What is correlation?** Correlation measures how strongly two pollutants are related.
        - **Correlation values:**
            - +1: Perfect positive correlation (both increase together)
            - 0: No correlation
            - -1: Perfect negative correlation (one increases as other decreases)
        - **Color coding:**
            - Red: Positive correlation
            - Blue: Negative correlation
            - Darker colors indicate stronger relationships
        """)
    
    # Create tabs for different analyses
    tab1, tab2 = st.tabs(["Correlation Matrix", "Detailed Analysis"])
    
    with tab1:
        st.write("#### Correlation Matrix Heatmap")
        fig = create_correlation_heatmap(df, list(pollutants.keys()))
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.write("#### Pollutant Relationship Analysis")
        
        # Add filters
        col1, col2, col3 = st.columns(3)
        with col1:
            x_pollutant = st.selectbox(
                "Select X-axis pollutant",
                options=list(pollutants.keys()),
                format_func=lambda x: pollutants[x]
            )
        with col2:
            y_pollutant = st.selectbox(
                "Select Y-axis pollutant",
                options=list(pollutants.keys()),
                index=1,
                format_func=lambda x: pollutants[x]
            )
        with col3:
            selected_city = st.selectbox(
                "Select City",
                options=['All Cities'] + sorted(df['City'].unique().tolist())
            )
        
        # Filter data based on selection
        plot_df = df.copy()
        if selected_city != 'All Cities':
            plot_df = plot_df[plot_df['City'] == selected_city]
        
        # Create scatter plot with trend line
        scatter_fig = px.scatter(
            plot_df,
            x=x_pollutant,
            y=y_pollutant,
            color='City' if selected_city == 'All Cities' else None,
            title=f"Relationship between {pollutants[x_pollutant]} and {pollutants[y_pollutant]}",
            opacity=0.6,
            trendline="ols" if selected_city != 'All Cities' else None
        )
        
        # Calculate statistics
        stats = calculate_regression_stats(plot_df[x_pollutant], plot_df[y_pollutant])
        
        # Display plot and statistics
        st.plotly_chart(scatter_fig, use_container_width=True)
        
        if stats:
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "R² (Strength of Relationship)",
                    f"{stats['r_squared']:.3f}"
                )
            with col2:
                correlation = plot_df[[x_pollutant, y_pollutant]].corr().iloc[0,1]
                st.metric(
                    "Correlation Coefficient",
                    f"{correlation:.3f}"
                )
            
            # Add interpretation
            st.write("#### 📝 Interpretation")
            if abs(correlation) > 0.7:
                strength = "strong"
            elif abs(correlation) > 0.3:
                strength = "moderate"
            else:
                strength = "weak"
                
            st.write(f"""
            - There is a {strength} {'positive' if correlation > 0 else 'negative'} relationship between 
              {pollutants[x_pollutant]} and {pollutants[y_pollutant]}.
            - R² value of {stats['r_squared']:.3f} indicates that {(stats['r_squared']*100):.1f}% of the variation
              in {pollutants[y_pollutant]} can be explained by {pollutants[x_pollutant]}.
            """)
