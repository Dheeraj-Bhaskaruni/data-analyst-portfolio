#!/usr/bin/env python3
"""Topic + language analysis."""
import pandas as pd
from collections import Counter
gh = pd.read_csv('../data/github_ai_repos.csv')
gh['language'] = gh['language'].fillna('Unknown')  # fix null languages
topics = Counter()
for t_str in gh['topics'].dropna():
    for t in t_str.split('|'):
        if t: topics[t] += 1
for t, c in topics.most_common(20):
    print(f'{t}: {c}')
