import pdfplumber
from pathlib import Path

pdf_path = Path("../data/timetables/BBA_Timetable.pdf")

with pdfplumber.open(pdf_path) as pdf:
    all_text = []

    for page_number, page in enumerate(pdf.pages, start=1):
        text = page.extract_text()

        if text:
            all_text.append(
                f"--- PAGE {page_number} ---\n{text}"
            )

output_path = Path("../data/timetables/BBA_extracted.txt")

output_path.write_text(
    "\n\n".join(all_text),
    encoding="utf-8"
)

print("PDF extraction completed!")
print("Saved to:", output_path)
