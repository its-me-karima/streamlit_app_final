import json
import pandas as pd

def json_to_csv(json_file, csv_file):
    # Read the JSON file
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Save as CSV
    df.to_csv(csv_file, index=False, encoding="utf-8")

    print(f"Converted {len(df)} records from {json_file} to {csv_file}")
    print("\nPreview:")
    print(df.to_string(index=False))

if __name__ == "__main__":
    json_to_csv("results.json", "results.csv")