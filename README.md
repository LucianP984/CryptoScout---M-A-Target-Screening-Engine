# CryptoVenture M&A Scout

**CryptoVenture M&A Scout** is a professional-grade Deal Sourcing & Valuation Dashboard designed for Investment Analysts and M&A Advisory firms. It automates the screening of Web3 protocols, providing real-time valuation metrics, revenue trends, and comparative analysis to identify undervalued targets.

## Features

*   **Real-time Data Ingestion**: Automatically fetches Protocol TVL, Market Cap, and Revenue/Fees data from DefiLlama.
*   **Automated Valuation Modeling**: Calculates P/S Ratios, Annualized Revenue, and Fair Value estimates based on sector medians.
*   **Venture Scoring System**: Proprietary 0-100 score based on Valuation Gap, Revenue Momentum, and Capital Efficiency.
*   **Market Insights**:
    *   **Valuation Landscape**: Interactive scatter plot (P/S vs Revenue) to spot outliers.
    *   **Growth Tracking**: specialized bar charts highlighting "Revenue Trend" (Green = Growing, Red = Declining).
    *   **Protocol Screening**: Sortable data table with deep financial metrics.
*   **Robust Fallback**: Includes a simulation mode with randomized data for demonstration when API limits are reached.

## Installation & Setup

This project uses modern Python tooling. You can set up and run the application with a single command.

### Prerequisites

*   Python 3.8+
*   (Optional) `uv` package manager

### Quick Start

We provide an automated setup script that creates a virtual environment, installs dependencies, and launches the app.

```bash
python setup.py
```

### Manual Setup

If you prefer to set it up manually:

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

## Tech Stack

*   **Frontend**: Streamlit
*   **Data Processing**: Pandas, NumPy
*   **Visualization**: Plotly Express
*   **Data Source**: DefiLlama API

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
