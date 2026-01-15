# API Endpoints
DEFI_LLAMA_PROTOCOLS_URL = "https://api.llama.fi/protocols"
DEFI_LLAMA_FEES_URL = "https://api.llama.fi/overview/fees"

# Scoring Model Weights (Global Constants)
VALUATION_GAP_WEIGHT = 0.40   # How undervalued compared to sector median
REVENUE_TREND_WEIGHT = 0.30   # Revenue momentum (1d vs 7d average)
SIZE_EFFICIENCY_WEIGHT = 0.30  # TVL / Market Cap ratio (capital efficiency)

# Category descriptions for user education
CATEGORY_DESCRIPTIONS = {
    'Dexs': 'Decentralized Exchanges - Platforms for peer-to-peer crypto trading without intermediaries (e.g., Uniswap, Curve)',
    'Lending': 'Lending Protocols - DeFi platforms that enable users to lend and borrow crypto assets (e.g., Aave, Compound)',
    'Liquid Staking': 'Liquid Staking - Protocols that allow staking while maintaining liquidity through derivative tokens (e.g., Lido, Rocket Pool)',
    'CDP': 'Collateralized Debt Positions - Protocols for borrowing stablecoins against crypto collateral (e.g., MakerDAO)',
    'Yield': 'Yield Aggregators - Platforms that optimize yield farming strategies across DeFi (e.g., Yearn Finance)',
    'DEX Aggregator': 'DEX Aggregators - Tools that find the best prices across multiple decentralized exchanges',
    'Derivatives': 'Derivatives - Platforms for trading crypto futures, options, and perpetual contracts',
    'Bridge': 'Cross-Chain Bridges - Infrastructure for transferring assets between different blockchains',
    'Launchpad': 'Launchpads - Platforms for launching new crypto projects and token sales',
    'Indexes': 'Index Protocols - DeFi index funds that track baskets of crypto assets',
    'Synthetics': 'Synthetic Assets - Protocols for creating tokenized versions of real-world assets',
    'Options': 'Options Protocols - Platforms for trading crypto options contracts',
    'Prediction Market': 'Prediction Markets - Platforms for betting on future events using crypto',
    'Insurance': 'DeFi Insurance - Protocols offering coverage for smart contract risks',
    'Privacy': 'Privacy Protocols - Platforms focused on anonymous/private crypto transactions',
    'Leveraged Farming': 'Leveraged Farming - Yield farming with built-in leverage/borrowing',
    'RWA': 'Real World Assets - Protocols tokenizing real-world assets like real estate, bonds',
    'Restaking': 'Restaking - Protocols that allow staked assets to be reused for additional security/yield',
}
