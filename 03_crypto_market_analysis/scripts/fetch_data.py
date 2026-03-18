#!/usr/bin/env python3
"""Fetch cryptocurrency market data from CoinGecko API.

Source: https://www.coingecko.com/en/api
Usage: python fetch_data.py
Output: ../data/crypto_market.csv
"""
import urllib.request, json, csv, time, os

API = "https://api.coingecko.com/api/v3/coins/markets"

if __name__ == "__main__":
    os.makedirs("../data", exist_ok=True)
    print("Fetching CoinGecko data...")
    rows = []
    for page in [1, 2]:
        url = f"{API}?vs_currency=usd&order=market_cap_desc&per_page=125&page={page}&sparkline=false"
        req = urllib.request.Request(url, headers={"User-Agent": "DataAnalyst-Portfolio"})
        data = json.loads(urllib.request.urlopen(req, timeout=30).read())
        for c in data:
            rows.append({
                "id": c["id"], "symbol": c["symbol"], "name": c["name"],
                "current_price": c.get("current_price",0),
                "market_cap": c.get("market_cap",0),
                "market_cap_rank": c.get("market_cap_rank",0),
                "total_volume": c.get("total_volume",0),
                "high_24h": c.get("high_24h",0), "low_24h": c.get("low_24h",0),
                "price_change_24h": c.get("price_change_24h",0),
                "price_change_pct_24h": c.get("price_change_percentage_24h",0),
                "market_cap_change_pct_24h": c.get("market_cap_change_percentage_24h",0),
                "circulating_supply": c.get("circulating_supply",0),
                "total_supply": c.get("total_supply",""),
                "ath": c.get("ath",0), "ath_change_pct": c.get("ath_change_percentage",0),
                "ath_date": (c.get("ath_date") or "")[:10],
                "atl": c.get("atl",0), "atl_date": (c.get("atl_date") or "")[:10],
            })
        time.sleep(3)
    with open("../data/crypto_market.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"Saved {len(rows)} coins")
