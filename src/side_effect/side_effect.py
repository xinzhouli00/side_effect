import re
import ssl
import pandas as pd
from nltk.corpus import wordnet
import nltk
import os

# 忽略 SSL 问题
ssl._create_default_https_context = ssl._create_unverified_context


# 下载 NLTK 数据
nltk.download('wordnet')

def preprocess_text(text):
    """
    Preprocesses a given text by removing unwanted characters and formatting.
    - Removes punctuation, numbers, and converts text to lowercase.
    """
    text = text.replace('-', ' ')
    text = text.replace('_', ' ')
    text = re.sub(r'[^\w\s]', '', text)  # Remove special characters
    text = re.sub(r'\d+', '', text)      # Remove numbers
    text = text.lower()                  # Convert to lowercase
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    return text

def get_drugs(df):
    """
    Extracts unique drug names from a DataFrame.
    :param df: Pandas DataFrame containing a column 'Drug Name'.
    :return: List of unique drug names.
    """
    return df['Drug Name'].unique()

def get_comment_dict(df, comment_col_name = None, cleaned_data = False):
    """
    Cleans comments and prepares a dictionary of all comments and their metadata.
    :param df: Pandas DataFrame containing comments.
    :param comment_col_name: Column name for the comments.
    :return: List of dictionaries with processed comments and additional fields.
    """
    if not cleaned_data:
        comments = df[comment_col_name]
        cleaned_comments = [preprocess_text(comment) for comment in comments]
        df['cleaned_comments'] = cleaned_comments
    df['side_effects'] = [[] for _ in range(len(cleaned_comments))]
    return df.to_dict(orient='records')

def pick_drug(comment_dict, drug_name):
    """
    Filters comments and metadata for a specific drug.
    :param comment_dict: List of comment dictionaries.
    :param drug_name: Name of the drug to filter comments for.
    :return: List of comments and cleaned comment texts for the specified drug.
    """
    drug_dict = [item for item in comment_dict if item['Drug Name'] == drug_name]
    drug_comment = [item['cleaned_comments'] for item in drug_dict]
    return drug_dict, drug_comment

def merge_data(folder_path):
    merged_files = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder_path, file_name)
            df = pd.read_csv(file_path)
            merged_files.append(df)
    merged_df = pd.concat(merged_files, ignore_index=True)
    return merged_df