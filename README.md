# Why Are Indian Mobile Subscribers Switching Operators?

Real-data analysis combining TRAI monthly subscription reports (MNP requests, subscriber movement) with public Play Store reviews of operator apps.

## Run order
1. `pip install -r requirements.txt`
2. Fill `data/raw/trai_pdf_list.csv` (month,url) from TRAI's press release page.
3. Run from the project root: `python scripts/extract_trai_mnp.py`
4. Edit app IDs in `scripts/config.py`, then `python scripts/scrape_play_reviews.py`
5. Record every issue you find in `docs/cleaning_log_template.md`.

## Notes
- Reviewer names are dropped; only public review text, rating, date and app version are kept.
- Rows flagged `needs_manual_check` in the TRAI output must be checked by hand against the PDF.
