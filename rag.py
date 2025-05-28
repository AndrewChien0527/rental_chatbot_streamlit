from sentence_transformers import SentenceTransformer
import faiss

def load_qa_from_txt(filename):
    qa_data = []
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    question = None
    answer = None
    for line in lines:
        line = line.strip()
        if line.startswith("Q") or line.startswith("Q:"):
            question = line.split(":",1)[1].strip()
        elif line.startswith("A") or line.startswith("A:"):
            answer = line.split(":",1)[1].strip()
        # 遇到空行，或問題和答案都有了就存
        if question and answer:
            qa_data.append({"question": question, "answer": answer})
            question = None
            answer = None

    return qa_data
qa_data = load_qa_from_txt("rental_qa.txt")
#print(f"讀取到 {len(qa_data)} 組 QA")

embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
questions = [item["question"] for item in qa_data]
embeddings = embedding_model.encode(questions)

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

def rag_lookup(user_input, top_k=3, threshold=0.6):
    query_vec = embedding_model.encode([user_input], convert_to_numpy=True)
    D, I = index.search(query_vec, top_k)

    results = []
    for i in range(top_k):
        dist = D[0][i]
        idx = I[0][i]
        if dist > threshold:
            answer = qa_data[idx]["answer"]
            results.append((answer, dist))

    # 回傳最相近的答案與其距離
    if results:
        # 按距離排序（小的越好）
        results.sort(key=lambda x: x[1])
        return results[0][0]  # 只回傳答案文字
    else:
        return None

