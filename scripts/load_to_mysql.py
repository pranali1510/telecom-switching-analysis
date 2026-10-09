"""Load classified Play Store review datasets into MySQL."""
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
import config

def main():
    db_uri = "mysql+pymysql://root:root@localhost:3306/telecom_churn_db"
    engine = create_engine(db_uri)

    print("Connecting to MySQL and loading classified reviews...")

    # Load Classified Play Store Reviews with utf-8-sig encoding to handle special characters
    classified_path = Path(config.CLEAN_DIR) / "reviews_classified.csv"
    if classified_path.exists():
        df_reviews = pd.read_csv(classified_path, encoding="latin-1")
        
        column_mapping = {
            "reviewId": "review_id",
            "thumbsUpCount": "thumbs_up_count",
            "reviewCreatedVersion": "review_created_version",
            "appVersion": "app_version",
            "at": "review_date",
            "replyContent": "reply_content",
            "repliedAt": "replied_at"
        }
        df_reviews = df_reviews.rename(columns={k: v for k, v in column_mapping.items() if k in df_reviews.columns})
        
        df_reviews.to_sql("play_store_reviews", con=engine, if_exists="replace", index=False)
        print(f"Loaded {len(df_reviews)} enriched rows (with complaint themes) into 'play_store_reviews'.")

    print("MySQL classified reviews loading complete!")

if __name__ == "__main__":
    main()