import pandas as pd
import numpy as np
from utils.consts import VALUATION_GAP_WEIGHT, REVENUE_TREND_WEIGHT, SIZE_EFFICIENCY_WEIGHT

def calculate_financial_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate key financial metrics for valuation analysis.
    """
    df = df.copy()
    
    # Calculate Annualized Revenue
    # Priority: 30d * 12, fallback to 24h * 365
    df['annualized_revenue'] = np.where(
        df['total30d'] > 0,
        df['total30d'] * 12,  # 30 days of data, annualize
        df['total24h'] * 365  # Use daily revenue, 365 days
    )
    
    # Calculate P/S Ratio
    # Guard against division by zero
    df['ps_ratio'] = np.where(
        df['annualized_revenue'] > 0,
        df['mcap'] / df['annualized_revenue'],
        np.inf  # Infinite P/S when no revenue
    )
    
    # Replace infinity with a very high number for calculations
    df['ps_ratio_calc'] = df['ps_ratio'].replace([np.inf, -np.inf], np.nan)
    
    # Calculate Sector Median P/S (excluding infinite values)
    valid_ps = df[df['ps_ratio_calc'].notna() & (df['ps_ratio_calc'] > 0) & (df['ps_ratio_calc'] < 1000)]
    sector_median_ps = valid_ps['ps_ratio_calc'].median() if len(valid_ps) > 0 else 10.0
    
    # Store sector median for display
    df['sector_median_ps'] = sector_median_ps
    
    # Calculate Fair Value
    df['fair_value'] = df['annualized_revenue'] * sector_median_ps
    
    # Calculate Upside Potential (%)
    df['upside_potential'] = np.where(
        df['mcap'] > 0,
        ((df['fair_value'] - df['mcap']) / df['mcap']) * 100,
        0
    )
    
    return df


def calculate_venture_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the Venture Score (0-100) based on three components.
    """
    df = df.copy()
    
    # 1. Valuation Gap Score
    # Cap upside at 200% and floor at -100% for scoring
    upside_capped = df['upside_potential'].clip(-100, 200)
    # Normalize: -100 -> 0, 200 -> weight * 100
    df['valuation_score'] = ((upside_capped + 100) / 300) * (VALUATION_GAP_WEIGHT * 100)
    
    # 2. Revenue Trend Score
    # Calculate 7d daily average
    df['daily_avg_7d'] = df['total7d'] / 7
    
    # Revenue trend: (current daily - 7d avg) / 7d avg
    df['revenue_trend'] = np.where(
        df['daily_avg_7d'] > 0,
        ((df['total24h'] - df['daily_avg_7d']) / df['daily_avg_7d']) * 100,
        0  # No trend data available
    )
    
    # Flag for insufficient data
    df['revenue_trend_status'] = np.where(
        df['total7d'] > 0,
        'Calculated',
        'Insufficient Data'
    )
    
    # Normalize: -50% to +50% trend -> 0 to weight * 100
    trend_capped = df['revenue_trend'].clip(-50, 50)
    df['trend_score'] = ((trend_capped + 50) / 100) * (REVENUE_TREND_WEIGHT * 100)
    
    # 3. Size/Efficiency Score
    # TVL / Market Cap ratio
    df['tvl_mcap_ratio'] = np.where(
        df['mcap'] > 0,
        df['tvl'] / df['mcap'],
        0
    )
    
    # Normalize: 0-10 ratio -> 0 to weight * 100 (cap at 10x)
    ratio_capped = df['tvl_mcap_ratio'].clip(0, 10)
    df['efficiency_score'] = (ratio_capped / 10) * (SIZE_EFFICIENCY_WEIGHT * 100)
    
    # Calculate Final Venture Score
    df['venture_score'] = (
        df['valuation_score'] + 
        df['trend_score'] + 
        df['efficiency_score']
    ).round(1)
    
    # Cap at 0-100
    df['venture_score'] = df['venture_score'].clip(0, 100)
    
    return df
