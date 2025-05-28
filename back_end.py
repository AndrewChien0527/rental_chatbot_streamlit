# chatbot_backend.py (or in your app.py)
import joblib
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from rag import rag_lookup
from flow_manage import update_state, construct_prompt_with_state, generate_response
from slot_extract import handle_rental_post

# Initialize models and classifier once (do this outside the function!)
model_name = "liswei/Taiwan-ELM-270M-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True).eval()
generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
clf = joblib.load('intent_classifier.pkl')

def classify(text):
    emb = embedder.encode([text])
    return clf.predict(emb)[0]

def fallback_or_escalate(user_input):
    escalate_keywords = ["告", "法院", "仲介賠償", "律師", "法律責任"]
    if any(kw in user_input for kw in escalate_keywords):
        return "🚨 這可能涉及法律程序，建議諮詢律師或法律專業人士。"
    return None

def chatbot_response(user_input, chat_state):
    if not user_input.strip():
        return ""

    classification = classify(user_input)
    update_state(user_input, classification, chat_state)  # Pass chat_state here if needed

    warning = fallback_or_escalate(user_input)
    if warning:
        return warning

    if classification == "greeting":
        return "哈囉～請問有什麼租屋相關的問題我可以幫忙？"
    
    elif classification == "other":
        return "請問租屋相關問題或在說的清楚一些"

    elif classification == "rental_post":
        result = handle_rental_post(user_input)
        chat_state.setdefault("fb_post_info", {}).update(result["parsed_info"])
        chat_state["last_topic_type"] = "rental_post"
        missing = [k for k, v in result["parsed_info"].items() if v == "無"]
        if missing and chat_state.get("update_chance", True):
            chat_state["update_chance"] = False
            return f"目前\n{result['advice']} 建議補充"
        else:
            reply = (
                f"以下是目前擷取的內容：\n{result['parsed_info']}\n\n"
                f"根據上述內容，這是我的建議：\n{result['consequence']}"
            )
            return reply

    else:
        rag_answer = rag_lookup(user_input)
        if rag_answer:
            return f"助理（RAG）：{rag_answer}"
        else:
            prompt = construct_prompt_with_state(user_input)
            prompt += "\n請提供與租屋相關的建議或風險提醒："
            answer = generate_response(model, tokenizer, prompt)
            return f"助理（LLM）：{answer}"
