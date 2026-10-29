import os
import sqlite3
from datetime import datetime
import requests

# Geographical coordinates for Larnaca (Cyprus)
LATITUDE = 34.9221
LONGITUDE = 33.6279

# Date and time
teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Path to an ALREADY EXISTING database
db_name = "pogoda_larnaca.db"
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, db_name)

# URL to API Open-Meteo
URL_WEATHER = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,cloud_cover,weather_code"
URL_MARINE = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current=sea_surface_temperature,wave_height"



#"""Adds a new row to an existing database."""
conn = sqlite3.connect(db_path)
cursor = conn.cursor()


# """Retrieves data from the Open-Meteo API."""
odpowiedz_pogoda = requests.get(URL_WEATHER).json()
dane_pogody = odpowiedz_pogoda["current"]

odpowiedz_morze = requests.get(URL_MARINE).json()
dane_morza = odpowiedz_morze["current"]


# We are inserting another record into the existing table.
cursor.execute(
"""
INSERT INTO pogoda_i_morze (data_zapisu, data_pomiaru, godzina_pomiaru, temp_powietrza, wilgotnosc, sila_wiatru, kierunek_wiatru, stopien_zachmurzenia, kod_pogody, temp_morza, wysokosc_fali)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""",
(
    teraz,
    dane_pogody["time"][:10],               # data_pomiaru
    dane_pogody["time"][11:],               # godzina_pomiaru
    dane_pogody["temperature_2m"],          # temp_powietrza
    dane_pogody["relative_humidity_2m"],    # wilgotnosc
    dane_pogody['wind_speed_10m'],          # sila_wiatru
    dane_pogody['wind_direction_10m'],      # kierunek_wiatru
    dane_pogody['cloud_cover'],             # stopien_zachmurzenia
    dane_pogody["weather_code"],            # kod_pogody
    dane_morza["sea_surface_temperature"],  # temp_morza
    dane_morza['wave_height']               # wysokosc_fali
    ),
)

conn.commit()
conn.close()
print(f"[{teraz}] New data added to the databas {db_name}.")
