"""Download TRAI monthly press-release PDFs and pull out the MNP request count.

Input : data/raw/trai_pdf_list.csv with columns month,url[,manual_mnp_million]
Output: data/clean/trai_mnp_monthly.csv

status values:
  ok                  value read automatically from the PDF
  manual_entry        PDF has no readable MNP text; value typed in by hand
  needs_manual_check  not found and no manual value supplied
"""
import re
import time
from pathlib import Path

import pandas as pd
import requests

import config

MNP_PATTERN = re.compile(
    r"([\d.,]+)\s*million\s+subscribers\s+submitted\s+(?:their\s+)?requests?\s+for\s+"
    r"Mobile\s+Number\s+Portability",
    re.IGNORECASE | re.DOTALL,
)
MONTH_PATTERN = re.compile(
    r"Telecom\s+Subscription\s+Data\s+(?:at\s+the\s+end\s+of|as\s+on)\s+"
    r"(?:\d{1,2}\s*(?:st|nd|rd|th)?\s+)?([A-Za-z]+\s+\d{4})",
    re.IGNORECASE,
)

MNP_COMPACT = re.compile(
    r"(\d+\.\d+)millionsubscriberssubmitted(?:their)?requests?forMobileNumberPortability",
    re.IGNORECASE,
)
MONTH_COMPACT = re.compile(
    r"TelecomSubscriptionData(?:attheendof|ason)(?:\d{1,2}(?:st|nd|rd|th)?)?([A-Za-z]+)(\d{4})",
    re.IGNORECASE,
)


def parse_text(text: str) -> dict:
    mnp = MNP_PATTERN.search(text)
    month = MONTH_PATTERN.search(text)
    mnp_value = float(mnp.group(1).replace(",", "")) if mnp else None
    month_text = month.group(1) if month else None
    if mnp_value is None or month_text is None:
        # second attempt: strip all whitespace, in case extraction added odd gaps
        squeezed = re.sub(r"\s+", "", text)
        if mnp_value is None:
            m = MNP_COMPACT.search(squeezed)
            if m:
                mnp_value = float(m.group(1))
        if month_text is None:
            m = MONTH_COMPACT.search(squeezed)
            if m:
                month_text = f"{m.group(1)} {m.group(2)}"
    return {"report_month_in_text": month_text, "mnp_requests_million": mnp_value}

def pdf_to_text(path: Path) -> str:
    from pypdf import PdfReader

    text = "\n".join((p.extract_text() or "") for p in PdfReader(path).pages[:3])
    if MNP_PATTERN.search(text):
        return text
    # fallback for PDFs where pypdf can't find the sentence
    import pdfplumber

    with pdfplumber.open(path) as pdf:
        return "\n".join((p.extract_text() or "") for p in pdf.pages[:2])


def main():
    Path(config.RAW_PDF_DIR).mkdir(parents=True, exist_ok=True)
    Path(config.CLEAN_DIR).mkdir(parents=True, exist_ok=True)
    todo = pd.read_csv(config.TRAI_PDF_LIST, dtype={"month": str})
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
        if parsed["mnp_requests_million"] is not None:
            parsed["status"] = "ok"
        else:
            manual = row.get("manual_mnp_million")
            if pd.notna(manual):
                parsed["mnp_requests_million"] = float(manual)
                parsed["status"] = "manual_entry"
            else:
                parsed["status"] = "needs_manual_check"
        out.append(parsed)
    result = pd.DataFrame(out)
    result.to_csv(Path(config.CLEAN_DIR) / "trai_mnp_monthly.csv", index=False)
    print(result[["month", "report_month_in_text", "mnp_requests_million", "status"]])


if __name__ == "__main__":
    main()