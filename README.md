# 🏠 Rental Chatbot Streamlit

A lightweight, CPU-friendly rental chatbot built with Streamlit, designed to assist users with rental-related questions and rental listing analysis — particularly for the Taiwanese rental market. This project uses a combination of traditional rule-based techniques and small language models (SLMs), with optional vector retrieval (RAG) support.

---

## 🌟 Features

- **ChatGPT-style web interface** via Streamlit
- **Intent classification** (greeting, rental post analysis, general Q&A, etc.)
- **Slot extraction** from Facebook-style rental posts (e.g., location, rent, size)
- **Legal and market advice** generation using LLMs or prompts
- **Retrieval-Augmented Generation (RAG)** via FAISS vector index
- **Traditional Chinese support** for Taiwanese users

---

## 🚀 Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/AndrewChien0527/rental_chatbot_streamlit.git
cd rental_chatbot_streamlit
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> 💡 Tip: Create a virtual environment if needed.

### 3. Launch the chatbot

```bash
streamlit run app.py
```

---

## 🧠 How it Works

1. **RAG support**  
   For general rental/legal questions, a simple FAISS-based QA system (`rag.py`) is used to retrieve answers from `rental_qa.txt`.

---

## 📂 Project Structure

```
.
├── app.py                  # Streamlit frontend
├── main.py                 # Core logic dispatcher
├── back_end.py             # Advice generation logic
├── flow_manage.py          # Chat state & flow control
├── classify.py             # Intent classification logic
├── slot_extract.py         # Regex-based slot extraction
├── rag.py                  # FAISS + RAG answer retrieval
├── intent_classifier.pkl   # Pretrained classifier model
├── faiss_index.index       # FAISS vector index
├── qa_embeds.npy           # Embedded QA vectors
├── rental_qa.txt           # Rental/legal QA knowledge base
├── classify_data.csv       # Intent classifier training data
├── slot.csv                # Slot extraction keyword list
├── requirements.txt        # Python dependencies
```

---

## 🔮 Example Use Cases

- Input a Facebook-style rental post → Get extracted info + advice
- Ask general rental/legal questions → Get answers from QA base
- Send incomplete info → Bot will follow up with specific questions
- Use as a base for a full rental legal assistant

---

## 📌 To Do / Future Work

- Integrate map API for location visualization (Leaflet.js / Google Maps)
- Add ML-based NER to improve slot extraction accuracy
- Expand knowledge base with more legal FAQs
- Streamlit Cloud / Hugging Face Spaces deployment
- Add English interface for international users

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 👨‍💻 Author

- **Andrew Chien**
- GitHub: [@AndrewChien0527](https://github.com/AndrewChien0527)

---

> ⚠️ Disclaimer: This chatbot is not a substitute for professional legal advice. Always consult a lawyer for critical legal matters.
