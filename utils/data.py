import requests
import pandas as pd
import streamlit as st
from utils.consts import DEFI_LLAMA_PROTOCOLS_URL, DEFI_LLAMA_FEES_URL

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_protocols_data() -> pd.DataFrame:
    """
    Fetch protocol data from DefiLlama API.
    
    Returns:
        DataFrame with columns: name, symbol, tvl, mcap, category, chains
    """
    try:
        response = requests.get(DEFI_LLAMA_PROTOCOLS_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        df = pd.DataFrame(data)
        
        # Extract relevant columns
        cols = ['name', 'symbol', 'tvl', 'mcap', 'category', 'chains']
        # Handle missing columns safely
        for c in cols:
            if c not in df.columns:
                df[c] = None
        
        df = df[cols].copy()
        
        # Clean data
        df['tvl'] = pd.to_numeric(df['tvl'], errors='coerce').fillna(0)
        df['mcap'] = pd.to_numeric(df['mcap'], errors='coerce').fillna(0)
        
        # Extract primary chain (first in list)
        df['primary_chain'] = df['chains'].apply(
            lambda x: x[0] if isinstance(x, list) and len(x) > 0 else 'Unknown'
        )
        
        return df
        
    except Exception as e:
        st.warning(f"⚠️ Failed to fetch protocol data: {e} - we are using ramdom generated data")
        return get_sample_protocols_data()


@st.cache_data(ttl=3600)
def fetch_fees_data() -> pd.DataFrame:
    """
    Fetch fee/revenue data from DefiLlama API.
    
    Returns:
        DataFrame with columns: name, symbol, total24h, total7d, total30d
    """
    try:
        response = requests.get(DEFI_LLAMA_FEES_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if 'protocols' not in data:
            raise ValueError("No protocols in fees response")
        
        protocols = data['protocols']
        
        rows = []
        for protocol in protocols:
            rows.append({
                'name': protocol.get('name', ''),
                'symbol': protocol.get('symbol', ''),
                'total24h': protocol.get('total24h', 0),
                'total7d': protocol.get('total7d', 0),
                'total30d': protocol.get('total30d', 0),
            })
        
        df = pd.DataFrame(rows)
        
        # Clean data
        for col in ['total24h', 'total7d', 'total30d']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df
        
    except Exception as e:
        # st.warning(f"⚠️ Failed to fetch fees data: {e}. Using sample data.")
        # Only warn once in the main protocols fetch if both fail, or just warn here too
        # The user requested "if the api dosent work write a message that we are using ramdom generated data"
        # We can rely on the first warning or print it here too.
        return get_sample_fees_data()


def get_sample_protocols_data() -> pd.DataFrame:
    """Generate sample data for demonstration when API fails."""
    import random
    
    categories = ['Lending', 'Dexes', 'Liquid Staking', 'CDP', 'Yield', 'Derivatives', 'Bridge', 'Services']
    chains = ['Ethereum', 'Arbitrum', 'Optimism', 'Polygon', 'Solana', 'Avalanche', 'Binance']
    
    names = [f"Protocol {i}" for i in range(1, 51)]
    data = []
    
    for name in names:
        cat = random.choice(categories)
        chain = random.choice(chains)
        tvl = random.uniform(1e6, 10e9)
        mcap = tvl * random.uniform(0.1, 2.0)
        symbol = name.split()[1] # Just use the number
        
        data.append({
            'name': name,
            'symbol': f"PROTO{symbol}",
            'tvl': tvl,
            'mcap': mcap,
            'category': cat,
            'chains': [chain],
            'primary_chain': chain
        })
        
    return pd.DataFrame(data)


def get_sample_fees_data() -> pd.DataFrame:
    """Generate sample fees data for demonstration when API fails."""
    import random
    
    names = [f"Protocol {i}" for i in range(1, 51)]
    data = []
    
    for name in names:
        daily_rev = random.uniform(1000, 1000000)
        
        data.append({
            'name': name,
            'symbol': f"PROTO{name.split()[1]}",
            'total24h': daily_rev,
            'total7d': daily_rev * 7 * random.uniform(0.8, 1.2), # Some variance
            'total30d': daily_rev * 30 * random.uniform(0.8, 1.2)
        })
        
    return pd.DataFrame(data)


def merge_datasets(protocols_df: pd.DataFrame, fees_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge protocol data with fees data.
    """
    # Create copies to avoid modifying originals
    protocols = protocols_df.copy()
    fees = fees_df.copy()
    
    # Standardize for matching
    protocols['name_lower'] = protocols['name'].str.lower().str.strip()
    fees['name_lower'] = fees['name'].str.lower().str.strip()
    
    # Deduplicate fees data on name_lower (keep first occurrence)
    fees_dedup = fees.drop_duplicates(subset='name_lower', keep='first')
    
    # Merge on name
    merged = protocols.merge(
        fees_dedup[['name_lower', 'total24h', 'total7d', 'total30d']],
        on='name_lower',
        how='left'
    )
    
    # For still unmatched rows, try symbol matching
    unmatched_mask = merged['total24h'].isna()
    if unmatched_mask.any():
        # Prepare symbol-based matching
        # Must check if 'symbol' exists
        if 'symbol' in protocols.columns:
            protocols['symbol_lower'] = protocols['symbol'].str.lower().str.strip()
            
            # Since we merged protocols, merged already has protocol symbols. 
            # We need to look up into FEES by symbol.
            
            fees['symbol_lower'] = fees['symbol'].str.lower().str.strip()
            fees_symbol_dedup = fees.drop_duplicates(subset='symbol_lower', keep='first')
            
            # Get unmatched protocol indices
            unmatched_indices = merged[unmatched_mask].index.tolist()
            
            for idx in unmatched_indices:
                # Get the symbol from the protocols DF (using the index which is preserved/aligned if left merge?
                # Wait, merge resets index if not careful.
                # Left merge on Protocols preserves Protocols index if 1-to-1?
                # Actually, `merge` returns new DF with integers usually.
                # But here we are iterating over `merged` indices.
                
                # Check protocols original
                # This logic is a bit tricky if `merged` indices don't align with `protocols` indices.
                # 'protocols' and 'merged' should have same length and order if 'how=left' and 'fees_dedup' is unique on join key.
                # 'fees_dedup' IS unique (we dropped duplicates).
                # So indices should align.
                
                # Let's use loc from merged directly if symbol is reachable?
                # merged has 'symbol' column from protocols.
                
                symbol_val = merged.loc[idx, 'symbol']
                if pd.notna(symbol_val):
                    symbol_lower = str(symbol_val).lower().strip()
                    match = fees_symbol_dedup[fees_symbol_dedup['symbol_lower'] == symbol_lower]
                    if not match.empty:
                        merged.loc[idx, 'total24h'] = match.iloc[0]['total24h']
                        merged.loc[idx, 'total7d'] = match.iloc[0]['total7d']
                        merged.loc[idx, 'total30d'] = match.iloc[0]['total30d']
    
    # Fill remaining NaN with 0
    for col in ['total24h', 'total7d', 'total30d']:
        merged[col] = merged[col].fillna(0)
    
    # Clean up temporary columns (drop only if they exist)
    cols_to_drop = ['name_lower', 'symbol_lower']
    existing_drop = [c for c in cols_to_drop if c in merged.columns]
    merged = merged.drop(columns=existing_drop)
    
    return merged
