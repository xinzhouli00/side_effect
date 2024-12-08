import pandas as pd
from .side_effect import preprocess_text, get_comment_dict, pick_drug

def load_data(file_path):
    """
    Reads the CSV file containing drug review data.
    :param file_path: Path to the CSV file.
    :return: Pandas DataFrame of the data.
    """
    return pd.read_csv(file_path)

def prepare_comment_dict(data, comment_col_name='Review Text'):
    """
    Cleans and preprocesses comments, preparing a dictionary for further analysis.
    :param data: Pandas DataFrame containing review data.
    :param comment_col_name: The name of the column containing comments.
    :return: Comment dictionary ready for analysis.
    """
    return get_comment_dict(data, comment_col_name)

def filter_comments_by_drug(comment_dict, drug_name):
    """
    Filters comments for a specific drug name.
    :param comment_dict: List of dictionaries containing comments and metadata.
    :param drug_name: Name of the drug to filter.
    :return: Filtered comment dictionary and list of cleaned comments.
    """
    return pick_drug(comment_dict, drug_name)

def get_drugs(df):
    """
    Extracts unique drug names from a DataFrame.
    :param df: Pandas DataFrame containing a column 'Drug Name'.
    :return: List of unique drug names.
    """
    return df['Drug Name'].unique()