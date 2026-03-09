# AI & LLM Open Source Ecosystem Analysis

## Overview
Analysis of the AI/ML open-source landscape using live data from the **GitHub REST API** and **HuggingFace API**. Maps the ecosystem of 400+ top AI repositories and 200 most-downloaded models.

## Data Sources
- **GitHub API** - Top repos by stars across ML, DL, LLM, GenAI, NLP, CV topics
- **HuggingFace API** - Top 200 models sorted by download count

## Key Findings
- Python dominates the AI ecosystem by a massive margin
- Explosive growth post-2022 driven by the LLM revolution
- Sentence transformers and text generation are the most downloaded model types
- Apache-2.0 and MIT are the dominant licenses

## Techniques
API data collection, trend analysis, language distribution, community engagement analysis (stars/forks), model ecosystem mapping

## Run
```bash
cd scripts && python fetch_data.py  # refresh data
jupyter notebook notebooks/ai_ecosystem_analysis.ipynb
```
