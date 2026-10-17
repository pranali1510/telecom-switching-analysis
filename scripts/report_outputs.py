"""Build the summary tables used by the dashboard.

Input : data/clean/reviews_classified.csv, data/clean/trai_mnp_monthly.csv
Output (all UTF-8 with BOM, in data/clean/):
  operator_summary.csv      reviews, average rating, % 1-2 star, date window per operator
  operator_theme_share.csv  share of each operator's complaints by theme
  top_complaints.csv        most-liked 1-2 star complaints per operator
  trai_monthly_for_bi.csv   TRAI MNP series with a real date column
"""
from pathlib import Path

import pandas as pd

import config

CLEAN = Path(config.CLEAN_DIR)


def write(df, name):
    df.to_csv(CLEAN / name, index=False, encoding="utf-8-sig")
    print(f"Wrote {name} ({len(df)} rows)")


def main():
    r = pd.read_csv(CLEAN / "reviews_classified.csv", encoding="utf-8-sig")
    r["at"] = pd.to_datetime(r["at"], errors="coerce")

    summary = r.groupby("operator").agg(
        reviews=("reviewId", "count"),
        avg_rating=("score", "mean"),
        first_review=("at", "min"),
        last_review=("at", "max"),
    )
    summary["pct_1_2_star"] = r[r["score"] <= 2].groupby("operator").size() / summary["reviews"]
    summary["complaint_reviews"] = r[r["is_complaint"]].groupby("operator").size()
    summary["days_covered"] = (summary["last_review"] - summary["first_review"]).dt.days + 1
    summary["avg_rating"] = summary["avg_rating"].round(2)
    summary["pct_1_2_star"] = summary["pct_1_2_star"].round(3)
    summary = summary.reset_index()
    write(summary, "operator_summary.csv")

    c = r[r["is_complaint"]]
    share = c.groupby(["operator", "complaint_theme"]).size().rename("complaints").reset_index()
    share["share_of_operator_complaints"] = (
        share["complaints"] / share.groupby("operator")["complaints"].transform("sum")
    ).round(3)
    write(share, "operator_theme_share.csv")

    top = (
        c[c["score"] <= 2]
        .sort_values(["operator", "thumbsUpCount"], ascending=[True, False])
        .groupby("operator")
        .head(5)[["operator", "complaint_theme", "score", "thumbsUpCount", "content"]]
        .copy()
    )
    top["content"] = top["content"].astype(str).str.slice(0, 400)
    write(top, "top_complaints.csv")

    t = pd.read_csv(CLEAN / "trai_mnp_monthly.csv", dtype={"month": str})
    t["month_date"] = pd.to_datetime(t["month"] + "-01")
    t = t.sort_values("month_date")[["month", "month_date", "mnp_requests_million", "status", "source_url"]]
    write(t, "trai_monthly_for_bi.csv")


if __name__ == "__main__":
    main()
