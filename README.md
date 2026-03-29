# Data Analyst Portfolio

Real-world data analysis projects using **live data** from public APIs and open datasets. Each project demonstrates the complete data pipeline: sourcing, cleaning, analysis, visualization, and business/policy insights.

## Projects

| # | Project | Data Source | Key Techniques |
|---|---------|-------------|----------------|
| 1 | [AI/ML Open Source Ecosystem](01_ai_ecosystem_analysis/) | GitHub API, HuggingFace API | API data collection, trend analysis, landscape mapping |
| 2 | [Global CO2 & Climate Trends](02_global_co2_analysis/) | Our World in Data | Time series analysis, geographic comparison, policy analysis |
| 3 | [Cryptocurrency Market Analysis](03_crypto_market_analysis/) | CoinGecko API | Market structure, volatility analysis, tier segmentation |

## Tech Stack

- **Languages:** Python 3.11+
- **Data Collection:** urllib, REST APIs (GitHub, HuggingFace, CoinGecko)
- **Data Processing:** pandas, numpy
- **Visualization:** matplotlib, seaborn
- **Statistics:** scipy, statsmodels
- **Environment:** Jupyter Notebooks

## Data Sources

All data is sourced from **real, public APIs**:
- **GitHub REST API** - Repository metadata, stars, forks, topics
- **HuggingFace API** - Model downloads, tasks, community metrics
- **Our World in Data** - Open-access CO2 and greenhouse gas emissions (CC BY)
- **CoinGecko API** - Real-time cryptocurrency market data

Each project includes a `scripts/fetch_data.py` script to reproduce the data collection.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

To refresh data from live APIs:
```bash
cd <project>/scripts && python fetch_data.py
```
