import pytest
import pandas as pd
from src.side_effect.side_effect import (
    preprocess_text,
    get_drugs,
    get_comment_dict,
    remove_comment,
)
from src.side_effect.analysis import comment_side_effect
import string


def load_test_data():
    data = pd.read_csv("tests/data/test_data.csv")
    return data


def test_process_text():
    test_data = load_test_data()
    processed_text = [preprocess_text(text) for text in test_data["Review Text"]]
    check_punc = [
        any(char in string.punctuation for char in text) for text in processed_text
    ]
    assert not all(check_punc), "Cleaned text contains text with punctuation!"
    check_number = [
        any(char in string.digits for char in text) for text in processed_text
    ]
    assert not all(check_number), "Cleaned text contains text with number!"


def test_comment_length():
    test_data = load_test_data().to_dict(orient="records")
    lim = 30
    test_data = remove_comment(test_data, lim)
    check_len = [len(obj["cleaned_comments"]) > 30 for obj in test_data]
    assert all(check_len), f"All cleaned text should be longer than {lim} words!"


def test_get_drugs():
    drugs = [
        "adderall",
        "clonidine",
        "concerta",
        "dexedrine",
        "intuniv",
        "qelbree",
        "ritalin",
        "strattera",
        "vyvanse",
        "wellbutrin",
        "dexstrostat",
        "kapvay",
    ]
    test_data = load_test_data()
    extract_drug = get_drugs(test_data)
    check_drug = [drug in extract_drug for drug in drugs]
    assert all(check_drug), f"There are drugs missing!"
    check_drug = [drug in drugs for drug in extract_drug]
    assert all(check_drug), f"There are extra drugs show up!"


def test_get_commit_dict():
    test_data = load_test_data()
    comment_dict = get_comment_dict(test_data, "Review Text")
    check_dict = [len(item) == 4 for item in comment_dict]
    assert all(
        check_dict
    ), f"Something wrong with adding column or transforing dataframe to dictionary!"


def test_comment_side_effect():
    comment_similarity = {"nausea": [0.8, 0.9, 0.7]}
    expanded_keywords = {"nausea": [{"nausea": 1.0}]}
    drug_dict = [
        {"Drug Name": "DrugA", "Review Text": "Test comment 1", "side_effects": []},
        {"Drug Name": "DrugB", "Review Text": "Test comment 2", "side_effects": []},
        {"Drug Name": "DrugA", "Review Text": "Test comment 3", "side_effects": []},
    ]
    drug_dict, top_k_comments = comment_side_effect(
        comment_similarity, "nausea", expanded_keywords, drug_dict, top_k=2
    )
    assert len(top_k_comments) == 2
    assert "nausea" in drug_dict[0]["side_effects"]
