"""Classify customer review complaints into thematic categories using keyword rules."""
from pathlib import Path
import pandas as pd
import config

def classify_text(text):
    if not isinstance(text, str):
        return "Other / General"
    
    text_lower = text.lower()
    
    # Define keyword rules for complaint themes
    if any(keyword in text_lower for keyword in ["network", "speed", "internet", "signal", "coverage", "3g", "5g", "slow", "data"]):
        return "Network & Connectivity"
    elif any(keyword in text_lower for keyword in ["bill", "recharge", "plan", "money", "charged", "pack", "price", "cost", "validity"]):
        return "Billing & Pricing"
    elif any(keyword in text_lower for keyword in ["app", "bug", "crash", "update", "login", "otp", "error", "glitch"]):
        return "App Performance & Bugs"
    elif any(keyword in text_lower for keyword in ["customer care", "support", "call", "executive", "help", "service", "executive"]):
        return "Customer Support"
    else:
        return "General Feedback"

def main():
    cleaned_path = Path(config.CLEAN_DIR) / "reviews_stage1.csv"
    if not cleaned_path.exists():
        print(f"Error: {cleaned_path} not found. Run the scraper first.")
        return

    print("Loading reviews for NLP classification...")
    df = pd.read_csv(cleaned_path)

    # Apply classification
    df["complaint_theme"] = df["content"].apply(classify_text)

    # Output theme distribution summary
    print("\n--- Complaint Theme Breakdown ---")
    print(df["complaint_theme"].value_counts())

    # Save enriched dataset for Power BI
    output_path = Path(config.CLEAN_DIR) / "reviews_classified.csv"
    df.to_csv(output_path, index=False)
    print(f"\nEnriched reviews saved to {output_path}")

if __name__ == "__main__":
    main()