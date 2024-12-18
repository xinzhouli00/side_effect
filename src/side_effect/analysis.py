import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from src.side_effect.embedding_and_keywords import BioBERTEmbedder

embedder = BioBERTEmbedder()


def get_comment_similarity(
    initial_kw, expanded_keywords, comment_embeddings, threshold=0.5
):
    """
    Calculate similarity between expanded keywords and comments.
    :param initial_kw: The initial keyword being analyzed.
    :param expanded_keywords: Dictionary of expanded keywords and their similarity scores.
    :param comment_embeddings: List of comment embeddings.
    :return: Dictionary of keyword-comment similarities.
    """
    exp_kw = [list(item.keys())[0] for item in expanded_keywords[initial_kw]]
    # kw_embeddings = {kw: get_embeddings(kw)[0] for kw in exp_kw}
    kw_embeddings = {kw: embedder.get_embeddings(kw)[0] for kw in exp_kw}
    kw_comment_similarities = {}
    for kw, emb in kw_embeddings.items():
        similarities = cosine_similarity([emb], comment_embeddings)[0]
        kw_comment_similarities[kw] = similarities
    return kw_comment_similarities


def evaluate_score(comment_similarity, initial_kw, expanded_keywords):
    """
    Calculate the overall relevance score for a keyword and comments.
    :param comment_similarity: Dictionary of keyword-comment similarities.
    :param initial_kw: The initial keyword.
    :param expanded_keywords: Dictionary of expanded keywords and their similarity scores.
    :return: Relevance score.
    """
    score = 0
    exp_kw_emb_dict = expanded_keywords[initial_kw]
    exp_kw = [list(item.keys())[0] for item in expanded_keywords[initial_kw]]
    for kw in exp_kw:
        word_score = next(item[kw] for item in exp_kw_emb_dict if kw in item)
        # comment_score = comment_similarity[kw]
        comment_score = np.array(comment_similarity[kw])
        score += sum(word_score * comment_score) / len(comment_score)
    return score


def comment_side_effect(
    comment_similarity, initial_kw, expanded_keywords, drug_dict, top_k=10
):
    """
    Match comments with side effects and rank them by relevance.
    :param comment_similarity: Dictionary of keyword-comment similarities.
    :param initial_kw: The initial keyword.
    :param expanded_keywords: Dictionary of expanded keywords and their similarity scores.
    :param drug_dict: List of dictionaries containing drug metadata.
    :param top_k: Maximum number of comments to return.
    :return: Updated drug_dict and top K comments related to the side effect.
    """
    exp_kw_emb_dict = expanded_keywords[initial_kw]
    exp_kw = [list(item.keys())[0] for item in expanded_keywords[initial_kw]]
    # scores = [0 for _ in range(len(drug_dict))]
    scores = np.zeros(len(drug_dict))
    for kw in exp_kw:
        word_score = next(item[kw] for item in exp_kw_emb_dict if kw in item)
        # comment_score = comment_similarity[kw]
        comment_score = np.array(comment_similarity[kw])
        # scores = list(np.array(scores) + np.array(word_score * comment_score))
        scores += word_score * comment_score
    upper_quartile = np.percentile(scores, 50)
    comment_idx = [i for i in range(len(scores)) if scores[i] >= upper_quartile]
    top_k_comments = []
    for idx in comment_idx:
        drug_dict[idx]["side_effects"].append(initial_kw)
        top_k_comments.append(
            {
                "drug": drug_dict[idx]["Drug Name"],
                "side_effect": initial_kw,
                "comment": drug_dict[idx]["Review Text"],
                "score": scores[idx],
            }
        )
    return (
        drug_dict,
        sorted(top_k_comments, key=lambda x: x["score"], reverse=True)[:top_k],
    )
