# Global CO2 Emissions & Climate Trends

## Overview
Analysis of global CO2 emissions using the **Our World in Data** open dataset. Covers 200+ countries from 2000-present with metrics including total emissions, per-capita, by fuel source, and cumulative historical responsibility.

## Data Source
- **OWID CO2 Dataset** - https://github.com/owid/co2-data (CC BY license)

## Key Findings
- Global emissions continue rising despite climate pledges
- Massive per-capita gap between developed and developing nations
- Coal remains the #1 source but gas is growing fastest
- Asia dominates total emissions; North America/Europe hold cumulative responsibility

## Techniques
Time series analysis, geographic comparison, per-capita normalization, fuel source decomposition, GDP-emissions correlation, cumulative emissions analysis

## Run
```bash
cd scripts && python fetch_data.py  # refresh data
jupyter notebook notebooks/co2_analysis.ipynb
```
