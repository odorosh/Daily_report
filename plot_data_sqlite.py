import json
import os
import sqlite3
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

# Use "Agg" backend to avoid GUI/graphics errors in headless Linux environments (like cron)
matplotlib.use("Agg")

# Get the base directory of the script
base_dir = os.path.dirname(os.path.abspath(__file__))
generated_images = []

# ==============================================================================
# 1. READING DATA FROM SQLITE WITH PANDAS
# ==============================================================================
db_path = os.path.join(base_dir, "pogoda_larnaca.db")
conn = sqlite3.connect(db_path)

query = """
    SELECT data_pomiaru, temp_powietrza, wilgotnosc, sila_wiatru,
           kierunek_wiatru, stopien_zachmurzenia, kod_pogody, temp_morza
    FROM pogoda_i_morze
    ORDER BY data_pomiaru;
"""

df = pd.read_sql_query(query, conn, parse_dates=["data_pomiaru"])
conn.close()

if df.empty:
    print("[ERROR] Database is empty!")
    exit(1)

# Set date as index
df.set_index("data_pomiaru", inplace=True)

# ==============================================================================
# 2. HANDLING GAPS IN DATA
# ==============================================================================
# Create a continuous 15-day range up to the maximum date found in the DB
max_date = df.index.max()
full_index = pd.date_range(start=max_date - pd.Timedelta(days=14), end=max_date, freq="D")

print(f"[INFO] Data range: {df.index.min().strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")

# Reindex to fill missing days with NaN
df = df.reindex(full_index)

# Prepare date formatting string for filenames
date_str_min = df.index.min().strftime("%Y-%m-%d")
date_str_max = df.index.max().strftime("%Y-%m-%d")

# ==============================================================================
# 3. PLOTTING AIR TEMPERATURE WITH WEATHER ICONS
# ==============================================================================
fig, ax1 = plt.subplots(figsize=(14, 9))

# Main plot for air temperature
ax1.plot(
    df.index,
    df["temp_powietrza"],
    color="#d32f2f",
    marker="o",
    markersize=5,
    linewidth=2,
    label="Temperature (°C)",
)

def wklej_ikone_pogody(ax, data_x, temp_y, wmo_code):
    """Helper function to overlay weather icons on the plot."""
    icon_path = os.path.join(base_dir, "icons", f"{wmo_code}.png")
    if os.path.exists(icon_path):
        img = plt.imread(icon_path)
        imagebox = OffsetImage(img, zoom=0.25)
        # Position the icon slightly above the temperature point
        ab = AnnotationBbox(imagebox, (data_x, temp_y + 1.5), frameon=False)
        ax.add_artist(ab)

# Iterate and apply icons where data exists
for date, row in df.iterrows():
    if pd.notna(row["temp_powietrza"]) and pd.notna(row["kod_pogody"]):
        wklej_ikone_pogody(ax1, date, row["temp_powietrza"], int(row["kod_pogody"]))

# Formatting
ax1.set_xlabel("Date", fontsize=12, labelpad=10)
ax1.set_ylabel("Temperature (°C)", fontsize=11, fontweight="bold")
ax1.set_title("Larnaca Weather Report (Icons from Noto Color Emoji)", fontsize=14, fontweight="bold", pad=15)
ax1.grid(True, linestyle=":", alpha=0.6)
ax1.legend(loc="upper left")

# Expand Y-axis limits so icons aren't cut off by the frame
if not df["temp_powietrza"].dropna().empty:
    ax1.set_ylim(df["temp_powietrza"].min() - 5, df["temp_powietrza"].max() + 5)

plt.xticks(df.index, df.index.strftime("%d.%m\n%a"), rotation=0, ha="center")
plt.tight_layout()

output_temp = os.path.join(base_dir, f"Larnaca_Air_temp_{date_str_min}_{date_str_max}.pdf")
generated_images.append({"path": output_temp, "caption": "Air Temperature and Weather Conditions."})
plt.savefig(output_temp)
plt.close()  # Clear memory
print(f"[SUCCESS] Temperature plot saved to: {output_temp}")

