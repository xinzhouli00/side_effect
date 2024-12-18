# --------------------------side_effect_scores-----------------------------

import csv
import json
from collections import defaultdict

def csv_to_json_grouped(csv_file, json_file):
    """
    Convert a CSV file to a JSON file grouped by drug, with side effects as a dictionary.
    Capitalize the first letter of each side effect.
    :param csv_file: Path to the input CSV file
    :param json_file: Path to the output JSON file
    """
    grouped_data = defaultdict(lambda: {"drugName": "", "sideEffects": {}})

    # Open and read the CSV file
    with open(csv_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)  # Use DictReader to process each row as a dictionary

        # Process each row in the CSV file
        for row in csv_reader:
            drug = row.get("drug")  # Get the 'drug' value
            side_effect = row.get("side_effect")  # Get the 'side_effect' value
            score = row.get("score")  # Get the 'score' value

            if not drug or not side_effect or not score:
                raise ValueError("Missing required fields ('drug', 'side_effect', 'score') in CSV file.")

            # Capitalize the first letter of the side effect and drug
            drug = drug.title()
            side_effect = side_effect.title()

            # Ensure score is converted to a string (retain precision as in your example)
            score = str(float(score))  # Convert to float first to ensure it's valid

            # Add data to the grouped structure
            if not grouped_data[drug]["drugName"]:
                grouped_data[drug]["drugName"] = drug
            grouped_data[drug]["sideEffects"][side_effect] = score

    # Convert the grouped data to a list of dictionaries
    result = list(grouped_data.values())

    # Write the grouped data to a JSON file
    with open(json_file, mode='w', encoding='utf-8') as file:
        json.dump(result, file, indent=4, ensure_ascii=False)  # ensure_ascii=False ensures proper display of non-ASCII characters
    print(f"Successfully converted {csv_file} to {json_file}.")

# Example call
if __name__ == "__main__":
    # Path to the input CSV file
    input_csv = "output/side_effect_scores.csv"  
    # Path to the output JSON file
    output_json = "website/public/data/drugSideEffectsData.json"  

    # Call the conversion function
    csv_to_json_grouped(input_csv, output_json)

# --------------------------side_effect_fda-----------------------------

def csv_to_json_grouped(csv_file, json_file):
    """
    Convert a CSV file to a JSON file grouped by drug, with side effects as a dictionary.
    Capitalize the first letter of each side effect.
    :param csv_file: Path to the input CSV file
    :param json_file: Path to the output JSON file
    """
    grouped_data = defaultdict(lambda: {"drugName": "", "sideEffects": {}})

    # Open and read the CSV file
    with open(csv_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)  # Use DictReader to process each row as a dictionary

        # Process each row in the CSV file
        for row in csv_reader:
            drug = row.get("Drug")  # Get the 'drug' value
            side_effect = row.get("Reaction")  # Get the 'side_effect' value
            score = row.get("Count")  # Get the 'score' value

            if not drug or not side_effect or not score:
                raise ValueError("Missing required fields ('Drug', 'Reaction', 'Count') in CSV file.")

            # Capitalize the first letter of the side effect and drug
            drug = drug.title()
            side_effect = side_effect.title()

            # Ensure score is converted to a string (retain precision as in your example)
            score = str(float(score))  # Convert to float first to ensure it's valid

            # Add data to the grouped structure
            if not grouped_data[drug]["drugName"]:
                grouped_data[drug]["drugName"] = drug
            grouped_data[drug]["sideEffects"][side_effect] = score

    # Convert the grouped data to a list of dictionaries
    result = list(grouped_data.values())

    # Write the grouped data to a JSON file
    with open(json_file, mode='w', encoding='utf-8') as file:
        json.dump(result, file, indent=4, ensure_ascii=False)  # ensure_ascii=False ensures proper display of non-ASCII characters
    print(f"Successfully converted {csv_file} to {json_file}.")

# Example call
if __name__ == "__main__":
    # Path to the input CSV file
    input_csv = "data/drug_reactions.csv"  
    # Path to the output JSON file
    output_json = "website/public/data/formatted_drug_reactions.json"  

    # Call the conversion function
    csv_to_json_grouped(input_csv, output_json)

# --------------------------Process Drug Reviews-----------------------------
import os
import pandas as pd

# Define folder path
folder_path = "output"
output_file = "output/merged_drug_data.csv"  

# Initialize empty DataFrame for merging
merged_data = pd.DataFrame()

# Iterate through all CSV files in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith("_rank.csv"):  # Process only relevant files
        # Extract drug name from filename (e.g., 'adderall' from 'adderall_rank.csv')
        drug_name = file_name.replace("_rank.csv", "")

        # Read CSV file
        file_path = os.path.join(folder_path, file_name)
        df = pd.read_csv(file_path)

        # Add drug name column
        df["drug"] = drug_name

        # Remove rows where 'rank' contains "tail"
        df = df[~df["rank"].str.contains("tail", na=False)]

        # Drop 'rank' column
        df = df.drop(columns=["rank"])

        # Merge into main DataFrame
        merged_data = pd.concat([merged_data, df], ignore_index=True)

# Export merged results to CSV file
merged_data.to_csv(output_file, index=False, encoding="utf-8")
print(f"Completed merging! Results stored in {output_file}")

# Process and Convert to JSON
import json

# Read CSV file
file_path = "output/merged_drug_data.csv"
df = pd.read_csv(file_path)

# Convert "drug" and "side_effect" columns to title case
df["drug"] = df["drug"].str.title()
df["side_effect"] = df["side_effect"].str.title()

# Transform data into required JSON structure
result = []

# Group by drug name
for drug, group in df.groupby("drug"):
    drug_data = {
        "drugName": drug,
        "sideEffects": {}
    }

    # Group by side effects and collect unique comments
    for side_effect, comments in group.groupby("side_effect"):
        drug_data["sideEffects"][side_effect] = list(comments["comment"].unique())

    result.append(drug_data)

# Convert to JSON format
output_json = json.dumps(result, indent=4, ensure_ascii=False)

# Write JSON to file
output_file = "website/public/data/reviews.json"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(output_json)

print(f"JSON generated and saved to {output_file}")