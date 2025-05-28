from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
import numpy as np

# Load Q&A from file
def load_qa_from_txt(filename):
    qa_data = []
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    question = None
    answer = None
    for line in lines:
        line = line.strip()
        if line.startswith("Q") or line.startswith("Q:"):
            question = line.split(":", 1)[1].strip()
        elif line.startswith("A") or line.startswith("A:"):
            answer = line.split(":", 1)[1].strip()
        
        if question and answer:
            qa_data.append({"question": question, "answer": answer})
            question = None
            answer = None

    return qa_data

# Load data
qa_data = load_qa_from_txt("rental_qa.txt")

# Embedding model
embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
questions = [item["question"] for item in qa_data]
embeddings = embedding_model.encode(questions)

# Create sklearn NearestNeighbors index
nn_model = NearestNeighbors(n_neighbors=3, metric='euclidean')
nn_model.fit(embeddings)

# RAG lookup function
def rag_lookup(user_input, top_k=3, threshold=0.6):
    query_vec = embedding_model.encode([user_input])
    distances, indices = nn_model.kneighbors(query_vec)

    results = []
    for i in range(top_k):
        dist = distances[0][i]
        idx = indices[0][i]
        if dist < threshold:  # Lower distance = more similar
            answer = qa_data[idx]["answer"]
            results.append((answer, dist))

    # Return best match
    if results:
        results.sort(key=lambda x: x[1])  # sort by distance (ascending)
        return results[0][0]
    else:
        return None


