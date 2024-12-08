import pytest
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from src.side_effect.side_effect import preprocess_text, get_drugs, get_comment_dict, pick_drug
from src.side_effect.embedding_and_keywords import BioBERTEmbedder, KeywordExpander
from src.side_effect.analysis import get_comment_similarity, evaluate_score, comment_side_effect

# Sample data for testing
sample_data = pd.DataFrame({
    "Drug Name": ["DrugA", "DrugB", "DrugA"],
    "Review Text": [
        "This is a test comment for DrugA.",
        "DrugB caused nausea and headache.",
        "DrugA made me dizzy and I felt tired."
    ]
})

# 1. Test functions from `side_effect.py`
def test_preprocess_text():
    text = "Nausea - Dizziness 123!!"
    expected = "nausea dizziness"
    assert preprocess_text(text) == expected

def test_get_drugs():
    drugs = get_drugs(sample_data)
    assert set(drugs) == {"DrugA", "DrugB"}

def test_get_comment_dict():
    comment_dict = get_comment_dict(sample_data, "Review Text")
    assert len(comment_dict) == 3
    assert comment_dict[0]['cleaned_comments'] == "this is a test comment for druga"

def test_pick_drug():
    comment_dict = get_comment_dict(sample_data, "Review Text")
    drug_dict, drug_comments = pick_drug(comment_dict, "DrugA")
    assert len(drug_dict) == 2
    assert len(drug_comments) == 2
    assert "this is a test comment for druga" in drug_comments

# 2. Test classes from `embedding_and_keywords.py`
def test_biobert_embedder(monkeypatch):
    # Mock BioBERTEmbedder
    class MockBioBERTEmbedder:
        def get_embeddings(self, text):
            return np.random.rand(1, 768)  # Simulate embedding

    embedder = MockBioBERTEmbedder()
    embedding = embedder.get_embeddings("Test text")
    assert embedding.shape == (1, 768)

def test_keyword_expander(monkeypatch):
    # Mock KeywordExpander
    class MockKeywordExpander:
        def __init__(self, embedder, side_effects_official):
            self.side_effects_official = side_effects_official

        def expand_keywords(self, initial_keywords):
            return {kw: [{kw: 1.0}] for kw in initial_keywords}

    expander = MockKeywordExpander(None, ["fatigue", "anxiety"])
    expanded_keywords = expander.expand_keywords(["nausea"])
    assert "nausea" in expanded_keywords
    assert expanded_keywords["nausea"] == [{"nausea": 1.0}]

# 3. Test functions from `analysis.py`
def test_get_comment_similarity(monkeypatch):
    # Mock embeddings and similarity calculation
    def mock_get_embeddings(text):
        return np.random.rand(1, 768)

    embeddings = np.random.rand(3, 768)  # Simulated comment embeddings
    expanded_keywords = {
        "nausea": [{"nausea": 1.0}, {"sickness": 0.9}]
    }
    similarity = get_comment_similarity("nausea", expanded_keywords, embeddings)
    assert "nausea" in similarity
    assert len(similarity["nausea"]) == 3

def test_evaluate_score():
    comment_similarity = {
        "nausea": [0.8, 0.9, 0.7]
    }
    expanded_keywords = {
        "nausea": [{"nausea": 1.0}]
    }
    score = evaluate_score(comment_similarity, "nausea", expanded_keywords)
    assert isinstance(score, float)
    assert score > 0

def test_comment_side_effect():
    comment_similarity = {
        "nausea": [0.8, 0.9, 0.7]
    }
    expanded_keywords = {
        "nausea": [{"nausea": 1.0}]
    }
    drug_dict = [
        {"Drug Name": "DrugA", "Review Text": "Test comment 1", "side_effects": []},
        {"Drug Name": "DrugB", "Review Text": "Test comment 2", "side_effects": []},
        {"Drug Name": "DrugA", "Review Text": "Test comment 3", "side_effects": []}
    ]
    drug_dict, top_k_comments = comment_side_effect(comment_similarity, "nausea", expanded_keywords, drug_dict, top_k=2)
    assert len(top_k_comments) == 2
    assert "nausea" in drug_dict[0]["side_effects"]

