"""Train a TF-IDF + Nearest-Neighbour retrieval model on the 10,000 Q&A dataset."""
import json, os, sys
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "data", "qa_dataset.jsonl")
MODEL = os.path.join(HERE, "data", "chatbot_model.joblib")


def main():
    if not os.path.exists(DATA):
        print("Dataset not found - generating it first...")
        from generate_dataset import make_pairs
        pairs = make_pairs()
        os.makedirs(os.path.dirname(DATA), exist_ok=True)
        with open(DATA, "w", encoding="utf-8") as f:
            for q, a in pairs:
                f.write(json.dumps({"q": q, "a": a}) + "\n")

    questions, answers = [], []
    with open(DATA, "r", encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            questions.append(row["q"])
            answers.append(row["a"])

    print(f"Loaded {len(questions)} training examples")

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, lowercase=True, stop_words="english")
    X = vectorizer.fit_transform(questions)
    print(f"Feature matrix: {X.shape}")

    nn = NearestNeighbors(n_neighbors=3, metric="cosine")
    nn.fit(X)

    joblib.dump({"vectorizer": vectorizer, "nn": nn, "answers": answers, "questions": questions}, MODEL)
    print(f"Saved model to {MODEL}")


if __name__ == "__main__":
    main()
