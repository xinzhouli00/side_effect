import pandas as pd
import os
import re
import numpy as np


class SideEffectProcessor:
    def __init__(self, input_dir, output_dir):
        """
        Initializes the processor with input and output directories.
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists

    @staticmethod
    def preprocess_text(text):
        """
        Cleans and preprocesses the given text by removing specific patterns,
        punctuation, digits, and converting to lowercase.
        """
        text = text.replace("-", " ")
        text = text.replace("_", " ")
        text = re.sub(r"[^\w\s]", "", text)  # Remove non-alphanumeric characters
        text = re.sub(r"\d+", "", text)  # Remove digits
        text = text.lower()  # Convert to lowercase
        return text.strip()

    @staticmethod
    def extract_drug_name(file_name):
        """
        Extracts the drug name from the file name by taking the last word
        before the file extension.
        """
        base_name = os.path.splitext(file_name)[0]
        drug_name = base_name.split("_")[-1]
        return drug_name

    def process_file(self, file_path):
        """
        Reads a CSV file, processes the data, and writes it to a new CSV file.
        """
        # Read the CSV file
        df = pd.read_csv(file_path)

        # Remove rows where Comment contains '[ Removed by Reddit ]' or '[deleted]'
        df = df[~df["Comment"].isin(["[ Removed by Reddit ]", "[deleted]", "[removed]"])]

        # Extract drug name from the file name
        drug_name = self.extract_drug_name(file_path)


        title_to_comment  = df['Post Title'].unique().tolist()
        comments = df["Comment"].unique().tolist()
        # print(len(df['Post Title']), len(df["Comment"]), len(comments), len(title_to_comment))
        title_to_comment.extend(comments)
        df = pd.DataFrame({'Review Text':title_to_comment})
        # print(df)

        # Clean the combined comments
        df["cleaned_comments"] = df["Review Text"].apply(self.preprocess_text)

        # Add the 'Drug Name' and 'side_effects' columns
        df["Drug Name"] = drug_name
        df["side_effects"] = [[]] * len(df)  # Initialize side_effects as empty lists

        # Select only required columns
        processed_df = df[
            ["Drug Name", "Review Text", "cleaned_comments", "side_effects"]
        ]

        # Save to a new CSV file in the output directory
        output_file = os.path.join(self.output_dir, os.path.basename(file_path))
        processed_df.to_csv(output_file, index=False)
        print(f"Processed data saved to: {output_file}")

    def process_directory(self):
        """
        Processes all CSV files in the input directory and saves the results
        to the output directory.
        """
        for file in os.listdir(self.input_dir):
            if file.endswith(".csv"):
                file_path = os.path.join(self.input_dir, file)
                self.process_file(file_path)
