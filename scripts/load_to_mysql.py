"""Load cleaned TRAI and Play Store review datasets into MySQL."""
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
import config

def main():
    # Update with your local MySQL credentials if necessary (user:password@host/dbname)
    db_uri = "mysql+pymysql://root:root@localhost:3306/telecom_churn_db"
    engine = create_engine(db_uri)

    print("Connecting to MySQL and loading data...")

    # 1. Load TRAI Monthly Data
    trai_path = Path("data/clean/trai_mnp_monthly.csv") # or your processed trai output file path
    if trai_path.exists():
        df_trai = pd.read_csv(trai_path)
        df_trai.to_sql("trai_monthly_metrics", con=engine, if_exists="replace", index=False)
        print(f"Loaded {len(df_trai)} rows into 'trai_monthly_metrics'.")

    # 2. Load Cleaned Play Store Reviews
    reviews_path = Path(config.CLEAN_DIR) / "reviews_stage1.csv"
    if reviews_path.exists():
        df_reviews = pd.read_csv(reviews_path)
        # Rename columns to match MySQL snake_case table schema if needed
        df_reviews = df_reviews.rename(columns={
            "reviewId": "review_id",
            "thumbsUpCount": "thumbs_up_count",
            "reviewCreatedVersion": "review_created_version",
            "appVersion": "app_version",
            "at": "review_date",
            "replyContent": "reply_content",
            "repliedAt": "replied_at"
        })
        df_reviews.to_sql("play_store_reviews", con=engine, if_exists="append", index=False)
        print(f"Loaded {len(df_reviews)} rows into 'play_store_reviews'.")

    print("MySQL data loading complete!")

if __name__ == "__main__":
    main()