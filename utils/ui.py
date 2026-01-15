import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Tuple
from utils.consts import CATEGORY_DESCRIPTIONS

def setup_page_config():
    """Configure Streamlit page settings for professional appearance."""
    st.set_page_config(
        page_title="CryptoVenture M&A Scout",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for professional dark theme styling
    st.markdown("""
        <style>
        /* Main container styling */
        .main {
            background-color: #0e1117;
        }
        
        /* KPI Card styling */
        .kpi-card {
            background: linear-gradient(135deg, #1a1f2e 0%, #2d3548 100%);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #3d4f6f;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }
        
        .kpi-value {
            font-size: 2.2rem;
            font-weight: bold;
            color: #00d4ff;
            margin: 10px 0;
        }
        
        .kpi-label {
            font-size: 0.9rem;
            color: #8b9dc3;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Header styling */
        .main-header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: 800;
            text-align: center;
            margin-bottom: 10px;
        }
        
        .sub-header {
            color: #8b9dc3;
            text-align: center;
            font-size: 1.1rem;
            margin-bottom: 30px;
        }
        </style>
    """, unsafe_allow_html=True)


def render_header():
    """Render the main header and description."""
    st.markdown('<h1 class="main-header">🔍 CryptoVenture M&A Scout</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Web3 Deal Sourcing & Valuation Dashboard | '
        'Automated Protocol Screening for Investment & Acquisition Targets</p>',
        unsafe_allow_html=True
    )


def render_sidebar_filters(df: pd.DataFrame) -> Tuple[list, list, float]:
    """
    Render sidebar filters and return filter values.
    """
    st.sidebar.header("🎯 Filter Protocols")
    st.sidebar.markdown("---")
    
    # Category filter with descriptions
    categories = sorted(df['category'].dropna().unique().tolist())
    
    def format_cat_label(cat):
        desc = CATEGORY_DESCRIPTIONS.get(cat, "")
        if desc:
            # "Dexs - Decentralized..." -> "Dexs (Decentralized...)"
            parts = desc.split(" - ")
            if len(parts) > 0:
                full_name = parts[0]
                if full_name.lower() != cat.lower():
                    return f"{cat} ({full_name})"
        return cat

    selected_categories = st.sidebar.multiselect(
        "📊 Categories",
        options=categories,
        default=[],
        format_func=format_cat_label,
        help="Filter by protocol category"
    )
    
    # Show description for selected categories
    if selected_categories:
        st.sidebar.markdown("**Selected Categories:**")
        for cat in selected_categories:
            if cat in CATEGORY_DESCRIPTIONS:
                st.sidebar.caption(f"• {CATEGORY_DESCRIPTIONS[cat]}")
    
    # Chain filter
    chains = sorted(df['primary_chain'].dropna().unique().tolist())
    selected_chains = st.sidebar.multiselect(
        "⛓️ Chains",
        options=chains,
        default=[],
        help="Filter by primary blockchain where the protocol is deployed"
    )
    
    st.sidebar.markdown("---")
    max_tvl = df['tvl'].max()
    
    # Unit Selector
    tvl_unit = st.sidebar.radio("💰 TVL Unit", ["Millions ($M)", "Billions ($B)"], horizontal=True)
    
    # Configure scales based on unit
    if "Billions" in tvl_unit:
        multiplier = 1e9
        format_str = "$%.1fB"
        step_value = 0.1
        default_val = 1.0
    else:
        multiplier = 1e6
        format_str = "$%.0fM"
        step_value = 1.0
        default_val = 10.0
        
    max_value_scaled = float(max_tvl / multiplier)
    
    # Initialize session state
    if 'tvl_filter_value' not in st.session_state:
        st.session_state.tvl_filter_value = default_val
        st.session_state.tvl_unit_prev = tvl_unit

    # Handle Unit Switch Conversion
    if 'tvl_unit_prev' in st.session_state and st.session_state.tvl_unit_prev != tvl_unit:
        if "Billions" in tvl_unit: # Switched M -> B
            st.session_state.tvl_filter_value = st.session_state.tvl_filter_value / 1000.0
        else: # Switched B -> M
            st.session_state.tvl_filter_value = st.session_state.tvl_filter_value * 1000.0
        st.session_state.tvl_unit_prev = tvl_unit

    # Callbacks for sync
    def update_from_slider():
        st.session_state.tvl_filter_value = st.session_state.tvl_slider
        
    def update_from_input():
        st.session_state.tvl_filter_value = st.session_state.tvl_input
    
    # Ensure value is valid
    current_val = float(st.session_state.tvl_filter_value)
    
    col_slider, col_input = st.sidebar.columns([2, 1])
    
    with col_slider:
        st.slider(
            "Min TVL Value",
            min_value=0.0,
            max_value=max_value_scaled if max_value_scaled > 0 else 1000.0,
            value=current_val,
            step=step_value,
            format=format_str,
            key='tvl_slider',
            on_change=update_from_slider,
            help="Total Value Locked slider",
            label_visibility="collapsed"
        )
        
    with col_input:
        st.number_input(
            "Manual Input",
            min_value=0.0,
            max_value=max_value_scaled if max_value_scaled > 0 else 1000.0,
            value=current_val,
            step=step_value,
            key='tvl_input',
            on_change=update_from_input,
            label_visibility="collapsed"
        )
        
    # Calculate final filter value
    min_tvl = st.session_state.tvl_filter_value * multiplier
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "💡 **Tip**: Use filters strategically to find hidden gems. "
        "Start with specific categories and lower TVL thresholds."
    )
    
    return selected_categories, selected_chains, min_tvl


