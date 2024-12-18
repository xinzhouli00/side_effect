import re
import ssl
import pandas as pd
from nltk.corpus import wordnet
import nltk
import os
from nltk.sentiment import SentimentIntensityAnalyzer

ssl._create_default_https_context = ssl._create_unverified_context

nltk.download("wordnet")


def preprocess_text(text):
    """
    Preprocesses a given text by removing unwanted characters and formatting.
    - Removes punctuation, numbers, and converts text to lowercase.
    """
    text = text.replace("-", " ")
    text = text.replace("_", " ")
    text = re.sub(r"[^\w\s]", "", text)  # Remove special characters
    text = re.sub(r"\d+", "", text)  # Remove numbers
    text = text.lower()  # Convert to lowercase
    text = re.sub(r"\s+", " ", text).strip()  # Remove extra spaces
    return text


def get_drugs(df):
    """
    Extracts unique drug names from a DataFrame.
    :param df: Pandas DataFrame containing a column 'Drug Name'.
    :return: List of unique drug names.
    """
    return df["Drug Name"].unique()


def get_comment_dict(df, comment_col_name=None, cleaned_data=False):
    """
    Cleans comments and prepares a dictionary of all comments and their metadata.
    :param df: Pandas DataFrame containing comments.
    :param comment_col_name: Column name for the comments.
    :return: List of dictionaries with processed comments and additional fields.
    """
    if not cleaned_data:
        comments = df[comment_col_name]
        cleaned_comments = [preprocess_text(comment) for comment in comments]
        df["cleaned_comments"] = cleaned_comments
    df["side_effects"] = [[] for _ in range(len(cleaned_comments))]
    dict = df.to_dict(orient="records")
    return dict


def pick_drug(comment_dict, drug_name):
    """
    Filters comments and metadata for a specific drug.
    :param comment_dict: List of comment dictionaries.
    :param drug_name: Name of the drug to filter comments for.
    :return: List of comments and cleaned comment texts for the specified drug.
    """
    drug_dict = [item for item in comment_dict if item["Drug Name"] == drug_name]
    drug_comment = [item["cleaned_comments"] for item in drug_dict]
    return drug_dict, drug_comment


def merge_data(folder_path):
    """
    Merge all CSV files in a specified folder into a single DataFrame.

    Parameters:
    folder_path (str): Path to the folder containing the CSV files.

    Returns:
    pd.DataFrame: A DataFrame that combines all CSV files in the folder.
    """
    merged_files = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".csv"):
            file_path = os.path.join(folder_path, file_name)
            df = pd.read_csv(file_path)
            merged_files.append(df)
    merged_df = pd.concat(merged_files, ignore_index=True)
    return merged_df


def remove_comment(dict, lim):
    """
    Remove comments with word counts exceeding a specified limit.

    Parameters:
    dict (list of dict): A list of dictionaries where each dictionary contains a 'cleaned_comments' key.
    lim (int): The word count limit for comments to be removed.

    Returns:
    list: A list of dictionaries with comments that have a word count above the limit.
    """
    rm_sc = [obj for obj in dict if len(obj["cleaned_comments"].split()) > lim]
    print(len(rm_sc))
    return rm_sc


def remove_positive_comments(df):
    """
    Remove rows from a DataFrame where the sentiment score of the 'Review Text' column is positive.

    Parameters:
    df (pd.DataFrame): A DataFrame containing a 'Review Text' column.

    Returns:
    pd.DataFrame: A DataFrame with only rows having negative sentiment scores in the 'Review Text' column.
    """
    sentiment_scores = []
    sia = SentimentIntensityAnalyzer()

    for text in df["Review Text"]:
        score = sia.polarity_scores(text)
        sentiment_scores.append(score["compound"])

    df["sentiment_score"] = sentiment_scores
    df = df[df["sentiment_score"] < 0].reset_index()

    df.drop(columns=["sentiment_score"], inplace=True)
    return df
