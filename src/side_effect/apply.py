import pandas as pd
from src.side_effect.embedding_and_keywords import BioBERTEmbedder, KeywordExpander
from src.side_effect.analysis import get_comment_similarity, evaluate_score, comment_side_effect
from src.side_effect.data_processing import get_comment_dict, get_drugs, pick_drug


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

    def process_file(self, file_path):
        """
        Processes a CSV file containing drug reviews.
        :param file_path: Path to the CSV file.
        :return: Updated comment dictionary, side effect scores, and top comments.
        """
        # Load and preprocess data
        data = pd.read_csv(file_path)
        data['Review Text'] = data['Review Text'].str.replace('For ADHD', '', regex=False)
        data = data.drop(columns=["Condition"], errors='ignore')

        # Prepare comment dictionary and drug list
        comment_dict = get_comment_dict(data, 'Review Text')
        drugs = get_drugs(data)

        new_comment_dict = []
        side_effect_scores = {}
        top_k_comments = []

        for drug in drugs:
            print(f"Processing drug: {drug}")
            # Filter comments for the specific drug
            drug_dict, comments = pick_drug(comment_dict, drug)

            # Generate embeddings for comments
            embeddings = [self.embedder.get_embeddings(comment)[0] for comment in comments]

            # Expand keywords
            expanded_keywords = self.keyword_expander.expand_keywords(self.initial_keywords)

            # Analyze side effects
            side_effect_score = {}
            for kw in self.initial_keywords:
                # Calculate similarity between keywords and comments
                kw_comment_similarities = get_comment_similarity(kw, expanded_keywords, embeddings)
                # Evaluate overall score for the keyword
                score = evaluate_score(kw_comment_similarities, kw, expanded_keywords)
                side_effect_score[kw] = score
                # Match comments with side effects and rank
                drug_dict, top_k_comment = comment_side_effect(kw_comment_similarities, kw, expanded_keywords, drug_dict)

            new_comment_dict.extend(drug_dict)
            side_effect_scores[drug] = side_effect_score
            top_k_comments.extend(top_k_comment)

            print(f"Side effect scores for {drug}: {side_effect_score}\n")

        return new_comment_dict, side_effect_scores, top_k_comments


if __name__ == "__main__":
    # Step 1: Initialize keywords and official side effects
    initial_keywords = ["nausea", "dizziness", "headache", "stomach pain"]
    side_effects_df = pd.read_csv("side_effects.csv")
    side_effects_official = [effect.lower() for effect in side_effects_df['Reaction']]

    # Step 2: Initialize the SideEffectAnalyzer
    analyzer = SideEffectAnalyzer(initial_keywords, side_effects_official)

    # Step 3: Analyze the first dataset (simulants)
    print("Processing simulants reviews...")
    simulants_results = analyzer.process_file("simulants_reviews.csv")

    # Step 4: Analyze the second dataset (non-simulants)
    print("Processing non-simulants reviews...")
    non_simulants_results = analyzer.process_file("non_simulants_reviews.csv")

    # Step 5: Combine results
    combined_comment_dict = simulants_results[0] + non_simulants_results[0]
    combined_side_effect_scores = {**simulants_results[1], **non_simulants_results[1]}
    combined_top_k_comments = simulants_results[2] + non_simulants_results[2]

    # Step 6: Save results to CSV
    print("Saving results to CSV...")
    # Save updated comments dictionary
    pd.DataFrame(combined_comment_dict).to_csv("updated_comments.csv", index=False)
    print("Updated comments saved to 'updated_comments.csv'.")

    # Save side effect scores
    pd.DataFrame([
        {"Drug Name": drug, **scores}
        for drug, scores in combined_side_effect_scores.items()
    ]).to_csv("side_effect_scores.csv", index=False)
    print("Side effect scores saved to 'side_effect_scores.csv'.")

    # Save top K comments
    pd.DataFrame(combined_top_k_comments).to_csv("top_k_comments.csv", index=False)
    print("Top K comments saved to 'top_k_comments.csv'.")