# Daily Weather Report Automation

An automated Python system that records weather conditions for Larnaca (Cyprus) and generates a visual 15-day retrospective PDF report every day.

## 📊 How It Works
1. **Data Collection:** Fetches weather data for Larnaca via the [OpenMeteo API](https://open-meteo.com).
2. **Storage:** Saves the collected weather metrics into a local **SQLite** database (`pogoda_larnaca.db`).
3. **Visualization:** Generates weather plots for the last 15 days using **Matplotlib**.
4. **Report Generation:** Compiles the charts and data into a professional PDF document using **LaTeX**.

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Database:** SQLite
* **Libraries:** Matplotlib, Requests (or modern HTTP client)
* **Typesetting:** LaTeX

## 💻 Project Structure
* `larnaca_open_meteo_sqlite.py` — Fetches data from OpenMeteo and stores it in SQLite.
* `plot_data_sqlite.py` — Extracts data from the DB and creates Matplotlib charts.
* `make_tex.py` — Generates the LaTeX file and compiles it into the final PDF report.
* `cron_script` — Automation shell script for daily execution.

## ⚙️ Installation & Usage

### 1. Prerequisites
Make sure you have Python installed along with a working LaTeX distribution (like TeX Live or MiKTeX) capable of running `pdflatex` from the terminal.

### 2. Setup Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 3. Automation with Cron
To generate the report automatically every day, configure the system cron daemon:

1. Move or link the `cron_script` into your daily cron directory:
   ```bash
   cp cron_script /etc/cron.daily/
   ```
2. Open the `cron_script` and update the absolute paths to point to your working directory where the Python scripts and `pogoda_larnaca.db` reside.
3. Ensure the script has execution permissions:
   ```bash
   chmod +x /etc/cron.daily/cron_script
   ```

The system will now run seamlessly in the background and produce your report daily.


## 🎨 Assets & Credits

* **Weather Icons:** The graphical weather markers located in the `icons/` directory were generated using Google's [Noto Color Emoji](https://github.com) font (specifically the `Noto-COLRv1.ttf` format). 
* **License:** Noto Color Emoji is licensed under the [SIL Open Font License, Version 1.1](https://sil.org). You are free to use these assets in accordance with the license terms.
