import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page configuration (must be the first Streamlit command)
st.set_page_config(
    page_title="Viral Content Analysis",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.streamlit.io/community',
        'Report a bug': "https://github.com/your-repo/issues",
        'About': "# Viral Content Analysis Dashboard\nAnalyze social media engagement trends."
    }
)

# Enhanced Custom styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    .stMetric:hover {
        transform: translateY(-5px);
    }
    .stSelectbox {
        border-radius: 0.5rem;
    }
    .plot-container {
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 1rem;
        background-color: white;
    }
    h1 {
        color: #1f77b4;
        font-weight: bold;
    }
    h2 {
        color: #2c3e50;
        margin-top: 2rem;
    }
    .stDataFrame {
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    </style>
""", unsafe_allow_html=True)

# Load dataset
@st.cache_data  # Add caching for better performance
def load_data():
    try:
        file_path = "../data/engineered_viral_trends.csv"
        if not os.path.exists(file_path):
            file_path = "./data/engineered_viral_trends.csv"
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.error("Dataset file not found. Please ensure the data file exists in the correct location.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading dataset: {str(e)}")
        st.stop()

df = load_data()

# Calculate key metrics
@st.cache_data
def calculate_metrics(df):
    return {
        'avg_engagement': df["Engagement_Score"].mean(),
        'highest_engagement_post': df.loc[df["Engagement_Score"].idxmax()],
        'total_posts': df.shape[0],
        'total_views': df['Views'].sum(),
        'avg_likes': df['Likes'].mean()
    }

metrics = calculate_metrics(df)

# Sidebar Navigation with custom styling
with st.sidebar:
    st.title("📊 Navigation")
    st.markdown("---")
    page = st.radio(
        "Select a Page",
        ["Overview", "Visualizations", "Model Performance"],
        format_func=lambda x: f"📈 {x}" if x == "Overview" else (f"🎯 {x}" if x == "Visualizations" else f"🤖 {x}")
    )
    
    st.markdown("---")
    st.markdown("### Filters")
    platform_filter = st.multiselect(
        "Filter by Platform",
        options=df['Platform'].unique(),
        default=df['Platform'].unique()
    )

# Filter data based on selection
filtered_df = df[df['Platform'].isin(platform_filter)]

# Overview Page
if page == "Overview":
    st.title("📊 Viral Content Trends Overview")
    
    # Key Metrics with animations
    st.markdown("### 📈 Key Performance Indicators")
    cols = st.columns(4)
    
    with cols[0]:
        st.metric("Total Posts", f"{metrics['total_posts']:,}", 
                 delta=f"{len(filtered_df)} selected")
    with cols[1]:
        st.metric("Average Engagement", f"{metrics['avg_engagement']:.4f}", 
                 delta=f"{(filtered_df['Engagement_Score'].mean() - metrics['avg_engagement']):.4f}")
    with cols[2]:
        st.metric("Total Views", f"{metrics['total_views']:,}", 
                 delta=f"{filtered_df['Views'].sum():,}")
    with cols[3]:
        st.metric("Average Likes", f"{metrics['avg_likes']:,.0f}", 
                 delta=f"{(filtered_df['Likes'].mean() - metrics['avg_likes']):,.0f}")
    
    # Interactive Platform Distribution
    st.markdown("### 📱 Platform Distribution")
    col1, col2 = st.columns(2)
    
    with col1:
        platform_dist = filtered_df["Platform"].value_counts()
        fig_platform = go.Figure(data=[go.Pie(
            labels=platform_dist.index,
            values=platform_dist.values,
            hole=.3,
            hovertemplate="Platform: %{label}<br>Posts: %{value}<br>Share: %{percent}<extra></extra>"
        )])
        fig_platform.update_layout(
            title="Content Distribution Across Platforms",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_platform, use_container_width=True)
    
    with col2:
        engagement_by_platform = filtered_df.groupby('Platform')['Engagement_Score'].mean().sort_values(ascending=True)
        fig_engagement = go.Figure(data=[go.Bar(
            x=engagement_by_platform.values,
            y=engagement_by_platform.index,
            orientation='h',
            marker_color='lightblue',
            hovertemplate="Engagement Score: %{x:.4f}<extra></extra>"
        )])
        fig_engagement.update_layout(
            title="Average Engagement by Platform",
            xaxis_title="Average Engagement Score",
            yaxis_title="Platform",
            showlegend=False
        )
        st.plotly_chart(fig_engagement, use_container_width=True)
    
    # Interactive Data Explorer
    st.markdown("### 🔍 Data Explorer")
    col_to_display = st.multiselect(
        "Select columns to display",
        options=df.columns.tolist(),
        default=['Post_ID', 'Platform', 'Content_Type', 'Engagement_Score', 'Views', 'Likes']
    )
    
    st.dataframe(
        filtered_df[col_to_display].style.background_gradient(subset=['Engagement_Score'], cmap='YlOrRd'),
        use_container_width=True,
        height=400
    )

# Visualization Page
elif page == "Visualizations":
    st.title("🎯 Interactive Data Visualizations")
    
    tabs = st.tabs(["Engagement Analysis", "Platform Insights", "Content Performance"])
    
    with tabs[0]:
        st.markdown("### 📊 Engagement Distribution")
        
        # Interactive visualization controls
        col1, col2 = st.columns(2)
        with col1:
            metric = st.selectbox(
                "Select Metric",
                ["Engagement_Score", "Views", "Likes", "Comments", "Shares"]
            )
        with col2:
            chart_type = st.selectbox(
                "Select Chart Type",
                ["Box Plot", "Violin Plot", "Distribution"]
            )
        
        if chart_type == "Distribution":
            fig = px.histogram(
                filtered_df,
                x=metric,
                color="Platform",
                marginal="box",
                opacity=0.7,
                title=f"Distribution of {metric}",
            )
        elif chart_type == "Box Plot":
            fig = px.box(
                filtered_df,
                x="Platform",
                y=metric,
                color="Platform",
                title=f"{metric} by Platform",
                points="all"
            )
        else:  # Violin Plot
            fig = px.violin(
                filtered_df,
                x="Platform",
                y=metric,
                color="Platform",
                title=f"{metric} Distribution by Platform",
                box=True,
                points="all"
            )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[1]:
        st.markdown("### 📱 Platform Performance Deep Dive")
        
        # Create metrics table
        platform_metrics = filtered_df.groupby("Platform").agg({
            "Engagement_Score": ["mean", "median", "std", "count"],
            "Views": "mean",
            "Likes": "mean"
        }).round(2)
        
        platform_metrics.columns = ["Avg Engagement", "Median Engagement", "Std Engagement", "Post Count", "Avg Views", "Avg Likes"]
        
        # Interactive correlation heatmap
        fig_corr = px.imshow(
            filtered_df[["Views", "Likes", "Comments", "Shares", "Engagement_Score"]].corr(),
            title="Correlation Matrix",
            color_continuous_scale="RdBu",
            aspect="auto"
        )
        st.plotly_chart(fig_corr, use_container_width=True)
        
        st.dataframe(platform_metrics, use_container_width=True)
    
    with tabs[2]:
        st.markdown("### 📝 Content Performance Analysis")
        
        # Time series analysis if timestamp is available
        content_metrics = filtered_df.groupby("Content_Type").agg({
            "Engagement_Score": ["mean", "count"],
            "Views": "mean",
            "Likes": "mean"
        }).round(2)
        
        content_metrics.columns = ["Avg Engagement", "Post Count", "Avg Views", "Avg Likes"]
        
        fig = make_subplots(rows=1, cols=2, specs=[[{"type": "bar"}, {"type": "pie"}]])
        
        fig.add_trace(
            go.Bar(
                x=content_metrics.index,
                y=content_metrics["Avg Engagement"],
                name="Avg Engagement",
                marker_color="lightblue"
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Pie(
                labels=content_metrics.index,
                values=content_metrics["Post Count"],
                name="Content Distribution"
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title="Content Type Performance Overview",
            showlegend=True,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(content_metrics, use_container_width=True)

# Model Performance Page
elif page == "Model Performance":
    st.title("🤖 Model Performance Analysis")
    
    # Create tabs for different analyses
    tabs = st.tabs(["Engagement Distribution", "Feature Analysis", "Platform Impact"])
    
    with tabs[0]:
        confusion_data = pd.crosstab(
            filtered_df["Engagement_Level"],
            filtered_df["Platform"],
            normalize="index"
        ) * 100
        
        fig = px.imshow(
            confusion_data,
            title="Platform vs Engagement Level Distribution (%)",
            color_continuous_scale="Viridis",
            aspect="auto",
            labels=dict(x="Platform", y="Engagement Level", color="Percentage")
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[1]:
        # Feature importance analysis
        features = ["Views", "Likes", "Shares", "Comments"]
        correlations = filtered_df[features + ["Engagement_Score"]].corr()["Engagement_Score"].drop("Engagement_Score")
        
        fig = go.Figure(data=[
            go.Bar(
                x=correlations.index,
                y=correlations.values,
                marker_color='lightblue',
                hovertemplate="Correlation: %{y:.4f}<extra></extra>"
            )
        ])
        
        fig.update_layout(
            title="Feature Correlation with Engagement Score",
            xaxis_title="Features",
            yaxis_title="Correlation Coefficient",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[2]:
        # Platform impact analysis
        platform_impact = filtered_df.groupby("Platform").agg({
            "Engagement_Score": ["mean", "std", "count"],
            "Views": "mean",
            "Likes": "mean"
        }).round(4)
        
        platform_impact.columns = ["Avg Engagement", "Std Engagement", "Post Count", "Avg Views", "Avg Likes"]
        st.dataframe(platform_impact, use_container_width=True)
        
        # Scatter plot of views vs engagement by platform
        fig = px.scatter(
            filtered_df,
            x="Views",
            y="Engagement_Score",
            color="Platform",
            size="Likes",
            hover_data=["Post_ID", "Content_Type"],
            title="Views vs Engagement Score by Platform",
            labels={"Views": "Number of Views", "Engagement_Score": "Engagement Score"},
            trendline="ols"
        )
        st.plotly_chart(fig, use_container_width=True)

# Add footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Made with ❤️ using Streamlit | Data last updated: 2024
    </div>
    """,
    unsafe_allow_html=True
)

