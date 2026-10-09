"""Collect public Play Store reviews per operator app.

Raw output keeps everything the library returns (JSON lines).
Cleaned output drops reviewer names (personal data) and exact duplicates.
"""
import json
import time
from pathlib import Path

import pandas as pd
from google_play_scraper import Sort, reviews

import config


def fetch_app_reviews(app_id: str, target: int):
    collected, token = [], None
    while len(collected) < target:
        batch, token = reviews(
            app_id,
            lang="en",
            country="in",
            sort=Sort.NEWEST,
            count=min(200, target - len(collected)),
            continuation_token=token,
        )
        if not batch:
            break
        collected.extend(batch)
        if token is None:
            break
        time.sleep(config.SLEEP_SECONDS)
    return collected


def main():
    Path(config.RAW_REVIEWS_DIR).mkdir(parents=True, exist_ok=True)
    Path(config.CLEAN_DIR).mkdir(parents=True, exist_ok=True)
    frames = []
    for operator, app_id in config.APPS.items():
        if app_id.startswith("TODO"):
            print(f"Skipping {operator}: set its app ID in config.py")
            continue
        rows = fetch_app_reviews(app_id, config.REVIEWS_PER_APP)
        raw_path = Path(config.RAW_REVIEWS_DIR) / f"{operator}.jsonl"
        with raw_path.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, default=str, ensure_ascii=False) + "\n")
        df = pd.DataFrame(rows)
        df["operator"] = operator
        frames.append(df)
        print(f"{operator}: {len(df)} reviews saved to {raw_path}")

    if not frames:
        return
    all_df = pd.concat(frames, ignore_index=True)
    all_df = all_df.drop(columns=["userName", "userImage"], errors="ignore")  # personal data
    before = len(all_df)
    all_df = all_df.drop_duplicates(subset=["operator", "content", "at"])
    print(f"Dropped {before - len(all_df)} exact duplicates")
    all_df.to_csv(Path(config.CLEAN_DIR) / "reviews_stage1.csv", index=False)


if __name__ == "__main__":
    main()