def apply_filters(df: pd.DataFrame, categories: list, chains: list, min_tvl: float) -> pd.DataFrame:
    """Apply sidebar filters to the dataframe."""
    filtered = df.copy()
    if categories:
        filtered = filtered[filtered['category'].isin(categories)]
    if chains:
        filtered = filtered[filtered['primary_chain'].isin(chains)]
    filtered = filtered[filtered['tvl'] >= min_tvl]
    return filtered


def render_kpi_cards(df: pd.DataFrame):
    """Render the KPI summary cards."""
    col1, col2, col3, col4 = st.columns(4)
    
    # Total Protocols
    with col1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Protocols Scanned</div>
                <div class="kpi-value">{len(df):,}</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Average Sector P/S
    if 'sector_median_ps' in df.columns and len(df) > 0:
        avg_ps = df['sector_median_ps'].iloc[0]
    else:
        valid_ps = df[(df['ps_ratio_calc'].notna()) & (df['ps_ratio_calc'] > 0) & (df['ps_ratio_calc'] < 1000)]
        avg_ps = valid_ps['ps_ratio_calc'].median() if len(valid_ps) > 0 else 10.0
    
    if pd.isna(avg_ps):
        avg_ps = 10.0
        
    with col2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Sector Median P/S</div>
                <div class="kpi-value">{avg_ps:.1f}x</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Total Revenue (24h)
    total_revenue = df['total24h'].sum()
    with col3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">24h Revenue (All)</div>
                <div class="kpi-value">${total_revenue/1e6:.1f}M</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Top Undervalued Pick
    valid_protocols = df[
        (df['upside_potential'] > 0) & 
        (df['annualized_revenue'] > 100000) &
        (df['venture_score'] > 50)
    ].sort_values('venture_score', ascending=False)
    
    top_pick = valid_protocols.iloc[0]['name'] if len(valid_protocols) > 0 else "N/A"
    with col4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Top Undervalued Pick</div>
                <div class="kpi-value" style="font-size: 1.4rem;">{top_pick}</div>
            </div>
        """, unsafe_allow_html=True)


def render_scatter_plot(df: pd.DataFrame):
    """Render interactive scatter plot."""
    st.subheader("📈 Valuation Landscape: P/S Ratio vs Revenue")
    
    plot_df = df[
        (df['ps_ratio_calc'].notna()) & 
        (df['ps_ratio_calc'] > 0) & 
        (df['ps_ratio_calc'] < 500) &
        (df['annualized_revenue'] > 0)
    ].copy()
    
    if len(plot_df) == 0:
        total_protocols = len(df)
        no_mcap = len(df[df['mcap'] <= 0])
        no_revenue = len(df[df['annualized_revenue'] <= 0])
        no_both = len(df[(df['mcap'] <= 0) & (df['annualized_revenue'] <= 0)])
        
        st.warning(
            f"⚠️ **No protocols with complete valuation data to display in scatter plot.**\n\n"
            f"Out of {total_protocols} protocol(s) in this selection:\n"
            f"- **{no_revenue}** have no revenue/fee data from DefiLlama\n"
            f"- **{no_mcap}** have no market cap data\n"
            f"- **{no_both}** are missing both"
        )
        return
    
    # Create scatter plot
    fig = px.scatter(
        plot_df,
        x='ps_ratio_calc',
        y='annualized_revenue',
        color='category',
        size='tvl',
        size_max=50,
        hover_name='name',
        hover_data={
            'ps_ratio_calc': ':.1f',
            'annualized_revenue': ':,.0f',
            'tvl': ':,.0f',
            'venture_score': ':.1f',
            'category': True
        },
        labels={
            'ps_ratio_calc': 'P/S Ratio',
            'annualized_revenue': 'Annualized Revenue ($)',
            'category': 'Category',
            'tvl': 'TVL ($)',
            'venture_score': 'Venture Score'
        },
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#8b9dc3'),
        legend=dict(orientation='h', y=1.02, x=1),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)', type='log', title='P/S Ratio (Log)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)', type='log', title='Annualized Revenue (Log)'),
        height=500
    )
    
    median_ps = df['sector_median_ps'].iloc[0] if len(df) > 0 else 10
    fig.add_vline(x=median_ps, line_dash="dash", line_color="#ffab00", annotation_text=f"Median: {median_ps:.1f}x")
    
    st.plotly_chart(fig, use_container_width=True)
    st.caption("💡 **Reading the Chart**: Protocols in the bottom-right may be undervalued.")





def render_additional_charts(df: pd.DataFrame):
    """Render additional market insight charts."""
    st.subheader("📊 Market Insights")
    col1, col2 = st.columns(2)
    
    with col1:
        top_tvl = df.nlargest(10, 'tvl').sort_values('tvl', ascending=True)
        fig_tvl = px.bar(
            top_tvl, 
            y='name', 
            x='tvl', 
            orientation='h', 
            title='Top 10 by TVL',
            color='revenue_trend',
            color_continuous_scale='RdYlGn',
            color_continuous_midpoint=0,
            range_color=[-50, 50],
            labels={'revenue_trend': 'Revenue Trend (%)'}
        )
        fig_tvl.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', showlegend=False, height=400)
        st.plotly_chart(fig_tvl, use_container_width=True)
        
    with col2:
        top_rev = df.nlargest(10, 'annualized_revenue').sort_values('annualized_revenue', ascending=True)
        fig_rev = px.bar(
            top_rev, 
            y='name', 
            x='annualized_revenue', 
            orientation='h', 
            title='Top 10 by Revenue',
            color='revenue_trend',
            color_continuous_scale='RdYlGn',
            color_continuous_midpoint=0,
            range_color=[-50, 50],
            labels={'revenue_trend': 'Revenue Trend (%)'}
        )
        fig_rev.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', showlegend=False, height=400)
        st.plotly_chart(fig_rev, use_container_width=True)

    # Category Distribution
    st.subheader("🥧 Market Composition")
    cat_tvl = df.groupby('category')['tvl'].sum().reset_index()
    fig_pie = px.pie(cat_tvl, values='tvl', names='category', title='TVL by Category', hole=0.4)
    fig_pie.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', height=400)
    st.plotly_chart(fig_pie, use_container_width=True)


def render_data_table(df: pd.DataFrame):
    """Render the sortable data table with key metrics."""
    st.subheader("📋 Protocol Valuation Table")
    
    display_cols = [
        'name', 'category', 'primary_chain', 'tvl', 'mcap',
        'annualized_revenue', 'ps_ratio_calc', 'sector_median_ps',
        'fair_value', 'upside_potential', 'venture_score'
    ]
    
    display_df = df[display_cols].copy()
    display_df.columns = [
        'Protocol', 'Category', 'Chain', 'TVL ($)', 'Market Cap ($)',
        'Annual Revenue ($)', 'P/S Ratio', 'Sector P/S', 
        'Fair Value ($)', 'Upside (%)', 'Venture Score'
    ]
    display_df = display_df.sort_values('Venture Score', ascending=False)
    
    st.dataframe(
        display_df,
        column_config={
            "Venture Score": st.column_config.ProgressColumn(
                "Venture Score", help="Investment score (0-100)", format="%.1f", min_value=0, max_value=100
            ),
        },
        hide_index=True,
        use_container_width=True,
        height=400
    )


def render_metric_explanations():
    """Render detailed explanations for the financial metrics used."""
    with st.expander("ℹ️ Guide: Understanding the Metrics"):
        st.markdown("""
        ### 📊 Financial Metrics Glossary
        **💰 TVL**: Total Value Locked...
        **💸 Annualized Revenue**: 30d Revenue * 12...
        **📉 P/S Ratio**: Mcap / Revenue...
        **🎯 Fair Value**: Revenue * Sector Median P/S...
        **🚀 Venture Score**: 0-100 score based on Valuation Gap, Revenue Trend, Efficiency.
        """)


def render_methodology():
    """Render the methodology explanation section."""
    with st.expander("📚 Methodology & Financial Logic"):
        st.markdown("""
        ### How We Calculate Valuations
        **1. Annualized Revenue**: 30-day revenue × 12
        **2. P/S Ratio**: Market Cap / Annualized Revenue
        **3. Venture Score (0-100)**: Composite of Valuation Gap, Trend, Efficiency.
        """)
