# Daily_report

Create daily report of two weeks weather condition.

The weather is recorded for Larnaca (Cyprus) by OpenMeteo service

The weather condition are writeng to SQLite database.

The plots of last 15 days are created with Matplotlib(python)

The plots are puted to pdf document by latex.

## Using

Script "cron_script" put to cron directory cron.daily

Change path to dicrectory where scripts "larnaca_open_meteo_sqlite.py" "plot_data_sqlite.py" "make_tex.py". Also in the directory shoud be file "pogoda_larnaca.db" of SQLite


The report is produced daily.
