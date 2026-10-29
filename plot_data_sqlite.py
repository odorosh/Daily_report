import os
import sqlite3
import pandas as pd
import numpy as np

import json

generated_images = []

# "Agg" rendering engine as its backend, to avoid errors in graphics in Linux
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox


# Path to working script
base_dir = os.path.dirname(os.path.abspath(__file__))


# ==========================================
# 1. Reading data from SQLITE with PANDAS
# ==========================================
db_path = os.path.join(base_dir, "pogoda_larnaca.db")
conn = sqlite3.connect(db_path)

# Request to DB. Sorting by data
query = "SELECT data_pomiaru, temp_powietrza, wilgotnosc,  sila_wiatru, kierunek_wiatru, stopien_zachmurzenia, kod_pogody, temp_morza FROM pogoda_i_morze ORDER BY data_pomiaru;"

# Pandas converts column 'data_pomiaru' to data format
df = pd.read_sql_query(query, conn, parse_dates=["data_pomiaru"])
conn.close()

if df.empty:
    print("Database is empty!")
    exit()

# Date is an index
df.set_index("data_pomiaru", inplace=True)


# ==========================================
# 2. Treat the gap in data
# ==========================================
# Make continius series of the dates in DB
#
full_index = pd.date_range(
    start=df.index.max() - pd.Timedelta(days=14), end=df.index.max(), freq="D"
)

print(f"df.index.min() = {df.index.min()}")
print(f"df.index.max() = {df.index.max()}")

print(f"full_index = {full_index}")


# Gaps in data series ar filled with NaN (not a number)
df = df.reindex(full_index)

# ==========================================
# 3. Make plots (MATPLOTLIB) weather condition and air temperature
# ==========================================
fig, ax1 = plt.subplots(figsize=(14, 9))


# Main pltot of air temperature (for absent data - NaN)
ax1.plot(
    df.index,
    df["temp_powietrza"],
    color="#d32f2f",
    marker="o",
    markersize=5,
    linewidth=2,
    label="Temperature (°C)",
)


# Function to put color icons on the plot
def wklej_ikone_pogody(ax, data_x, temp_y, wmo_code):
    icon_path = base_dir + f"/icons/{wmo_code}.png"
    print("icon_path = ", icon_path)
    if os.path.exists(icon_path):
        img = plt.imread(icon_path)
        # zoom=0.25 adjast 128x128 icone to scale
        imagebox = OffsetImage(img, zoom=0.25)
        # Pup icons a little over temperature point (np. temp + 1.5 stopnia)
        ab = AnnotationBbox(imagebox, (data_x, temp_y + 1.5), frameon=False)
        ax.add_artist(ab)


# Iterating through rows and applying icons
for date, row in df.iterrows():
    if pd.notna(row["temp_powietrza"]) and pd.notna(row["kod_pogody"]):
        wklej_ikone_pogody(ax1, date, row["temp_powietrza"], int(row["kod_pogody"]))

# Formatting the top panel
ax1.set_xlabel("Date", fontsize=12, labelpad=10)
ax1.set_ylabel("Temperatura (°C)", fontsize=11, fontweight="bold")
ax1.set_title(
    "Weather raport (color icons from Noto Color Emoji)",
    fontsize=14,
    fontweight="bold",
    pad=15,
)
ax1.grid(True, linestyle=":", alpha=0.6)
ax1.legend(loc="upper left")

# Important: We are increasing the upper limit of the Y-axis so that the icons are not cut off by the chart frame.
ax1.set_ylim(df["temp_powietrza"].min() - 5, df["temp_powietrza"].max() + 5)


# Formatting the timeline (X-axis) for both panels
plt.xticks(df.index, df.index.strftime("%d.%m\n%a"), rotation=0, ha="center")

# Automatic adjustment and saving to a file
plt.tight_layout()

output_file = os.path.join(
    base_dir,
    "Larnaca_Ait_temp_"
    + df.index.min().strftime("%Y-%m-%d")
    + "_"
    + df.index.max().strftime("%Y-%m-%d")
    + ".pdf",
)
caption = "Weather chart."

generated_images.append({"path": output_file, "caption": caption})

plt.savefig(output_file)
print(f"Success! The chart with colored icons has been saved as '{output_file}'.")


# ==========================================
# 6 Creating a polar plot
# ==========================================

# Creating a graph object
fig, ax1 = plt.subplots(figsize=(10, 6))

# 1. Plot cloud cover as bar charts (using the first axis, ax1)
color_cloud = "#a1c4fd"  # soft blue
bars = ax1.bar(
    df.index,
    df["stopien_zachmurzenia"],
    color=color_cloud,
    alpha=0.7,
    label="Cloudness (%)",
    width=0.5,
)

# Left Y-axis settings (for cloud cover)
ax1.set_xlabel("Date", fontsize=14, labelpad=10)
ax1.set_ylabel("Cloudness (%)", color="#4a90e2", fontsize=12)
ax1.tick_params(axis="y", labelcolor="#4a90e2")
ax1.set_ylim(0, 105)

# We explicitly tell the plot to show all days from `df.index` on the X-axis, even if they are empty.
ax1.set_xticks(range(len(df.index)))
# ----------------------------------------

# 2. We create a second Y-axis that shares the same X-axis.
ax2 = ax1.twinx()

print("df[wilgotnosc] = ", df["wilgotnosc"])
print("df[stopien_zachmurzenia] = ", df["stopien_zachmurzenia"])

# Plot humidity as a line (using the second axis, ax2)
color_humidity = "#2af598"  # greenish-blue
(line,) = ax2.plot(
    df.index,
    df["wilgotnosc"],
    color=color_humidity,
    linewidth=2.5,
    marker="o",
    label="Humidity (%)",
)

