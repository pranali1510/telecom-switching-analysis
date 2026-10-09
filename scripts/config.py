"""Project settings. Edit the app IDs and PDF list before running."""

# Play Store app IDs: open the app's Play Store page and copy the text after "id=" in the URL.
# VERIFY every ID below yourself; package names can change.
APPS = {
    "Jio": "com.jio.myjio",
    "Airtel": "com.myairtelapp",
    "Vi": "com.mventus.selfcare.activity",
    "BSNL": "TODO_copy_from_play_store_url",
}

REVIEWS_PER_APP = 3000      # keep modest and polite
SLEEP_SECONDS = 2           # pause between requests
RAW_REVIEWS_DIR = "data/raw/reviews"
RAW_PDF_DIR = "data/raw/trai_pdfs"
CLEAN_DIR = "data/clean"
# Fill this CSV (columns: month,url) from TRAI's press release page.
TRAI_PDF_LIST = "data/raw/trai_pdf_list.csv"
