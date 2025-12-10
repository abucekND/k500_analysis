


# Introduction

Cars are hard. Choosing the best car to invest in? Even harder. Cars
vary in:

- performance (0–60, top speed)  
- design  
- historical significance  
- market demand  
- future value

To make this decision more data-driven, this project uses the K500
Index, an independent ranking of 500 investment-grade classic cars
curated by experts and historians. The goal of this project is to
identify the strongest candidate for the best classic car to invest in
using data scraped directly from the K500 website.

This README documents the dataset, code, analysis, and final conclusions
of the project.

# Data Source

The data comes directly from the K500 website’s Guide page. URL:
https://k500.com/the-guide

The page contains a sortable table listing:

- Year  
- Make  
- Model  
- Body  
- Category  
- 0–60 mph time  
- Top speed  
- Rating (0–100 scale)

The data was scraped using Python, Requests, BeautifulSoup, and
pandas.  
The dataset was not downloaded manually; it was extracted dynamically
from the website using the final code included in this repository.

# Code w. Steps

Below is the exact code used for scraping, cleaning, sorting, and
generating the recommendation.

*Step 1: Import packages & define URLs*

``` python
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

BASE_URL = "https://k500.com"
HOME_URL = BASE_URL + "/"
GUIDE_URL = BASE_URL + "/the-guide"
```

*Step 2: Request homepage and extract K500/K50 indices*

``` python
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
```

    Current K500 index value: 100.0
    Current K50 index value : 100.0

*Step 3: Read the Guide table and inspect its strucure*

``` python
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
```


    Raw Guide columns as scraped:
    ['Year', 'Make', 'Model', 'Body', 'Category', '0-60', 'Top Speed', 'Rating']

    First few raw rows:
            Year    Make          Model    Body       Category       0-60  \
    0       Sort    Sort           Sort    Sort           Sort       Sort   
    1  1955-1959  Abarth  750 GT Zagato   Coupe  Sports-Rac...  15.0 secs   
    2  1960-1971  Abarth           1000  Saloon  Getaway Ca...          -   
    3  1963-1964  Abarth     Simca 2000   Coupe  Sports-Rac...   6.0 secs   
    4  1963-1971  Abarth            595  Saloon       Microcar  28.3 secs   

      Top Speed Rating  
    0      Sort   Sort  
    1     89mph     50  
    2    100mph     45  
    3    160mph     65  
    4     75mph     46  

    [Saved] Raw scraped table → k500_raw.csv

*Step 4: Define function to extract numeric values*

``` python
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
```

*Step 5: Clean numberic fields and prepare dataset*

``` python
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
```


    Cleaned Guide preview:
            Year    Make          Model    Body       Category       0-60  \
    1  1955-1959  Abarth  750 GT Zagato   Coupe  Sports-Rac...  15.0 secs   
    2  1960-1971  Abarth           1000  Saloon  Getaway Ca...          -   
    3  1963-1964  Abarth     Simca 2000   Coupe  Sports-Rac...   6.0 secs   
    4  1963-1971  Abarth            595  Saloon       Microcar  28.3 secs   
    5  1965-1968  Abarth        OT 1300   Coupe  Sports-Rac...   7.0 secs   

      Top Speed  Rating  0_60_sec  TopSpeed_mph  
    1     89mph    50.0      15.0          89.0  
    2    100mph    45.0       NaN         100.0  
    3    160mph    65.0       6.0         160.0  
    4     75mph    46.0      28.3          75.0  
    5    150mph    63.0       7.0         150.0  
    [Saved] Cleaned dataset → k500_cleaned.csv

*Step 6: Rank cars and generate the recommendation*

``` python
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
print(f"  Rating     : {recommended['Rating']}")
```


    Top 10 cars by K500 Rating (as scraped):
              Year           Make               Model       Category       0-60  \
    375  1955-1955  Mercedes-Benz       300 SLR Coupé  Grand Tour...   6.9 secs   
    127  1936-1938        Bugatti  Type 57SC Atlantic  Pre-War, S...  10.0 secs   
    185  1962-1964        Ferrari             250 GTO  Sports-Rac...   4.7 secs   
    369  1928-1932  Mercedes-Benz                 SSK  Grand Tour...  13.0 secs   
    366  1994-1998        McLaren                  F1       Hypercar   3.2 secs   
    175  1957-1961        Ferrari     250 Testa Rossa  Sports-Rac...   5.0 secs   
    17   1937-1938     Alfa Romeo             8C 2900  Grand Tour...  10.0 secs   
    121  1929-1933        Bugatti      Type 41 Royale  Grand Tour...  18.0 secs   
    438  1969-1971        Porsche                917K  Film Star,...   3.5 secs   
    14   1931-1934     Alfa Romeo             8C 2300  Grand Tour...  10.0 secs   

         Top Speed  Rating  
    375  176.47mph   100.0  
    127     125mph    99.0  
    185     174mph    97.0  
    369     125mph    95.0  
    366  242.95mph    95.0  
    175     167mph    95.0  
    17      130mph    92.0  
    121     125mph    90.0  
    438     240mph    88.0  
    14      115mph    88.0  

    *** Recommendation based on scraped data ***
    Current market indices: K500 = 100.0, K50 = 100.0
    Based on the K500 Guide ratings alone, a very strong candidate for a 'first classic car to buy' is:

      Year range : 1955-1955
      Make       : Mercedes-Benz
      Model      : 300 SLR Coupé
      Category   : Grand Tour...
      0-60 mph   : 6.9 secs
      Top speed  : 176.47mph
      Rating     : 100.0
