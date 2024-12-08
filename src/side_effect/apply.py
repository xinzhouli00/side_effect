import pandas as pd
from side_effect.embedding_and_keywords import BioBERTEmbedder, KeywordExpander
from side_effect.analysis import get_comment_similarity, evaluate_score, comment_side_effect
from side_effect.data_processing import get_comment_dict, get_drugs, pick_drug, get_merged_data
from side_effect.embedding_and_keywords import BioBERTEmbedder, KeywordExpander
from side_effect.analysis import (
    get_comment_similarity,
    evaluate_score,
    comment_side_effect,
)
from side_effect.data_processing import get_comment_dict, get_drugs, pick_drug
import sys
import os
import pandas as pd

# 添加项目根目录到 sys.path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(base_dir)


class SideEffectAnalyzer:
    def __init__(
        self,
        initial_keywords,
        side_effects_official,
        model_name="dmis-lab/biobert-base-cased-v1.2",
    ):
        """
        Initializes the SideEffectAnalyzer with initial keywords and a BioBERT model.
        :param initial_keywords: List of initial side effect keywords.
        :param side_effects_official: List of official side effects.
        :param model_name: Name of the BioBERT model to use.
        """
        self.initial_keywords = initial_keywords
        self.embedder = BioBERTEmbedder(model_name)
        self.keyword_expander = KeywordExpander(self.embedder, side_effects_official)

    def process_file(self, file_path):
        """
        Processes a CSV file containing drug reviews.
        :param file_path: Path to the CSV file.
        :return: Updated comment dictionary, side effect scores, and top comments.
        """
        # Load and preprocess data
        data = pd.read_csv(file_path)
        # data['Review Text'] = data['Review Text'].str.replace('For ADHD', '', regex=False)
        # data = data.drop(columns=["Condition"], errors='ignore')

        # Prepare comment dictionary and drug list
        comment_dict = get_comment_dict(data, "Review Text")
        drugs = get_drugs(data)

        new_comment_dict = []
        side_effect_scores = {}
        top_k_comments = []

        for drug in drugs:
            print(f"Processing drug: {drug}")
            # Filter comments for the specific drug
            drug_dict, comments = pick_drug(comment_dict, drug)

            # Generate embeddings for comments
            embeddings = [
                self.embedder.get_embeddings(comment)[0] for comment in comments
            ]

            # Expand keywords
            expanded_keywords = self.keyword_expander.expand_keywords(
                self.initial_keywords
            )

            # Analyze side effects
            side_effect_score = {}
            for kw in self.initial_keywords:
                # Calculate similarity between keywords and comments
                kw_comment_similarities = get_comment_similarity(
                    kw, expanded_keywords, embeddings
                )
                # Evaluate overall score for the keyword
                score = evaluate_score(kw_comment_similarities, kw, expanded_keywords)
                side_effect_score[kw] = score
                # Match comments with side effects and rank
                drug_dict, top_k_comment = comment_side_effect(
                    kw_comment_similarities, kw, expanded_keywords, drug_dict
                )
                top_k_comments.extend(top_k_comment)

            new_comment_dict.extend(drug_dict)
            side_effect_scores[drug] = side_effect_score
            #top_k_comments.extend(top_k_comment)

            print(f"Side effect scores for {drug}: {side_effect_score}\n")

        return new_comment_dict, side_effect_scores, top_k_comments


