# Data Cleaning & Quality Log: Telecom Switching Analysis

## 1. TRAI MNP extraction and PDF parsing
**Component:** `scripts/extract_trai_mnp.py`, `data/raw/trai_pdf_list.csv`

| # | Issue | Rows affected | Decision | Reason |
|---|-------|---------------|----------|--------|
| 1 | The 2026-02 row pointed to the March 2026 release | 1 | Replaced the link and deleted the cached PDF | Caught by comparing the month in the PDF text with the target month |
| 2 | December 2025 PDF has no searchable text layer (browser search found 0 matches) | 1 | Typed 16.12 million from the PDF; row flagged `manual_entry` | Automatic extraction was impossible; value checked by eye on the page |
| 3 | February 2026 PDF text was extracted with odd spacing, so the first patterns failed | 1 | Added a whitespace-insensitive fallback; it read 14.47, matching the manual check | Fix is reusable for other months |
| 4 | 2025-08 and 2025-10 both show 15.05 million | 2 | Verified against each release; kept | Coincidence, not a duplicate ingestion |
| 5 | 2026-01 and 2026-07 both show 15.98 million | 2 | Verified against the TRAI releases; kept | Coincidence, confirmed in TRAI's July 2026 release |
| 6 | `report_month_in_text` is blank for 2025-12 and 2026-02 | 2 | Use the `month` column (converted to a real date in `trai_monthly_for_bi.csv`) for charts | The text column depends on PDF extraction |
| 7 | Series breaks: Tata Teleservices wireline counting change (June 2025); Bharti Airtel M2M counting change (until November 2025) | n/a | Noted; MNP counts unaffected; subscriber-base charts need a note | Definitions changed, not customer behaviour |
| 8 | August 2026 release (PR 125/2026) added; reads 15.83 million automatically | 1 | Kept, status ok | Extends the series so it overlaps the review window |

## 2. Play Store review collection
**Component:** `scripts/config.py`, `scripts/scrape_play_reviews.py`

| # | Issue | Rows affected | Decision | Reason |
|---|-------|---------------|----------|--------|
| 9 | Guessed BSNL package IDs returned 0 reviews | all BSNL | Looked up the ID from the Play Store URL (`com.rma.bsnl`); about 2,900 reviews collected | Package IDs must be copied from the store listing |
| 10 | Scraper uses `lang="en"`; romanised Hindi and regional-language reviews are underrepresented | unknown | Kept; documented as a limitation | Keeps classification feasible; biases the sample |
| 11 | Review windows differ by operator (Jio, Vi: about 9 days; Airtel: 24; BSNL: 68) | all | Compare shares, not counts; no trend analysis | Newest-3,000 sampling covers different time spans |
| 12 | Reviewer names and avatars | all | Dropped `userName` and `userImage` | Personal data not needed |

## 3. Classified-reviews file, classifier and validation
**Component:** `scripts/classify_reviews.py`, `scripts/make_label_sample.py`, `scripts/evaluate_classifier.py`

| # | Issue | Rows affected | Decision | Reason |
|---|-------|---------------|----------|--------|
| 13 | `reviews_classified.csv` was damaged after creation: not valid UTF-8, about 1,640 rows with garbled text, dates reformatted and seconds dropped | about 1,640 text rows, all dates | Regenerated from the intact `reviews_stage1.csv`; output now written as UTF-8 with BOM; stopped opening outputs in Excel | Likely an Excel round trip; the stage-1 file was unaffected |
| 14 | First classifier labelled praise as complaints: 1,659 of 5,790 reviews in complaint themes were 4-5 stars, and 1,025 1-2 star reviews were "General Feedback" | 2,684 | Only 1-3 star reviews of at least 5 characters are classed as complaints; rules use word boundaries | Substring matches and first-match ordering caused the errors |
| 15 | Very short reviews (under 5 characters) | 2,195 before the fix | 1-3 star ones labelled "Too short to classify"; 4-5 star ones "Not a complaint" | Not enough text to classify |
| 16 | First validation was not blind (labels followed the predicted theme), giving a meaningless 97.3% | 150 | Discarded the figure; sample regenerated with predictions hidden | A check that sees the answer measures nothing |
| 17 | Blind round 1 (rules v1, 150 reviews) scored 56.7%. Errors: app complaints pushed into Billing, network reviews landing in Other, inconsistent labels on vague or multi-issue reviews (accuracy fell from about 60% on short reviews to 41% on reviews over 200 characters) | 150 | Rewrote the rules as v2: weighted keywords, earliest-problem tie-break | Targets the main error patterns |
| 18 | A trained text model (TF-IDF with logistic regression) was cross-validated on the 150 labels and scored 57.7%, no better than the keywords | 150 | Not used | Too few, too noisy labels to beat the baseline |
| 19 | Round 2 (rules v2, 100 fresh reviews) scored 71.0% (95% interval 61% to 79%) | 100 | Reported both rounds | The v2 rules were tuned on round 1, so only round 2 is a fair test |
| 20 | Round-2 labels were assigned with AI assistance (Gemini) using a written guide | 100 | Spot-checked 25 labels myself: agreed with 25 of 25. Disclosed in the README | The score measures agreement with those labels, not a fully human answer key |
| 21 | Customer Support is rare (6 of 100 labelled) and was unreliable (precision 20%) | 6 | No conclusion drawn about support; flagged on the dashboard | Too few examples to measure |

## 4. Environment and database loading
**Component:** `requirements.txt`, `scripts/load_to_mysql.py`

| # | Issue | Decision | Reason |
|---|-------|----------|--------|
| 22 | `pypdf` missing from `requirements.txt` | Added | Clone-and-run failed without it |
| 23 | `sqlalchemy` and `pymysql` missing from `requirements.txt` | Added | The MySQL loader needs them |
| 24 | `PermissionError` when overwriting `reviews_stage1.csv` | Closed the program holding the file | A preview window locked it |
| 25 | Loader read the file as `latin-1` and used `if_exists="replace"` with no keys | Rewrote: UTF-8 read, `utf8mb4` tables, `review_id` and `month_period` as primary keys, tables rebuilt on each run | Re-runs must not duplicate rows and text must not be altered |
| 26 | Database password was hard-coded in the script | Moved to environment variables | Credentials must not be committed |

## 5. Dashboard (Power BI)

| # | Issue | Decision | Reason |
|---|-------|----------|--------|
| 27 | The MNP line chart grouped by calendar month, so June 2025 and June 2026 were added together (spikes above 28 million) | Turned off auto date/time and plotted `month_date` as a plain date axis | The date hierarchy merged the same months from different years |
| 28 | The "Complaint Reviews by operator" 100% bar showed 100% for every operator | Added `complaint_theme` to the legend | A 100% stacked bar needs a breakdown field |
| 29 | Cards showed "12K" and 0.41 | Display units set to None; `% 1-2 Star` formatted as a percentage | Readable exact values |
