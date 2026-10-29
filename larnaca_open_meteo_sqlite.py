import os
import sys
import sqlite3
from datetime import datetime
import requests

# Geographical coordinates for Larnaca (Cyprus)
LATITUDE = 34.9221
LONGITUDE = 33.6279

# Date and time for logging
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Database path configuration
DB_NAME = "pogoda_larnaca.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, DB_NAME)

# Open-Meteo API Endpoints
URL_WEATHER = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,cloud_cover,weather_code"
URL_MARINE = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current=sea_surface_temperature,wave_height"

def fetch_api_data(url):
    """Safely handles HTTP requests and JSON parsing with timeout protection."""
    try:
        # Added a 10-second timeout to prevent the script from hanging indefinitely
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Triggers an exception for 4xx or 5xx HTTP codes
        return response.json()
    except requests.RequestException as e:
        print(f"[{now_str}] [ERROR] API Request failed for {url}. Reason: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError:
        print(f"[{now_str}] [ERROR] Failed to parse JSON response from {url}.", file=sys.stderr)
        sys.exit(1)

# ==============================================================================
# 1. FETCHING DATA
# ==============================================================================
print(f"[{now_str}] [INFO] Fetching current weather and marine data...")

weather_json = fetch_api_data(URL_WEATHER)
marine_json = fetch_api_data(URL_MARINE)

# Safeguard against unexpected missing keys in API response
if "current" not in weather_json or "current" not in marine_json:
    print(f"[{now_str}] [ERROR] Invalid response format from Open-Meteo API.", file=sys.stderr)
    sys.exit(1)

dane_pogody = weather_json["current"]
dane_morza = marine_json["current"]

# ==============================================================================
# 2. SQLITE DATABASE INSERTION
# ==============================================================================
conn = None
try:
    # Set a timeout for SQLite in case the DB file is locked by another process
    conn = sqlite3.connect(DB_PATH, timeout=20)
    cursor = conn.cursor()

    query = """
        INSERT INTO pogoda_i_morze (
            data_zapisu, data_pomiaru, godzina_pomiaru, temp_powietrza,
            wilgotnosc, sila_wiatru, kierunek_wiatru, stopien_zachmurzenia,
            kod_pogody, temp_morza, wysokosc_fali
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    # Extract date and time components safely
    measurement_time = dane_pogody.get("time", "1970-01-01T00:00")
    date_part = measurement_time[:10]
    time_part = measurement_time[11:]

    record_data = (
        now_str,
        date_part,
        time_part,
        dane_pogody.get("temperature_2m"),
        dane_pogody.get("relative_humidity_2m"),
        dane_pogody.get("wind_speed_10m"),
        dane_pogody.get("wind_direction_10m"),
        dane_pogody.get("cloud_cover"),
        dane_pogody.get("weather_code"),
        dane_morza.get("sea_surface_temperature"),
        dane_morza.get("wave_height")
    )

    cursor.execute(query, record_data)
    conn.commit()
    print(f"[{now_str}] [SUCCESS] New daily record successfully added to {DB_NAME}.")

except sqlite3.Error as e:
    print(f"[{now_str}] [ERROR] Database transaction failed: {e}", file=sys.stderr)
    sys.exit(1)

finally:
    if conn:
        conn.close()
