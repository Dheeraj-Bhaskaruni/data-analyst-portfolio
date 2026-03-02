#!/usr/bin/env python3
"""Fetch top AI/ML repositories from the GitHub REST API.

Usage: python fetch_data.py
Output: ../data/github_ai_repos.csv, ../data/huggingface_models.csv
"""
import urllib.request, json, csv, time, os

API_BASE = "https://api.github.com/search/repositories"
HF_API = "https://huggingface.co/api/models"

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "DataAnalyst-Portfolio"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

def fetch_github():
    queries = ["topic:machine-learning", "topic:deep-learning", "topic:llm",
               "topic:generative-ai", "topic:natural-language-processing", "topic:computer-vision"]
    seen, rows = set(), []
    for q in queries:
        data = fetch_json(f"{API_BASE}?q={q}&sort=stars&per_page=100")
        for r in data.get("items", []):
            if r["full_name"] in seen: continue
            seen.add(r["full_name"])
            rows.append({
                "repo_name": r["name"], "full_name": r["full_name"],
                "description": (r.get("description") or "")[:200],
                "stars": r["stargazers_count"], "forks": r["forks_count"],
                "open_issues": r["open_issues_count"],
                "language": r.get("language") or "Unknown",
                "created_at": r["created_at"][:10], "updated_at": r["updated_at"][:10],
                "topics": "|".join(r.get("topics", [])[:10]),
                "license": (r.get("license") or {}).get("spdx_id", "None"),
                "size_kb": r.get("size", 0), "watchers": r["watchers_count"]
            })
        time.sleep(3)
        print(f"  {q}: {len(data.get('items',[]))} repos")
    return rows

def fetch_huggingface():
    rows = []
    for offset in [0, 100]:
        data = fetch_json(f"{HF_API}?sort=downloads&limit=100&offset={offset}")
        for m in data:
            rows.append({
                "model_id": m.get("id",""), "author": m.get("id","").split("/")[0] if "/" in m.get("id","") else "",
                "pipeline_tag": m.get("pipeline_tag") or "unknown",
                "downloads": m.get("downloads",0), "likes": m.get("likes",0),
                "created_at": (m.get("createdAt") or "")[:10],
                "library_name": m.get("library_name") or "unknown",
                "tags": "|".join((m.get("tags") or [])[:8])
            })
        time.sleep(2)
    return rows

if __name__ == "__main__":
    os.makedirs("../data", exist_ok=True)

    print("Fetching GitHub repos...")
    gh = fetch_github()
    with open("../data/github_ai_repos.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(gh[0].keys()))
        w.writeheader(); w.writerows(gh)
    print(f"Saved {len(gh)} repos")

    print("Fetching HuggingFace models...")
    hf = fetch_huggingface()
    with open("../data/huggingface_models.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(hf[0].keys()))
        w.writeheader(); w.writerows(hf)
    print(f"Saved {len(hf)} models")
