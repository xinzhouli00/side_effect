import pandas as pd
from .side_effect import (
    get_comment_dict,
    pick_drug,
    merge_data,
    remove_comment,
    remove_positive_comments,
)


def load_data(file_path):
    """
    Reads the CSV file containing drug review data.
    :param file_path: Path to the CSV file.
    :return: Pandas DataFrame of the data.
    """
    return pd.read_csv(file_path)


def prepare_comment_dict(
    data, comment_col_name="Review Text", cleaned_data=False, lim=30
):
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
    return df["Drug Name"].unique()


def get_merged_data(path):
    """
    Retrieve merged data from a specified folder path.

    Parameters:
    path (str): Path to the folder containing CSV files.

    Returns:
    pd.DataFrame: A DataFrame containing all merged data from the folder.
    """
    return merge_data(path)


def get_long_comment(dict, lim):
    """
    Filter comments with word counts exceeding a specified limit.

    Parameters:
    dict (list of dict): A list of dictionaries where each dictionary contains a 'cleaned_comments' key.
    lim (int): The word count limit for filtering comments.

    Returns:
    list: A list of dictionaries with comments that have a word count above the limit.
    """
    return remove_comment(dict, lim)


def get_negative_comment(df):
    """
    Filter out rows with positive sentiment scores in the 'Review Text' column.

    Parameters:
    df (pd.DataFrame): A DataFrame containing a 'Review Text' column.

    Returns:
    pd.DataFrame: A DataFrame containing rows with negative sentiment scores.
    """
    return remove_positive_comments(df)
