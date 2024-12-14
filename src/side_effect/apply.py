import sys
import os
import pandas as pd

# 添加项目根目录到 sys.path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(base_dir)

import pandas as pd
from src.side_effect.embedding_and_keywords import BioBERTEmbedder, KeywordExpander
from src.side_effect.analysis import get_comment_similarity, evaluate_score, comment_side_effect
from src.side_effect.data_processing import get_comment_dict, get_drugs, pick_drug, get_merged_data
from src.side_effect.embedding_and_keywords import BioBERTEmbedder, KeywordExpander
from src.side_effect.analysis import (
    get_comment_similarity,
    evaluate_score,
    comment_side_effect,
)
from src.side_effect.data_processing import get_comment_dict, get_drugs, pick_drug



class SideEffectAnalyzer:
    def __init__(
        self,
        initial_keywords,
        side_effects_official,
        model_name="dmis-lab/biobert-base-cased-v1.2"
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
        comment_dict = get_comment_dict(data, "cleaned_comments")
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
                print(f"Processing {kw} for {drug}")
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
    reddit_df = get_merged_data("data/cleaned_reddit")

    data = pd.concat([cleaned_simulants, cleaned_non_simulants, reddit_df])

    filtered_data = data[data['cleaned_comments'].apply(lambda x: len(str(x).split()) <= 512)]
    # m = max([len(x.split()) for x in filtered_data['cleaned_comments']])
    # print(m)

    data = filtered_data.drop_duplicates(subset = ['Drug Name', 'Review Text'])
    data = data.dropna()
    data.to_csv("reviews.csv", index=False)


    # Step 8: Analyze reddit reviews
    print("Analyzing reviews...")
    # reddit_results = analyzer.process_file("reviews.csv")
    new_comment_dict, side_effect_scores, top_k_comments = analyzer.process_file("reviews.csv")
    print(new_comment_dict)
    print(side_effect_scores)
    print(top_k_comments)

    df = pd.DataFrame([
        {"drug": drug, "side_effect": side_effect, "score": score}
        for drug, effects in side_effect_scores.items()
        for side_effect, score in effects.items()
    ])

    # pd.DataFrame(new_comment_dict).to_csv("new_comment_dict.csv", index=False)
    # df.to_csv("side_effect_scores.csv", index=False)
    # pd.DataFrame(top_k_comments).to_csv("top_k_comments.csv", index=False)

    pd.DataFrame(new_comment_dict).to_csv("new_comment_dict_bert.csv", index=False)
    df.to_csv("side_effect_scores_bert.csv", index=False)
    pd.DataFrame(top_k_comments).to_csv("top_k_comments_bert.csv", index=False)



    # # Step 5: Save results
    # print("Saving results...")
    # output_dir = "output/"
    # os.makedirs(output_dir, exist_ok=True)


    # # Save results for each drug
    # for drug, scores in side_effect_scores.items():
    #     scores_df = pd.DataFrame(
    #         [{"Side Effect": se, "Score": sc} for se, sc in scores.items()]
    #     ).sort_values(by="Score", ascending=False)

    #     # Mark Top 5 and Bottom 5
    #     scores_df["Type"] = ["Top 5"] * 5 + ["Bottom 5"] * 5 if len(scores_df) > 10 else ["Top" if i < 5 else "Bottom" for i in range(len(scores_df))]

    #     # Get comments for the drug
    #     drug_comments = [c for c in top_k_comments if c["drug"] == drug]

    #     # Merge scores and comments
    #     results = []
    #     for _, row in scores_df.iterrows():
    #         side_effect = row["Side Effect"]
    #         related_comments = [c for c in drug_comments if c["side_effect"] == side_effect]
    #         for comment in related_comments:
    #             results.append({
    #                 "Drug": drug,
    #                 "Side Effect": side_effect,
    #                 "Score": row["Score"],
    #                 "Type": row["Type"],
    #                 "Comment": comment["comment"],
    #                 "Comment Score": comment["score"]
    #             })

    #     # Save to a CSV file for the drug
    #     pd.DataFrame(results).to_csv(f"{output_dir}/{drug}_results.csv", index=False)

    # # Save overall side effect scores
    # overall_scores = [
    #     {"Drug": drug, "Side Effect": se, "Score": sc} for drug, scores in side_effect_scores.items() for se, sc in scores.items()
    # ]
    # pd.DataFrame(overall_scores).to_csv(f"{output_dir}/overall_side_effect_scores.csv", index=False)

    # print("All results saved.")
    for drug, score in side_effect_scores.items():
        # print(drug)
        # print(score)
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
        df.to_csv(f"{drug}_rank_bert.csv", index = False)