import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

BASE_URL = "https://k500.com"
HOME_URL = BASE_URL + "/"
GUIDE_URL = BASE_URL + "/the-guide"

home_resp = requests.get(HOME_URL)
home_resp.raise_for_status()

home_soup = BeautifulSoup(home_resp.content, "html.parser")

home_text = home_soup.get_text(" ", strip=True)

k500_match = re.search(r"K500\s+([0-9]+\.[0-9]+)", home_text)
k50_match  = re.search(r"K50\s+([0-9]+\.[0-9]+)",  home_text)

if not k500_match or not k50_match:
    raise RuntimeError("Could not find K500 and K50 index values on the homepage")

k500_value = float(k500_match.group(1))
k50_value  = float(k50_match.group(1))

print(f"Current K500 index value: {k500_value}")
print(f"Current K50 index value : {k50_value}")

guide_tables = pd.read_html(GUIDE_URL)
if not guide_tables:
    raise RuntimeError("No tables found on the Guide page")

guide = guide_tables[0]

print("\nRaw Guide columns as scraped:")
print(guide.columns.tolist())
print("\nFirst few raw rows:")
print(guide.head())

guide.to_csv("k500_raw.csv", index=False)
print("\n[Saved] Raw scraped table → k500_raw.csv")

expected_cols = ["Year", "Make", "Model", "Body", "Category", "0-60", "Top Speed", "Rating"]

if len(guide.columns) == len(expected_cols):
    guide.columns = expected_cols
else:
    print("\n[Warning] Column count mismatch, keeping original column names.")
    print("You may want to inspect guide.columns and rename manually.\n")

def to_float_maybe(x):
    """
    Try to extract a float from strings like '5.2 secs', '138mph',
    '112-130mph', '-', etc.
    """
    if isinstance(x, str):
        m = re.search(r"(\d+(\.\d+)?)", x)
        if m:
            return float(m.group(1))
        else:
            return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None

if "0-60" in guide.columns:
    guide["0_60_sec"] = guide["0-60"].apply(to_float_maybe)
if "Top Speed" in guide.columns:
    guide["TopSpeed_mph"] = guide["Top Speed"].apply(to_float_maybe)

if "Rating" in guide.columns:
    guide["Rating"] = guide["Rating"].apply(to_float_maybe)

if "Rating" in guide.columns:
    guide_clean = guide.dropna(subset=["Rating"]).copy()
else:
    guide_clean = guide.copy()
    print("\n[Warning] 'Rating' column not found; ranking will not work as intended.")

print("\nCleaned Guide preview:")
print(guide_clean.head())

guide_clean.to_csv("k500_cleaned.csv", index=False)
print("[Saved] Cleaned dataset → k500_cleaned.csv")

if "Rating" in guide_clean.columns:
    guide_sorted = guide_clean.sort_values("Rating", ascending=False)
else:
    guide_sorted = guide_clean

top_n = 10
top_cars = guide_sorted.head(top_n)

print(f"\nTop {top_n} cars by K500 Rating (as scraped):")
print(top_cars[["Year", "Make", "Model", "Category", "0-60", "Top Speed", "Rating"]])

recommended = top_cars.iloc[0]

print("\n*** Recommendation based on scraped data ***")
print(f"Current market indices: K500 = {k500_value}, K50 = {k50_value}")
print(
    "Based on the K500 Guide ratings alone, a very strong candidate "
    "for a 'first classic car to buy' is:\n"
)
print(f"  Year range : {recommended['Year']}")
print(f"  Make       : {recommended['Make']}")
print(f"  Model      : {recommended['Model']}")
print(f"  Category   : {recommended['Category']}")
print(f"  0-60 mph   : {recommended['0-60']}")
print(f"  Top speed  : {recommended['Top Speed']}")
print(f"  Rating     : {recommended['Rating']} (higher is better)")