# ==============================================================================
# 4. PLOTTING CLOUDINESS AND HUMIDITY (DUAL Y-AXIS)
# ==============================================================================
fig, ax1 = plt.subplots(figsize=(14, 9))  # Fixed to share exact timeline format

color_cloud = "#a1c4fd"
bars = ax1.bar(
    df.index,
    df["stopien_zachmurzenia"],
    color=color_cloud,
    alpha=0.7,
    label="Cloudiness (%)",
    width=0.5,
)

ax1.set_xlabel("Date", fontsize=12, labelpad=10)
ax1.set_ylabel("Cloudiness (%)", color="#4a90e2", fontsize=12, fontweight="bold")
ax1.tick_params(axis="y", labelcolor="#4a90e2")
ax1.set_ylim(0, 105)

# Dual axis for humidity
ax2 = ax1.twinx()
color_humidity = "#2af598"
line, = ax2.plot(
    df.index,
    df["wilgotnosc"],
    color=color_humidity,
    linewidth=2.5,
    marker="o",
    label="Humidity (%)",
)

ax2.set_ylabel("Relative Humidity (%)", color="#10b981", fontsize=12, fontweight="bold")
ax2.tick_params(axis="y", labelcolor="#10b981")
ax2.set_ylim(0, 105)

# Shared legend
lines_labels = [bars, line]
labels = [l.get_label() for l in lines_labels]
ax1.legend(lines_labels, labels, loc="upper left", fontsize=10)

plt.title("Cloudiness and Relative Humidity Trends", fontsize=14, fontweight="bold", pad=15)
ax1.grid(True, axis="y", linestyle="--", alpha=0.3)

# Fix: Use df.index to align perfectly with the bar chart
plt.xticks(df.index, df.index.strftime("%d.%m\n%a"), rotation=0, ha="center")
plt.tight_layout()

output_hum = os.path.join(base_dir, f"Larnaca_humidity_cloud_{date_str_min}_{date_str_max}.pdf")
generated_images.append({"path": output_hum, "caption": "Cloudiness and Humidity Levels."})
plt.savefig(output_hum)
plt.close()
print(f"[SUCCESS] Cloudiness/Humidity plot saved to: {output_hum}")

# ==============================================================================
# 5. CREATING A POLAR PLOT (WIND ROSE)
# ==============================================================================
if not df["kierunek_wiatru"].dropna().empty:
    # Convert angles >= 337.5° into negative bounds to merge with North sector
    degrees = df["kierunek_wiatru"].apply(lambda x: x - 360 if x >= 337.5 else x)

    bins = np.linspace(-22.5, 337.5, 9)
    labels_rose = ["N", "N-E", "E", "S-E", "S", "S-W", "W", "N-W"]

    counts_series = pd.cut(degrees, bins=bins, labels=labels_rose).value_counts()
    counts = [counts_series[label] for label in labels_rose]

    # Convert to standard meteorological wind rose geometry
    angles = np.linspace(0, 2 * np.pi, 8, endpoint=False)
    angles = np.concatenate((angles, [angles[0]]))
    counts = np.concatenate((counts, [counts[0]]))

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"projection": "polar"})
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)

    ax.plot(angles, counts, color="blue", linewidth=2, marker="o")
    ax.fill(angles, counts, color="skyblue", alpha=0.4)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels_rose)

    plt.title("Classic Wind Rose (Last 15 Days)", va="bottom", pad=20)
    plt.tight_layout()

    output_wind = os.path.join(base_dir, f"Larnaca_wind_rose_{date_str_min}_{date_str_max}.pdf")
    generated_images.append({"path": output_wind, "caption": "15-Day Wind Rose Chart."})
    plt.savefig(output_wind)
    plt.close()
    print(f"[SUCCESS] Wind rose plot saved to: {output_wind}")

# Saving the list of pictures to a JSON file
with open(os.path.join(base_dir, "generated_images.json"), "w", encoding="utf-8") as f:
    json.dump(generated_images, f, ensure_ascii=False, indent=4)
print("The list of plots have writen to generated_images.json")
