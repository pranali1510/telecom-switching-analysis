"""Download TRAI monthly press-release PDFs and pull out the MNP request count.

Input : data/raw/trai_pdf_list.csv with columns month,url
Output: data/clean/trai_mnp_monthly.csv  (+ rows flagged 'needs_manual_check')
Text extracted from these PDFs is often jumbled, so every row records whether
the pattern matched. Never silently fill a gap; check flagged rows by hand.
"""
import re
import time
from pathlib import Path

import pandas as pd
import requests

import config

MNP_PATTERN = re.compile(
    r"([\d.,]+)\s*million\s+subscribers\s+submitted\s+their\s+requests\s+for\s+"
    r"Mobile\s+Number\s+Portability",
    re.IGNORECASE | re.DOTALL,
)
MONTH_PATTERN = re.compile(
    r"Telecom\s+Subscription\s+Data\s+at\s+the\s+end\s+of\s+([A-Za-z]+\s+\d{4})",
    re.IGNORECASE,
)


def parse_text(text: str) -> dict:
    mnp = MNP_PATTERN.search(text)
    month = MONTH_PATTERN.search(text)
    return {
        "report_month_in_text": month.group(1) if month else None,
        "mnp_requests_million": float(mnp.group(1).replace(",", "")) if mnp else None,
    }


def pdf_to_text(path: Path) -> str:
    import pdfplumber

    with pdfplumber.open(path) as pdf:
        return "\n".join((page.extract_text() or "") for page in pdf.pages)


def main():
    Path(config.RAW_PDF_DIR).mkdir(parents=True, exist_ok=True)
    Path(config.CLEAN_DIR).mkdir(parents=True, exist_ok=True)
    todo = pd.read_csv(config.TRAI_PDF_LIST)
    out = []
    for _, row in todo.iterrows():
        pdf_path = Path(config.RAW_PDF_DIR) / (re.sub(r"\W+", "_", str(row["month"])) + ".pdf")
        if not pdf_path.exists():
            resp = requests.get(row["url"], timeout=60)
            resp.raise_for_status()
            pdf_path.write_bytes(resp.content)
            time.sleep(config.SLEEP_SECONDS)
        parsed = parse_text(pdf_to_text(pdf_path))
        parsed.update(month=row["month"], source_url=row["url"])
        parsed["status"] = "ok" if parsed["mnp_requests_million"] is not None else "needs_manual_check"
        out.append(parsed)
    pd.DataFrame(out).to_csv(Path(config.CLEAN_DIR) / "trai_mnp_monthly.csv", index=False)
    print(pd.DataFrame(out)[["month", "mnp_requests_million", "status"]])


if __name__ == "__main__":
    main()
