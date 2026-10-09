# Cleaning log

Data Cleaning & Quality Log: Telecom Switching & Churn Analysis
1. TRAI MNP Extraction & PDF Parsing Anomalies
Date: October 2026

Component: TRAI MNP Extraction Script (scripts/extract_trai_mnp.py) & PDF Lists (data/raw/trai_pdf_list.csv)

Issues & Decisions:

Incorrect Month Mapping (2026-02): The initial script linked February 2026 to the incorrect (March) press release PDF. This was caught during automated validation by comparing the extracted PDF heading month text against the target row, and subsequently corrected.

Unsearchable PDF (2025-12): The PDF for December 2025 contained no searchable/rasterized text layer (0/0 search match). The correct value (16.12 million) was manually cross-referenced from the official publication and hardcoded, with the row explicitly flagged as manual_entry.

Regex Fallback for White Space (2026-02): Standard extraction patterns failed to read the figures for February 2026 due to layout variations. A whitespace-insensitive fallback script was implemented, successfully retrieving 14.47 million, which matched independent manual verification.

Duplicate Metric Validation (2025-10 & 2025-08): Both months coincidentally registered identical MNP volume values (15.05 million). Verification confirmed these figures were authentic raw data points from their respective press releases rather than an ingestion error.

Series Breaks (External Note): Noted that the Tata Teleservices wireline counting change (June 2025) and Bharti Airtel M2M counting adjustments (up to November 2025) represent historical series breaks that affect long-term subscriber-base tracking, though they leave MNP request counts unaffected.

2. Play Store Review Scraper Configuration & Package IDs
Date: October 2026

Component: Play Store Scraper Script (scripts/config.py)

Issues & Decisions:

BSNL Package ID Correction: Initial trial guesses (com.bsnl.selfcare and legacy variants) returned 0 records because BSNL’s active self-care utility application uses a completely different developer package identifier. Investigated the direct Google Play Store web listing URL structure to verify the correct identifier (com.rma.bsnl), successfully restoring full ingestion of over 2,900 reviews.

3. Pipeline Execution Environment & File Locks
Date: October 2026

Component: Python Local Processing Environment (data/clean/)

Issues & Decisions:

File Access Permission Lock: Encountered a PermissionError: [Errno 13] Access Denied when pandas attempted to overwrite reviews_stage1.csv. Root cause traced to an active preview window/external program locking the CSV file. Resolved by closing the conflicting process instance to allow clean automated overwrites.

Missing Dependency Specification: Discovered that pypdf was omitted from requirements.txt during initial environment setup, which would block reproduction on clone environments. Resolved by explicitly appending pypdf to the requirements manifest and pushing the updated configuration to GitHub.



4. Database Schema & MySQL Loading Ingestion
Component: MySQL Database Integration (scripts/load_to_mysql.py)

Issues & Resolutions:

Column Name Harmonization: Mapped camelCase headers from the Play Store scraper output (reviewId, thumbsUpCount, reviewCreatedVersion) to standard snake_case database columns (review_id, thumbs_up_count, review_created_version) to maintain clean SQL convention standards.

Primary Key Constraints & Appends: Designated review_id as the primary key for play_store_reviews (loading 11,961 clean rows) and month_period for trai_monthly_metrics (loading 14 complete historical rows) to ensure idempotency and prevent duplicate inserts on script re-runs.

| # | Dataset | Issue found | Rows affected | Decision | Reason |
|---|---------|-------------|---------------|----------|--------|
| 1 |         |             |               |          |        |
