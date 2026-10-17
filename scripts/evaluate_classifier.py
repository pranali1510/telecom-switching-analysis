r"""Measure how accurate the keyword classifier is, using your hand labels.

Usage
  python scripts\evaluate_classifier.py                         scores label_sample.csv
  python scripts\evaluate_classifier.py label_sample_round2.csv scores a later round

Predictions are re-read from the latest reviews_classified.csv, so after changing the
keyword rules you must re-run classify_reviews.py first. Each run is APPENDED to
docs/classifier_validation.md so every round stays on record.
"""
import math
import sys
from datetime import date
from pathlib import Path

import pandas as pd

import config

VALID = {
    "Network & Connectivity", "Billing & Pricing", "App Performance & Bugs",
    "Customer Support", "Other complaint",
}


def wilson(correct: int, n: int, z: float = 1.96):
    p = correct / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "label_sample.csv"
    df = pd.read_csv(Path(config.CLEAN_DIR) / name, encoding="utf-8-sig")
    current = pd.read_csv(Path(config.CLEAN_DIR) / "reviews_classified.csv", encoding="utf-8-sig")
    version = current["rules_version"].iloc[0] if "rules_version" in current.columns else "v1"
    df["predicted_theme"] = df["reviewId"].map(current.set_index("reviewId")["complaint_theme"])
    df["true_theme"] = df["true_theme"].fillna("").astype(str).str.strip()

    unlabelled = (df["true_theme"] == "").sum()
    bad = df[(df["true_theme"] != "") & ~df["true_theme"].isin(VALID)]
    if unlabelled or len(bad):
        print(f"Unlabelled rows: {unlabelled}. Rows with an invalid label: {len(bad)}.")
        if len(bad):
            print(bad["true_theme"].value_counts())
        print("Fix the true_theme column and run again.")
        return

    df["correct"] = df["true_theme"] == df["predicted_theme"]
    n, hits = len(df), int(df["correct"].sum())
    low, high = wilson(hits, n)
    lines = [
        f"## {name} (rules {version}, scored {date.today().isoformat()})",
        "",
        f"Sample: {n} complaint reviews, random, labelled blind (predictions hidden).",
        f"Overall accuracy: {hits / n:.1%} (95% interval {low:.0%} to {high:.0%})",
        "Note: a score on a sample that was used to tune the rules is optimistic; only a fresh blind sample is a fair test.",
        "",
        "| Theme | Labelled count | Precision | Recall |",
        "|---|---|---|---|",
    ]
    for theme in sorted(VALID):
        predicted = df["predicted_theme"] == theme
        actual = df["true_theme"] == theme
        both = int((predicted & actual).sum())
        precision = both / predicted.sum() if predicted.sum() else float("nan")
        recall = both / actual.sum() if actual.sum() else float("nan")
        lines.append(f"| {theme} | {int(actual.sum())} | {precision:.0%} | {recall:.0%} |")
    report = "\n".join(lines)
    print(report)

    out = Path("docs") / "classifier_validation.md"
    out.parent.mkdir(exist_ok=True)
    header = "# Classifier validation\n\n" if not out.exists() else ""
    with out.open("a", encoding="utf-8") as f:
        f.write(header + report + "\n\n")
    print(f"\nAppended to {out}")
    print("\nMost common mistakes (true -> predicted):")
    print(df[~df["correct"]].groupby(["true_theme", "predicted_theme"]).size()
          .sort_values(ascending=False).head(8))


if __name__ == "__main__":
    main()
