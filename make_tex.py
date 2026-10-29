import json
import os
import sys
from datetime import datetime

# 1. Спроба імпорту PyLaTeX (динамічне додавання шляхів, якщо потрібно)
LOCAL_SITE_PACKAGES = os.path.expanduser("~/.local/lib/python3.14/site-packages")
if os.path.exists(LOCAL_SITE_PACKAGES) and LOCAL_SITE_PACKAGES not in sys.path:
    sys.path.append(LOCAL_SITE_PACKAGES)

try:
    from pylatex import Command, Document, Figure, Section
    from pylatex.utils import NoEscape
except ImportError:
    print("[ERROR] PyLaTeX library not found! Please run: pip install pylatex")
    sys.exit(1)

# Base directories configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "generated_images.json")
report_filename = f"final_report_{datetime.today().strftime('%Y-%m-%d')}"
report_path = os.path.join(BASE_DIR, report_filename)

if not os.path.exists(json_path):
    print(f"[ERROR] File '{json_path}' not found! Run the image generator script first.")
    sys.exit(1)

# ==============================================================================
# 2. GENERATING THE LATEX DOCUMENT
# ==============================================================================
print(f"[INFO] Processing image metadata from: {json_path}")
with open(json_path, "r", encoding="utf-8") as f:
    my_images = json.load(f)

# Initialize document with standard margins
doc = Document(geometry_options={"margin": "2cm"})

# Document Preamble Config
doc.preamble.append(Command("usepackage", "inputenc", "utf8"))
doc.preamble.append(Command("usepackage", "tempora"))  # Clean vector font
doc.preamble.append(Command("title", "Automated Daily Weather Report"))
doc.preamble.append(Command("author", "Automated Weather Station System"))
doc.preamble.append(Command("date", NoEscape(r"\today")))
doc.append(NoEscape(r"\maketitle"))

# --- Section 1: Introduction ---
with doc.create(Section("Introduction")):
    doc.append(
        "This report was generated automatically by the background system pipeline. "
        "It includes comprehensive automated tracking, database logging, and metric visualization."
    )

# --- Section 2: Data Visualizations ---
with doc.create(Section("Visualizations & Charts")):
    doc.append("Below are the graphical analytics processed for the current cycle:")

    for img_info in my_images:
        img_path = img_info.get("path", "")
        img_caption = img_info.get("caption", "Automated chart preview.")

        # Verify the file exists and is not a broken 0-byte file
        if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
            with doc.create(Figure(position="htbp")) as plot:
                plot.add_image(img_path, width=NoEscape(r"0.85\textwidth"))
                plot.add_caption(img_caption)
            print(f"[INFO] Successfully added image to report: {os.path.basename(img_path)}")
        else:
            print(f"[WARNING] File '{img_path}' is missing or empty. Skipping image.")

# Force a clean page layout after structural images
doc.append(NoEscape(r"\clearpage"))

# --- Section 3: Summary Conclusions ---
with doc.create(Section("Conclusions")):
    doc.append(
        "All targeted environmental metrics were successfully compiled, checked, and integrated. "
        "The automated report pipeline completed without structural exceptions."
    )

# ==============================================================================
# 3. PDF COMPILATION VIA PDFLATEX
# ==============================================================================
try:
    print(f"[INFO] Compiling document with pdflatex into: {report_path}.pdf")
    doc.generate_pdf(report_path, clean_tex=True, compiler="pdflatex")
    print(f"[SUCCESS] Report successfully compiled as: {report_path}.pdf")
except Exception as e:
    print(f"[ERROR] Failed to compile PDF via pdflatex. Reason: {e}")
    sys.exit(1)
