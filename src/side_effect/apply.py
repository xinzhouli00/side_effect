import sys
import os
import pandas as pd

# 添加项目根目录到 sys.path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(base_dir)

import pandas as pd
from src.side_effect.embedding_and_keywords import BioBERTEmbedder, KeywordExpander
from src.side_effect.analysis import get_comment_similarity, evaluate_score, comment_side_effect
from src.side_effect.data_processing import prepare_comment_dict, get_drugs, pick_drug, get_merged_data, get_negative_comment, prepare_comment_dict
from src.side_effect.embedding_and_keywords import BioBERTEmbedder, KeywordExpander
from src.side_effect.analysis import (
    get_comment_similarity,
    evaluate_score,
    comment_side_effect,
)
import argparse
import logging

logging.basicConfig(
    filename="logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w",
)

def log_progress(message):
    logging.info(message)
    print(message)



class SideEffectAnalyzer:
    def __init__(self, initial_keywords, side_effects_official, model_name="dmis-lab/biobert-base-cased-v1.2"):
        """
        Initializes the SideEffectAnalyzer with initial keywords and a BioBERT model.
        :param initial_keywords: List of initial side effect keywords.
        :param side_effects_official: List of official side effects.
        :param model_name: Name of the BioBERT model to use.
        """
        self.initial_keywords = initial_keywords
        self.embedder = BioBERTEmbedder(model_name)
        self.keyword_expander = KeywordExpander(self.embedder, side_effects_official)

    def process_file(self, file_path, drugs, initial_keywords):
        """
        Processes a CSV file containing drug reviews.
        :param file_path: Path to the CSV file.
        :return: Updated comment dictionary, side effect scores, and top comments.
        """
        # Load and preprocess data
        data = pd.read_csv(file_path)

        # Prepare comment dictionary and drug list
        comment_dict = prepare_comment_dict(data, "cleaned_comments")
        self.initial_keywords = initial_keywords

        new_comment_dict = []
        side_effect_scores = {}
        top_k_comments = []

        log_progress("Begin iterate over drugs...")
        for drug in drugs:
            log_progress(f"Processing drug: {drug}")
            # Filter comments for the specific drug
            drug_dict, comments = pick_drug(comment_dict, drug)
            log_progress("Embedding comments...")
            # Generate embeddings for comments
            embeddings = [self.embedder.get_embeddings(comment)[0] for comment in comments]

            # Expand keywords
            expanded_keywords = self.keyword_expander.expand_keywords(self.initial_keywords)

            # Analyze side effects
            side_effect_score = {}
            for kw in self.initial_keywords:
                # Calculate similarity between keywords and comments
                log_progress(f"Processing {kw} for {drug}")
                kw_comment_similarities = get_comment_similarity(kw, expanded_keywords, embeddings)
                # Evaluate overall score for the keyword
                score = evaluate_score(kw_comment_similarities, kw, expanded_keywords)
                side_effect_score[kw] = score

                # Match comments with side effects and rank
                drug_dict, top_k_comment = comment_side_effect( kw_comment_similarities, kw, expanded_keywords, drug_dict )
                top_k_comments.extend(top_k_comment)

            new_comment_dict.extend(drug_dict)
            side_effect_scores[drug] = side_effect_score

            log_progress(f"Side effect scores for {drug}: {side_effect_score}\n")
        print(new_comment_dict)
        return new_comment_dict, side_effect_scores, top_k_comments


def prepare_data(file_path):
    # Preprocess and save cleaned reviews for simulants
    log_progress("Processing and cleaning simulants reviews...")
    simulants_data = pd.read_csv("data/simulants_reviews.csv")
    simulants_data["Review Text"] = simulants_data["Review Text"].str.replace("For ADHD", "", regex=False)
    simulants_data = simulants_data.drop(columns=["Condition"], errors="ignore")
    # Clean reviews using prepare_comment_dict
    simulants_comment_dict = prepare_comment_dict(simulants_data, "Review Text")
    # Save cleaned reviews
    cleaned_simulants = pd.DataFrame(simulants_comment_dict)

    # Repeat the process for non-simulants
    log_progress("Processing and cleaning non-simulants reviews...")
    non_simulants_data = pd.read_csv("data/non_simulants_reviews.csv")
    non_simulants_data["Review Text"] = non_simulants_data["Review Text"].str.replace("For ADHD", "", regex=False)
    non_simulants_data = non_simulants_data.drop(columns=["Condition"], errors="ignore")
    # Clean reviews using prepare_comment_dict
    non_simulants_comment_dict = prepare_comment_dict(non_simulants_data, "Review Text")
    # Save cleaned reviews
    cleaned_non_simulants = pd.DataFrame(non_simulants_comment_dict)

    # Process reddit reviews
    log_progress("Processing and cleaning reddit reviews...")
    reddit_df = get_merged_data("data/cleaned_reddit")

    # Combine dataset
    data = pd.concat([cleaned_simulants, cleaned_non_simulants, reddit_df])
    data = get_negative_comment(data)

    # Clean dataset
    filtered_data = data[data['cleaned_comments'].apply(lambda x: len(str(x).split()) <= 512)]
    data = filtered_data.drop_duplicates(subset = ['Drug Name', 'Review Text'])
    data = data.dropna()
    data = data.drop(columns = ['index'])

    # Save dataset to file
    data.to_csv(file_path, index=False)

