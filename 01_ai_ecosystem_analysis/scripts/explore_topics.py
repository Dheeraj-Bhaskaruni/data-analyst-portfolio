#!/usr/bin/env python3
"""Quick topic exploration."""
import pandas as pd
gh = pd.read_csv('../data/github_ai_repos.csv')
for _, r in gh.iterrows():
    topics = str(r.get('topics','')).split('|')
    for t in topics:
        if t: print(t)
