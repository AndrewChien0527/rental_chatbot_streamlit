from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import os

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
questions = [item["question"] for item in qa_data]

# Load embedding model
embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Prepare embeddings
embedding_path = "faiss_index.index"
embedding_data_path = "qa_embeds.npy"

if os.path.exists(embedding_path) and os.path.exists(embedding_data_path):
    # Load existing index and embeddings
    faiss_index = faiss.read_index(embedding_path)
    embeddings = np.load(embedding_data_path)
else:
    # Encode and normalize embeddings (for cosine similarity)
    embeddings = embedding_model.encode(questions, convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(embeddings)

    # Create FAISS index for cosine similarity (use IndexFlatIP + normalized vectors)
    dim = embeddings.shape[1]
    faiss_index = faiss.IndexFlatIP(dim)
    faiss_index.add(embeddings)

    # Save for future use
    faiss.write_index(faiss_index, embedding_path)
    np.save(embedding_data_path, embeddings)

# RAG lookup using FAISS
def rag_lookup(user_input, top_k=3, threshold=0.6):
    query_vec = embedding_model.encode([user_input], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(query_vec)

    # Search top_k results
    similarities, indices = faiss_index.search(query_vec, top_k)

    results = []
    for i in range(top_k):
        sim = similarities[0][i]
        idx = indices[0][i]
        if sim > threshold:  # Higher similarity = more relevant
            answer = qa_data[idx]["answer"]
            results.append((answer, sim))

    if results:
        results.sort(key=lambda x: -x[1])  # sort by similarity (descending)
        return results[0][0]
    else:
        return None