def parse_choices(value):
    list = value.split(',')
    list = [l.lower() for l in list]
    return list

if __name__ == "__main__":
     
    # Allow user interact in terminal
    parser = argparse.ArgumentParser(description="Durg_Side_Effect_Search")
    parser.add_argument("-d", "--drug", type = parse_choices, help = "Input a drug name")
    parser.add_argument("-se", "--side_effect", type = parse_choices, help = "Input a side_effect")
    parser.add_argument("--process_data", action = "store_true")
    args = parser.parse_args()

    file_path = "data/reviews.csv"

    # If user called process_data, apply prepare_data function to build precessed dataset and save to certain path. Terminate  running.
    if args.process_data:
        log_progress("Preparing data ...")
        prepare_data(file_path)
        sys.exit()
    
    # Step 1: Setup official side effects
    side_effects_df = pd.read_csv("data/side_effects.csv")
    side_effects_official = [effect.lower() for effect in side_effects_df['Reaction']]

    log_progress("Data are ready!")
    
    # Step 2: Deal with user's request if needed. If no argument parsed, use default value
    # By default, initial_keywords will be set to the official side effect, drugs will set to all drugs in our dataset
    data = pd.read_csv(file_path)
    comment_dict = prepare_comment_dict(data, "cleaned_comments")
    drugs = get_drugs(data)
    if args.drug:
        assert all(drug in drugs for drug in args.drug), f"This drug is not included in the list: {[drug for drug in args.drug if drug not in drugs]}"
        drugs = args.drug
    print(drugs)

    initial_keywords = side_effects_official
    if args.side_effect:
        initial_keywords = args.side_effect

    # Step 3: Initialize the SideEffectAnalyzer
    analyzer = SideEffectAnalyzer(initial_keywords, side_effects_official)

    # Step 4: Analyze reddit reviews
    log_progress("Analyzing reviews...")
    new_comment_dict, side_effect_scores, top_k_comments = analyzer.process_file(file_path, drugs, initial_keywords)
    log_progress("Saving results to files ...")
    print(new_comment_dict)
    print(side_effect_scores)
    print(top_k_comments)

    # Step 5: Save results to file
    df = pd.DataFrame([
        {"drug": drug, "side_effect": side_effect, "score": score}
        for drug, effects in side_effect_scores.items()
        for side_effect, score in effects.items()
    ])

    pd.DataFrame(new_comment_dict).to_csv("output/new_comment_dict.csv", index=False)
    df.to_csv("output/side_effect_scores.csv", index=False)
    pd.DataFrame(top_k_comments).to_csv("output/top_k_comments.csv", index=False)


    # Step 6: Calculate side effect rank for each drug
    log_progress("Calculate ranks...")
    for drug, score in side_effect_scores.items():
        k = 5
        rank_score = sorted(score.items(), key=lambda x: x[1], reverse=True)
        top_k = dict(sorted(score.items(), key=lambda x: x[1], reverse=True)[:k])
        tail_k = dict(sorted(score.items(), key=lambda x: x[1], reverse=False)[:k])
        rank_top = {f"top {i + 1}": key for i, (key, _) in enumerate(top_k.items())}
        rank_tail = {f"tail {i + 1}": key for i, (key, _) in enumerate(tail_k.items())}
        rank = {**rank_top, **rank_tail}
        rank_df = pd.DataFrame(rank.items(), columns=["rank", "side_effect"])
        se_col = []
        comment_col = []
        for se in rank_df['side_effect']:
            se_tmp = []
            comment_tmp = []
            for item in top_k_comments:
                if item['drug'] == drug and item['side_effect'] == se:
                    se_tmp.append(se)
                    comment_tmp.append(item['comment'])
            se_col.extend(se_tmp[:k])
            comment_col.extend(comment_tmp[:k])
        print(se_col)
        comment_df = pd.DataFrame({'side_effect': se_col, 'comment': comment_col})
        df = rank_df.merge(comment_df, how = 'left')
        log_progress(f"Save side effect scores for {drug}...")
        df.to_csv(f"output/{drug}_rank.csv", index = False)