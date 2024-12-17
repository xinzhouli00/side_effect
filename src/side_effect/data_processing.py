import pandas as pd
from .side_effect import get_comment_dict, pick_drug, merge_data, remove_comment, remove_positive_comments

def load_data(file_path):
    """
    Reads the CSV file containing drug review data.
    :param file_path: Path to the CSV file.
    :return: Pandas DataFrame of the data.
    """
    return pd.read_csv(file_path)

def prepare_comment_dict(data, comment_col_name='Review Text', cleaned_data = False, lim = 30):
    """
    Cleans and preprocesses comments, preparing a dictionary for further analysis.
    :param data: Pandas DataFrame containing review data.
    :param comment_col_name: The name of the column containing comments.
    :return: Comment dictionary ready for analysis.
    """
    dict = get_comment_dict(data, comment_col_name)
    return get_long_comment(dict, lim)

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

def get_merged_data(path):
    return merge_data(path)

def get_long_comment(dict, lim):
    return remove_comment(dict, lim)

def get_negative_comment(df):
    return remove_positive_comments(df)