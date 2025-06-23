import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# Get current year and month from system date
now = datetime.now()
current_year = now.year
current_month = now.month

# List of (station_id, location_name, province) tuples
stations = [
    (50089, "ST. JOHN'S INTL A", "NEWFOUNDLAND"),
    (50091, "SASKATOON INTL A", "SASKATCHEWAN"),
    (50309, "MONCTON/GREATER MONCTON ROMEO LEBLANC INTL A", "NEW BRUNSWICK"),
    (50430, "CALGARY INTL A", "ALBERTA"),
    (50620, "HALIFAX STANFIELD INT'L A", "NOVA SCOTIA"),
    (50621, "CHARLOTTETOWN A", "PRINCE EDWARD ISLAND"),
    (50842, "WHITEHORSE A", "YUKON TERRITORY"),
    (51097, "WINNIPEG INTL A", "MANITOBA"),
    (51157, "MONTREAL INTL A", "QUEBEC"),
    (51442, "VANCOUVER INTL A", "BRITISH COLUMBIA"),
    (51459, "TORONTO INTL A", "ONTARIO"),
]

columns_to_keep = [
    "DAY",
    "Mean TempDefinition°C",
    "Total RainDefinitionmm",
    "Total SnowDefinitioncm",
    "Total PrecipDefinitionmm",
    "Snow on GrndDefinitioncm",
]

all_data = []

for station_id, location, province in stations:
    for year in range(2008, current_year + 1):
        last_month = current_month if year == current_year else 12
        for month in range(1, last_month + 1):
            url = (
                f"https://climate.weather.gc.ca/climate_data/daily_data_e.html?"
                f"StationID={station_id}&Year={year}&Month={month}&Day=1&timeframe=2&format=html"
            )
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            table = soup.find("table", class_="data-table")
            if not table:
                continue

            headers = [
                th.get_text(strip=True) for th in table.find("thead").find_all("th")
            ]
            rows = []
            for tr in table.find("tbody").find_all("tr"):
                cols = [td.get_text(strip=True) for td in tr.find_all("td")]
                day = tr.find("th").get_text(strip=True) if tr.find("th") else ""
                if cols:
                    rows.append([day] + cols)

            if not rows:
                continue

            df = pd.DataFrame(rows, columns=headers)
            df["location"] = location
            df["station_id"] = station_id
            df["province"] = province
            df["year"] = year
            df["month"] = month

            # Clean Day column: remove non-numeric, keep only 1-31
            if "DAY" in df.columns:
                df["DAY"] = pd.to_numeric(df["DAY"], errors="coerce")
                df = df[df["DAY"].between(1, 31)]
                df["DAY"] = df["DAY"].astype("Int64")

            # Convert weather columns to float
            for col in [
                "Mean TempDefinition°C",
                "Total RainDefinitionmm",
                "Total SnowDefinitioncm",
                "Total PrecipDefinitionmm",
                "Snow on GrndDefinitioncm",
            ]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            # Keep only required columns (if available)
            available_cols = [col for col in columns_to_keep if col in df.columns]
            df = df[
                available_cols + ["location", "province", "station_id", "year", "month"]
            ]

            all_data.append(df)

# Concatenate all data
# if all_data:
#     final_df = pd.concat(all_data, ignore_index=True)
#     print(final_df.head())
#     print(final_df.tail())
#     final_df.to_csv("weather_all_stations_2008_to_present.csv", index=False)
#     print("Data saved to weather_all_stations_2008_to_present.csv")
# else:
#     print("No data was scraped.")
