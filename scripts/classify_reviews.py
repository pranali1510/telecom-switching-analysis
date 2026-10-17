"""Classify complaint reviews into themes (weighted keyword rules, version v2).

Rules
- A review is a COMPLAINT only if it is rated 1-3 stars and has at least 5 characters.
- Each theme has strong keywords (weight 2) and weak keywords (weight 1), matched as
  whole words. The theme with the highest total score wins.
- If themes tie, the one whose strong keyword appears EARLIEST in the review wins
  (the first problem a reviewer mentions is usually the main one).
- No match at all -> 'Other complaint'.
- A 1-3 star review under 5 characters is 'Too short to classify'; 4-5 stars is 'Not a complaint'.

Input : data/clean/reviews_stage1.csv      (UTF-8, written by scrape_play_reviews.py)
Output: data/clean/reviews_classified.csv  (UTF-8 with BOM, safe for Power BI)

Do NOT open the output in Excel and save it; that is what damaged the old file.
These keyword lists were improved after reading mistakes from a first labelled sample,
so measure them on a NEW blind sample (make_label_sample.py 2) before quoting accuracy.
"""
import re
from pathlib import Path

import pandas as pd

import config

RULES_VERSION = "v2"

# theme -> {weight: [regex fragments]}
THEMES = {
    "Network & Connectivity": {
        2: [r"network", r"signal", r"coverage", r"tower", r"call drops?", r"disconnect\w*",
            r"speed", r"slow", r"internet", r"[2345]g", r"wi-?fi", r"fib(?:er|re)",
            r"broadband", r"net", r"connection", r"connectivity", r"lag+y+|lagy|lag"],
        1: [r"data", r"sms", r"calls?", r"range"],
    },
    "Billing & Pricing": {
        2: [r"bills?", r"billing", r"refund\w*", r"charges?", r"charged", r"charging",
            r"deduct\w*", r"pric\w+", r"expensive", r"costly", r"validity", r"tariff",
            r"paisa", r"paise", r"rupee\w*", r"money", r"cashback", r"offers?"],
        1: [r"recharg\w*", r"plans?", r"packs?", r"payments?", r"balance", r"unlimited"],
    },
    "App Performance & Bugs": {
        2: [r"app", r"apps", r"appp", r"application", r"bugs?", r"crash\w*", r"log ?in",
            r"log ?out", r"sign ?in", r"otp", r"updates?", r"updated", r"error\w*",
            r"glitch\w*", r"hang\w*", r"loading", r"interface", r"user friendly",
            r"profile", r"not show\w*", r"not able to", r"unable to", r"features?",
            r"server"],
        1: [r"open", r"install\w*", r"not working", r"not work", r"doesn'?t work"],
    },
    "Customer Support": {
        2: [r"customer care", r"customer support", r"customer service", r"support",
            r"executive", r"agent", r"complain\w*", r"helpline", r"chat ?bot", r"bot",
            r"no response", r"not responding", r"resolv\w*", r"unresolved",
            r"call cent(?:er|re)", r"toll free", r"rude", r"tickets?", r"grievance",
            r"technician", r"engineer", r"raised", r"request", r"no one", r"help"],
        1: [r"services?", r"response", r"pathetic"],
    },
}
PATTERNS = {
    theme: {w: re.compile(r"\b(?:" + "|".join(words) + r")\b", re.IGNORECASE)
            for w, words in weights.items()}
    for theme, weights in THEMES.items()
}
MIN_LENGTH = 5
MAX_COMPLAINT_SCORE = 3


def classify_text(text: str) -> str:
    scores, first = {}, {}
    for theme, by_weight in PATTERNS.items():
        total, earliest = 0, 10**9
        for weight, pattern in by_weight.items():
            matches = list(pattern.finditer(text))
            total += weight * len(matches)
            if matches and weight == 2:
                earliest = min(earliest, matches[0].start())
        scores[theme], first[theme] = total, earliest
    best = max(scores.values())
    if best == 0:
        return "Other complaint"
    tied = [t for t, v in scores.items() if v == best]
    return min(tied, key=lambda t: first[t])


def main():
    src = Path(config.CLEAN_DIR) / "reviews_stage1.csv"
    if not src.exists():
        print(f"Error: {src} not found. Run scrape_play_reviews.py first.")
        return

    df = pd.read_csv(src, encoding="utf-8")
    text = df["content"].fillna("").astype(str).str.strip()
    df["review_length"] = text.str.len()
    df["sentiment"] = pd.cut(df["score"], bins=[0, 2, 3, 5], labels=["Negative", "Neutral", "Positive"])
    df["review_date"] = pd.to_datetime(df["at"], errors="coerce").dt.date

    too_short = df["review_length"] < MIN_LENGTH
    is_complaint = (df["score"] <= MAX_COMPLAINT_SCORE) & ~too_short
    df["is_complaint"] = is_complaint

    df["complaint_theme"] = "Not a complaint"
    df.loc[too_short & (df["score"] <= MAX_COMPLAINT_SCORE), "complaint_theme"] = "Too short to classify"
    df.loc[is_complaint, "complaint_theme"] = text[is_complaint].apply(classify_text)
    df["rules_version"] = RULES_VERSION

    print(f"Rules version: {RULES_VERSION}")
    print("--- Theme breakdown (all reviews) ---")
    print(df["complaint_theme"].value_counts())
    print("\n--- Theme breakdown (complaints only) ---")
    print(df.loc[is_complaint, "complaint_theme"].value_counts(normalize=True).round(3))

    out = Path(config.CLEAN_DIR) / "reviews_classified.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"\nSaved {len(df)} rows to {out}")


if __name__ == "__main__":
    main()
