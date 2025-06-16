import requests
import pandas as pd
from io import StringIO
from locations import locations  # 👈 Import the module

all_data = pd.DataFrame()

# Loop through each city in the list
for city in locations:
    print(f"Downloading data for: {city}")

    url = f"https://{city}.weatherstats.ca/download.html"

    payload = {
        "formdata": "ok",
        "type": "normal_monthly",  # You can switch to other types like 'daily', 'hourly', etc.
        "limit": "99999999",
        "submit": "Download",
    }

    try:
        response = requests.post(url, data=payload)

        if response.status_code == 200 and "text/csv" in response.headers.get(
            "Content-Type", ""
        ):
            df = pd.read_csv(StringIO(response.text))
            df.set_index("date", inplace=True)
            df["location"] = city.capitalize()
            all_data = pd.concat([all_data, df])
        else:
            print(f"Failed to download for {city}. Status: {response.status_code}")
    except Exception as e:
        print(f"Error downloading {city}: {e}")

# Preview combined data
print("\nCombined Data Preview:")
print(all_data.head())
