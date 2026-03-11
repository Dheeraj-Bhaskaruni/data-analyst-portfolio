#!/usr/bin/env python3
"""Fetch global CO2 emissions data from Our World in Data (OWID).

Source: https://github.com/owid/co2-data
Usage: python fetch_data.py
Output: ../data/owid_co2_data.csv
"""
import urllib.request, csv, io, os

URL = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
KEEP = ["country","year","iso_code","population","gdp","co2","co2_per_capita","co2_per_gdp",
        "coal_co2","oil_co2","gas_co2","cement_co2","co2_growth_prct","share_global_co2",
        "cumulative_co2","energy_per_capita","methane","nitrous_oxide","total_ghg"]

if __name__ == "__main__":
    os.makedirs("../data", exist_ok=True)
    print("Downloading OWID CO2 data...")
    req = urllib.request.Request(URL, headers={"User-Agent": "DataAnalyst-Portfolio"})
    raw = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(raw))
    rows = []
    for row in reader:
        try:
            yr = int(float(row.get("year", 0)))
        except: continue
        if yr < 2000: continue
        rows.append({c: row.get(c, "") for c in KEEP})
    with open("../data/owid_co2_data.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=KEEP)
        w.writeheader(); w.writerows(rows)
    print(f"Saved {len(rows)} rows (2000-present)")
