import os
import json

import sys
sys.path.append('/home/user/.local/lib/python3.14/site-packages')

from pylatex import Document, Section, Figure, Command
from pylatex.utils import NoEscape
from datetime import datetime


# Path to the resulting file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print("BASE_DIR = ", BASE_DIR)
json_path = os.path.join(BASE_DIR, "generated_images.json")
print("json_path  = ", json_path )
raport_path = os.path.join(BASE_DIR, "final_report_"+datetime.today().strftime('%Y-%m-%d'))
print("raport_path  = ", raport_path)

if os.path.exists(json_path):
    # We read the list of images left by the previous script.
    with open(json_path, "r", encoding="utf-8") as f:
        my_images = json.load(f)
    print(f"List of files read from JSON: {my_images}")

    # Create document
    doc = Document(geometry_options={"margin": "2cm"})

    doc.preamble.append(Command('usepackage', 'inputenc', 'utf8'))      # Вхідне кодування тексту

    # Loading the Tempora vector font package
    doc.preamble.append(Command('usepackage', 'tempora'))

    # Metadata and Title Creation
    doc.preamble.append(Command('title', 'Automated Technical Report'))
    doc.preamble.append(Command('author', f'Created by {os.path.basename(__file__)}'))
    doc.preamble.append(Command('date', NoEscape(r'\today')))
    doc.append(NoEscape(r'\maketitle'))

    # Main text of the report
    with doc.create(Section('Introduction')):
        doc.append('This report was generated automatically using a Python script and the pdflatex system.')

    with doc.create(Section('Visualization and drawings')):
        doc.append('Below are the graphic materials attached to the report:')

        # Loop for pictures (now iterating over objects from JSON)
        for img_info in my_images:
            img_path = img_info['path']
            # Get the signature from the JSON; if it’s missing, use the default one.
            img_caption = img_info.get('caption', 'Image without a description.')

            if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
                with doc.create(Figure(position='htbp')) as plot:
                    plot.add_image(img_path, width=NoEscape(r'0.85\textwidth'))
                    # We insert our specific dynamic signature
                    plot.add_caption(img_caption)
            else:
                print(f"Warning: File '{img_path}' is missing or empty. Skipped..")

    # print next sectuion after pictures
    doc.append(NoEscape(r'\clearpage'))

    with doc.create(Section('Conclusions')):
        doc.append(f'All provided images were successfully imported into the document. \n The report structure is ready.')

    # 6. Compilation using pdflatex
    # clean_tex=True will automatically delete temporary files .aux, .log
    doc.generate_pdf(raport_path, clean_tex=True, compiler='pdflatex')
    print(f"\n[SUCCESS] Report successfully generated via pdflatex as: {raport_path}.pdf")
else:
    print(f"[Error] File {json_path} not found! Run the image generator first.")
