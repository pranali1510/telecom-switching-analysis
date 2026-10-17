"""Load the classified reviews and the TRAI series into MySQL.

Credentials come from environment variables (never put a password in this file):
  PowerShell:  $env:MYSQL_USER="root"; $env:MYSQL_PASSWORD="your-password"
Optional: MYSQL_HOST (default localhost), MYSQL_PORT (3306), MYSQL_DB (telecom_churn_db)
The database must already exist. Tables are dropped and rebuilt on each run, with
primary keys, so re-running never creates duplicates.
"""
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

import config

REVIEWS_DDL = """
CREATE TABLE play_store_reviews (
    review_id VARCHAR(64) NOT NULL,
    operator VARCHAR(20),
    score TINYINT,
    thumbs_up_count INT,
    review_created_version VARCHAR(40),
    app_version VARCHAR(40),
    review_datetime DATETIME,
    reply_content TEXT,
    replied_at DATETIME,
    content TEXT,
    review_length INT,
    sentiment VARCHAR(10),
    is_complaint BOOLEAN,
    complaint_theme VARCHAR(40),
    PRIMARY KEY (review_id)
) CHARACTER SET utf8mb4
"""

TRAI_DDL = """
CREATE TABLE trai_monthly_metrics (
    month_period CHAR(7) NOT NULL,
    month_date DATE,
    mnp_requests_million DECIMAL(6,2),
    status VARCHAR(20),
    source_url VARCHAR(400),
    PRIMARY KEY (month_period)
) CHARACTER SET utf8mb4
"""


def get_engine():
    password = os.environ.get("MYSQL_PASSWORD")
    if not password:
        raise SystemExit('Set the password first: $env:MYSQL_PASSWORD="your-password"')
    url = URL.create(
        "mysql+pymysql",
        username=os.environ.get("MYSQL_USER", "root"),
        password=password,
        host=os.environ.get("MYSQL_HOST", "localhost"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        database=os.environ.get("MYSQL_DB", "telecom_churn_db"),
        query={"charset": "utf8mb4"},
    )
    return create_engine(url)


def main():
    clean = Path(config.CLEAN_DIR)
    engine = get_engine()

    r = pd.read_csv(clean / "reviews_classified.csv", encoding="utf-8-sig")
    r = r.rename(columns={
        "reviewId": "review_id", "thumbsUpCount": "thumbs_up_count",
        "reviewCreatedVersion": "review_created_version", "appVersion": "app_version",
        "at": "review_datetime", "replyContent": "reply_content", "repliedAt": "replied_at",
    })
    r["review_datetime"] = pd.to_datetime(r["review_datetime"], errors="coerce")
    r["replied_at"] = pd.to_datetime(r["replied_at"], errors="coerce")
    r = r[[
        "review_id", "operator", "score", "thumbs_up_count", "review_created_version",
        "app_version", "review_datetime", "reply_content", "replied_at", "content",
        "review_length", "sentiment", "is_complaint", "complaint_theme",
    ]]

    t = pd.read_csv(clean / "trai_monthly_for_bi.csv", encoding="utf-8-sig")
    t = t.rename(columns={"month": "month_period"})
    t["month_date"] = pd.to_datetime(t["month_date"]).dt.date

    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS play_store_reviews"))
        conn.execute(text(REVIEWS_DDL))
        conn.execute(text("DROP TABLE IF EXISTS trai_monthly_metrics"))
        conn.execute(text(TRAI_DDL))
        r.to_sql("play_store_reviews", conn, if_exists="append", index=False, chunksize=500)
        t.to_sql("trai_monthly_metrics", conn, if_exists="append", index=False)
    print(f"Loaded {len(r)} reviews and {len(t)} TRAI months.")


if __name__ == "__main__":
    main()