if __name__ == "__main__":
    # Step 1: Initialize keywords and official side effects
    side_effects_df = pd.read_csv("data/side_effects.csv")
    side_effects_official = [effect.lower() for effect in side_effects_df['Reaction']]
    initial_keywords = side_effects_official

    # Step 2: Initialize the SideEffectAnalyzer
    analyzer = SideEffectAnalyzer(initial_keywords, side_effects_official)

    # Step 3: Preprocess and save cleaned reviews for simulants
    print("Processing and cleaning simulants reviews...")
    simulants_data = pd.read_csv("data/simulants_reviews.csv")
    simulants_data["Review Text"] = simulants_data["Review Text"].str.replace("For ADHD", "", regex=False)
    simulants_data = simulants_data.drop(columns=["Condition"], errors="ignore")

    # Clean reviews using get_comment_dict
    simulants_comment_dict = get_comment_dict(simulants_data, "Review Text")

    # Save cleaned reviews
    cleaned_simulants = pd.DataFrame(simulants_comment_dict)

    # Step 5: Repeat the process for non-simulants
    print("Processing and cleaning non-simulants reviews...")
    non_simulants_data = pd.read_csv("data/non_simulants_reviews.csv")
    non_simulants_data["Review Text"] = non_simulants_data["Review Text"].str.replace("For ADHD", "", regex=False)
    non_simulants_data = non_simulants_data.drop(columns=["Condition"], errors="ignore")

    # Clean reviews using get_comment_dict
    non_simulants_comment_dict = get_comment_dict(non_simulants_data, "Review Text")

    # Save cleaned reviews
    cleaned_non_simulants = pd.DataFrame(non_simulants_comment_dict)

    # Step 7: Process reddit reviews
    print('Import reddit data...')
    reddit_df = get_merged_data("../../data/cleaned_reddit")

    data = pd.concat([cleaned_simulants, cleaned_non_simulants, reddit_df, ])
    print(data)

    # # Step 3: Preprocess and save cleaned reviews for simulants
    # print("Processing and cleaning simulants reviews...")
    # simulants_data = pd.read_csv("data/simulants_reviews.csv")
    # simulants_data["Review Text"] = simulants_data["Review Text"].str.replace("For ADHD", "", regex=False)
    # simulants_data = simulants_data.drop(columns=["Condition"], errors="ignore")

    # # Clean reviews using get_comment_dict
    # simulants_comment_dict = get_comment_dict(simulants_data, "Review Text")

    # # Save cleaned reviews
    # cleaned_simulants = pd.DataFrame(simulants_comment_dict)
    # cleaned_simulants.to_csv("cleaned_simulants_reviews.csv", index=False)
    # print("Cleaned simulants reviews saved to 'cleaned_simulants_reviews.csv'.")

    # # Step 4: Analyze simulants
    # print("Analyzing simulants reviews...")
    # simulants_results = analyzer.process_file("cleaned_simulants_reviews.csv")

    # # Step 5: Repeat the process for non-simulants
    # print("Processing and cleaning non-simulants reviews...")
    # non_simulants_data = pd.read_csv("data/non_simulants_reviews.csv")
    # non_simulants_data["Review Text"] = non_simulants_data["Review Text"].str.replace("For ADHD", "", regex=False)
    # non_simulants_data = non_simulants_data.drop(columns=["Condition"], errors="ignore")

    # # Clean reviews using get_comment_dict
    # non_simulants_comment_dict = get_comment_dict(non_simulants_data, "Review Text")

    # # Save cleaned reviews
    # cleaned_non_simulants = pd.DataFrame(non_simulants_comment_dict)
    # cleaned_non_simulants.to_csv("cleaned_non_simulants_reviews.csv", index=False)
    # print("Cleaned non-simulants reviews saved to 'cleaned_non_simulants_reviews.csv'.")

    # # Step 6: Analyze non-simulants
    # print("Analyzing non-simulants reviews...")
    # non_simulants_results = analyzer.process_file("cleaned_non_simulants_reviews.csv")

    # # Step 7: Process reddit reviews
    # print('Import reddit data...')
    # reddit_df = get_merged_data("../../data/cleaned_reddit")
    # reddit_dict = get_comment_dict(reddit_df, cleaned_data = True)
    # reddit_df.to_csv("reddit_reviews.csv", index = False)
    # print("Merged reddit reviews saved to 'reddit_reviews.csv'.")

    # # Step 8: Analyze reddit reviews
    # print("Analyzing reddit reviews...")
    # reddit_results = analyzer.process_file("reddit_reviews.csv")

    # # Combine and save results
    # combined_comment_dict = simulants_results[0] + non_simulants_results[0] + reddit_results[0]
    # combined_side_effect_scores = {**simulants_results[1], **non_simulants_results[1], **reddit_results[1]}
    # combined_top_k_comments = simulants_results[2] + non_simulants_results[2] + reddit_results[2]

    # print("Saving results to CSV...")
    # pd.DataFrame(combined_comment_dict).to_csv("updated_comments.csv", index=False)

    # pd.DataFrame(
    #     [
    #         {"Drug Name": drug, **scores}
    #         for drug, scores in combined_side_effect_scores.items()
    #     ]
    # ).to_csv("side_effect_scores.csv", index=False)
    # pd.DataFrame(combined_top_k_comments).to_csv("top_k_comments.csv", index=False)
    # print("Results saved to CSV.")