# Configuring the right Y-axis (for humidity)
ax2.set_ylabel("Relative humidity (%)", color="#10b981", fontsize=12)
ax2.tick_params(axis="y", labelcolor="#10b981")
ax2.set_ylim(0, 105)

# 3. Adding a shared element for the columns and the line
lines_labels = [bars, line]
labels = [l.get_label() for l in lines_labels]
ax1.legend(lines_labels, labels, loc="upper left", fontsize=10)

# Settings general appearance
plt.title(
    "Plot of cloudness and humidity",
    fontsize=14,
    fontweight="bold",
    pad=15,
)
ax1.grid(True, axis="y", linestyle="--", alpha=0.3)

# Formatowanie osi czasu (X) dla obu paneli
plt.xticks(df.index, df.index.strftime("%d.%m\n%a"), rotation=0, ha="center")

# Automatic element alignment and display
plt.tight_layout()

# Save the picture to the file
output_file = os.path.join(
    base_dir,
    "Larnaca_humidity_cloud_"
    + df.index.min().strftime("%Y-%m-%d")
    + "_"
    + df.index.max().strftime("%Y-%m-%d")
    + ".pdf",
)

caption = "Cloudness and humidity."

# Save the information about file to json
generated_images.append({"path": output_file, "caption": caption})


plt.savefig(output_file)
print(f"Success! The chart with colored icons has been saved as '{output_file}'.")


# ==========================================
# 5 Creating a polar plot
# ==========================================

# --- 1. DATA PREPARATION (Grouping degrees by 8 cardinal/intercardinal directions) ---

print(df["kierunek_wiatru"])

# We define the boundaries for 8 sectors (from -22.5° to 337.5°)
# We convert values ​​>= 337.5 into the negative range to combine them with North.
degrees = df["kierunek_wiatru"].apply(lambda x: x - 360 if x >= 337.5 else x)

bins = np.linspace(-22.5, 337.5, 9)
labels = ["N", "N-E", "E", "S-E", "S", "S-W", "W", "N-W"]

# We sort the degrees into bins and count the number of days for each direction.
counts_series = pd.cut(degrees, bins=bins, labels=labels).value_counts()

# Verifying the correct meteorological order of the cardinal directions
counts = [counts_series[label] for label in labels]

# --- 2. CONSTRUCTING A CLASSICAL WIND ROSE ---

# 8 angles in radians for display
angles = np.linspace(0, 2 * np.pi, 8, endpoint=False)

# Close the chart contour (add the first point to the end)
angles = np.concatenate((angles, [angles[0]]))
counts = np.concatenate((counts, [counts[0]]))

# Creating a polar plot
fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"projection": "polar"})

# Orientation: North (N) at the top, clockwise movement
ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)

# Draw lines and fill the inner area
ax.plot(angles, counts, color="blue", linewidth=2, marker="o")
ax.fill(angles, counts, color="skyblue", alpha=0.4)

# Add text labels for the cardinal directions
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels)

plt.title("Classic wind rose for 15 days", va="bottom", pad=20)

# Automatic adjustment and saving to a high-quality file
plt.tight_layout()

output_file = os.path.join(
    base_dir,
    "Larnaca_wind_rose_"
    + df.index.min().strftime("%Y-%m-%d")
    + "_"
    + df.index.max().strftime("%Y-%m-%d")
    + ".pdf",
)

caption = "Wind rose."

generated_images.append({"path": output_file, "caption": caption})


plt.savefig(output_file)
print(f"Success! The chart with colored icons has been saved as '{output_file}'.")


# ==========================================
# 4. Creating a plot (MATPLOTLIB) sea water temperature
# ==========================================
fig, ax1 = plt.subplots(figsize=(14, 6))


# Main temperature line (will be interrupted at gaps, thanks to NaN)
ax1.plot(
    df.index,
    df["temp_morza"],
    color="#000080",
    marker="o",
    markersize=5,
    linewidth=2,
    label="Temperature (°C)",
)


# Formatting the top panel
ax1.set_xlabel("Date", fontsize=14, labelpad=10)
ax1.set_ylabel("Sea water temperature (°C)", fontsize=14, fontweight="bold")
# ax1.set_title('Automatic weather raport', fontsize=14, fontweight='bold', pad=15)
ax1.grid(True, linestyle=":", alpha=0.6)
ax1.legend(loc="upper left")

# Important: We are increasing the upper limit of the Y-axis so that the icons are not cut off by the chart frame.
ax1.set_ylim(df["temp_morza"].min() - 5, df["temp_morza"].max() + 5)


# Formatting the timeline (X-axis) for both panels
plt.xticks(df.index, df.index.strftime("%d.%m\n%a"), rotation=0, ha="center")

# Automatic adjustment and saving to a high-quality file
plt.tight_layout()

output_file = os.path.join(
    base_dir,
    "Larnaca_Sea_temp_"
    + df.index.min().strftime("%Y-%m-%d")
    + "_"
    + df.index.max().strftime("%Y-%m-%d")
    + ".pdf",
)

caption = "Plot of sea temperature."

generated_images.append({"path": output_file, "caption": caption})


plt.savefig(output_file)
print(f"Success! The chart with colored icons has been saved as '{output_file}'.")


# Saving the list to a JSON file
with open(os.path.join(base_dir, "generated_images.json"), "w", encoding="utf-8") as f:
    json.dump(generated_images, f, ensure_ascii=False, indent=4)
print("The list of plots have writen to generated_images.json")
