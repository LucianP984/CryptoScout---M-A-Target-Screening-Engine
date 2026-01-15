"""
CryptoVenture M&A Scout Dashboard
==================================
A professional Web3 M&A Deal Sourcing & Valuation Dashboard.
"""
import streamlit as st
import pandas as pd
from utils.data import fetch_protocols_data, fetch_fees_data, merge_datasets
from utils.metrics import calculate_financial_metrics, calculate_venture_score
from utils.ui import (
    setup_page_config, render_header, render_sidebar_filters, 
    apply_filters, render_kpi_cards, render_scatter_plot, 
    render_additional_charts, render_data_table, 
    render_metric_explanations, render_methodology
)

def main():
    # Setup
    setup_page_config()
    render_header()
    
    # Data loading
    with st.spinner("🔄 Fetching protocol data from DefiLlama..."):
        protocols_df = fetch_protocols_data()
        fees_df = fetch_fees_data()
    
    # Process data
    with st.spinner("⚙️ Processing financial metrics..."):
        merged_df = merge_datasets(protocols_df, fees_df)
        metrics_df = calculate_financial_metrics(merged_df)
        scored_df = calculate_venture_score(metrics_df)
    
    # Sidebar filters
    categories, chains, min_tvl = render_sidebar_filters(scored_df)
    
    # Apply filters
    filtered_df = apply_filters(scored_df, categories, chains, min_tvl)
    
    # Status message
    st.sidebar.markdown("---")
    st.sidebar.success(f"✅ Showing {len(filtered_df):,} of {len(scored_df):,} protocols")
    
    # Main content
    if len(filtered_df) == 0:
        st.warning("⚠️ No protocols match your filter criteria. Try adjusting the filters.")
        return
    
    # KPI Cards
    render_kpi_cards(filtered_df)
    
    st.markdown("---")
    
    # Scatter Plot
    render_scatter_plot(filtered_df)
    
    st.markdown("---")
    
    # Additional Charts
    render_additional_charts(filtered_df)
    
    st.markdown("---")
    
    # Data Table
    render_data_table(filtered_df)
    
    st.markdown("---")
    
    # Metric Explanations
    render_metric_explanations()
    
    # Methodology
    render_methodology()
    
    # Footer
    st.markdown("""
        <div style='text-align: center; color: #8b9dc3; padding: 20px; margin-top: 30px;'>
            <small>
                Built with 💜 for M&A Analysts | Data: DefiLlama API | 
                Last Updated: Real-time
            </small>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
