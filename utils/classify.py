from sklearn.neighbors import KNeighborsClassifier
from sentence_transformers import SentenceTransformer
import joblib
import csv
embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
def load_classify_data(csv_path):
    samples = []
    sample_labels = []
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            samples.append(row['text'])
            sample_labels.append(row['label'])  # not 'lable'
    return samples, sample_labels

# Usage
samples, sample_labels = load_classify_data("classify_data .csv")
X = embedder.encode(samples)
clf = KNeighborsClassifier(n_neighbors=2)
clf.fit(X, sample_labels)
joblib.dump(clf, 'intent_classifier.pkl')

def classify(text):
    emb = embedder.encode([text])
    return clf.predict(emb)[0]