from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import wordnet
import torch

class BioBERTEmbedder:
    def __init__(self, model_name="dmis-lab/biobert-base-cased-v1.2"):
        """
        Initializes the BioBERT model and tokenizer.
        """
        model_name = "bert-base-uncased"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
       
    # def get_embeddings(self, text):
    #     """
    #     Generate BioBERT embeddings for a given text.
    #     :param text: Input text.
    #     :return: NumPy array representing the text's embedding.
    #     """
    #     inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    #     outputs = self.model(**inputs)
    #     return outputs.last_hidden_state.mean(dim=1).detach().numpy()

# 获取文本的 BERT 嵌入
    def get_embeddings(self, text):
        tokens = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
        with torch.no_grad():
            output = self.model(**tokens)
        return output.last_hidden_state.mean(dim=1).detach().numpy()

class KeywordExpander:
    def __init__(self, embedder: BioBERTEmbedder, side_effects_official):
        """
        Initializes the KeywordExpander with a BioBERT embedder and official side effects.
        :param embedder: An instance of BioBERTEmbedder.
        :param side_effects_official: List of official side effects.
        """
        self.embedder = embedder
        self.side_effects_official = side_effects_official

    def get_wordnet_synonyms(self, initial_keywords):
        """
        Generate synonyms for a list of initial keywords using WordNet.
        :param initial_keywords: List of initial keywords.
        :return: Dictionary of keywords and their synonyms.
        """
        synonyms = {}
        for effect in initial_keywords:
            synonym_set = set()
            words = effect.split(' ') + [effect]
            abandon = ['pain', 'hurt', 'prescribed', 'overdose', 'condition', 'no', 'adverse', 'event', 'intentional', 'to', 'in', 'site', 'decreased', 'increased', 'drug']
            words = [word for word in words if word not in abandon]
            for word in words:
                for syn in wordnet.synsets(word):
                    for lemma in syn.lemmas():
                        synonym_set.add(lemma.name().replace("_", " "))
            synonyms[effect] = list(synonym_set)
        return synonyms

    def find_similar_words(self, target_word, reference_words, threshold=0.8, top_k=10):
        """
        Find words in a reference list similar to a target word using cosine similarity.
        :param target_word: The target word to compare.
        :param reference_words: List of reference words to check similarity with.
        :param threshold: Minimum similarity score to include a word.
        :param top_k: Maximum number of similar words to return.
        :return: List of dictionaries containing words and their similarity scores.
        """
        target_emb = self.embedder.get_embeddings(target_word)[0]
        similarities = []
        for word in reference_words:
            word_emb = self.embedder.get_embeddings(word)[0]
            # sim = cosine_similarity([target_emb], [word_emb])[0][0]
            sim = cosine_similarity([target_emb], [word_emb])[0][0]
            if sim >= threshold:
                similarities.append({word: sim})
        return sorted(similarities, key=lambda x: list(x.values())[0], reverse=True)[:top_k]

    def expand_keywords(self, initial_keywords):
        """
        Expand initial keywords using WordNet synonyms and similarity-based embeddings.
        :param initial_keywords: List of initial keywords to expand.
        :return: Dictionary of expanded keywords and their similarity scores.
        """
        synonyms_kw = self.get_wordnet_synonyms(initial_keywords)
        for word in initial_keywords:
            reference_words = list(set(synonyms_kw[word] + self.side_effects_official + [word]))
            similar_words_emb = self.find_similar_words(word, reference_words)
            synonyms_kw[word] = similar_words_emb
        return synonyms_kw
