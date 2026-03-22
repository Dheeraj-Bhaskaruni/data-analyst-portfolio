# Cryptocurrency Market Analysis

## Overview
Real-time analysis of the cryptocurrency market using the **CoinGecko API**. Covers the top 250 coins by market cap with metrics including price, volume, market dominance, and ATH distance.

## Data Source
- **CoinGecko API** - https://www.coingecko.com/en/api (free tier)

## Key Findings
- Bitcoin dominance remains the key structural feature
- Top 10 coins hold the majority of total market cap
- Smaller caps show significantly higher volatility
- Most coins are trading well below their all-time highs

## Techniques
Market structure analysis, dominance calculation, price distribution, volume-market cap relationship, tier segmentation, ATH recovery analysis

## Run
```bash
cd scripts && python fetch_data.py  # refresh data
jupyter notebook notebooks/crypto_analysis.ipynb
```
