r"""Pull a BLIND random sample of complaint reviews to label by hand.

Usage
  python scripts\make_label_sample.py            round 1: 150 reviews -> label_sample.csv
  python scripts\make_label_sample.py 2          round 2: 100 NEW reviews -> label_sample_round2.csv
  python scripts\make_label_sample.py 2 80       round 2 with 80 reviews

Later rounds never include a review you already labelled. No predictions are shown,
on purpose: if you can see the classifier's guess you will tend to agree with it.

Fill the empty 'true_theme' column using exactly one of:
  Network & Connectivity | Billing & Pricing | App Performance & Bugs |
  Customer Support | Other complaint
Save as 'CSV UTF-8 (Comma delimited)', then run:
  python scripts\evaluate_classifier.py label_sample_round2.csv
"""
import sys
from pathlib import Path

import pandas as pd

import config

CLEAN = Path(config.CLEAN_DIR)


def label_path(round_no: int) -> Path:
    return CLEAN / ("label_sample.csv" if round_no == 1 else f"label_sample_round{round_no}.csv")


def main():
    round_no = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    size = int(sys.argv[2]) if len(sys.argv) > 2 else (150 if round_no == 1 else 100)
    path = label_path(round_no)
    if path.exists():
        old = pd.read_csv(path, encoding="utf-8-sig")
        if old["true_theme"].fillna("").astype(str).str.strip().ne("").any():
            print(f"{path.name} already contains labels. Not overwriting it.")
            return

    df = pd.read_csv(CLEAN / "reviews_classified.csv", encoding="utf-8-sig")
    complaints = df[df["is_complaint"]]

    used = set()
    for earlier in range(1, round_no):
        p = label_path(earlier)
        if p.exists():
            used |= set(pd.read_csv(p, encoding="utf-8-sig")["reviewId"])
    complaints = complaints[~complaints["reviewId"].isin(used)]

    seed = 2026 if round_no == 1 else 2026 + round_no
    sample = complaints.sample(n=min(size, len(complaints)), random_state=seed)
    out = sample[["reviewId", "operator", "score", "content"]].copy()
    out["true_theme"] = ""
    out.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"Wrote {len(out)} reviews to {path} ({len(used)} earlier-labelled reviews excluded).")
    print("Fill in the true_theme column (no predictions shown).")


if __name__ == "__main__":
    main()
