# A/B Test Analysis: Checkout Flow Optimization

## Overview
Statistical analysis of a checkout redesign experiment prepared for product leadership. Demonstrates the rigorous experiment evaluation process used at top tech companies.

## Business Context
The product team simplified the checkout from 4 steps to 2 steps. This analysis determines whether the change should ship to all users.

## Key Skills Demonstrated
- Experiment validation (SRM check, covariate balance)
- Funnel analysis (visitor → cart → checkout → purchase)
- Hypothesis testing (two-proportion z-test)
- Power analysis (post-hoc and minimum sample size)
- Segmented analysis (device, new vs returning)
- Revenue impact estimation
- Ship/no-ship recommendation with rollout plan

## Files
- `data/ab_test_checkout.csv` - 15,000 user experiment data
- `notebooks/ab_test_analysis.ipynb` - Complete statistical analysis
- `outputs/` - Result visualizations

## Run
```bash
jupyter notebook notebooks/ab_test_analysis.ipynb
```
