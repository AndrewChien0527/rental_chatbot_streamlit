import joblib
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import re
from typing import Dict, List
from utils.rag import rag_lookup
from utils.flow_manage import update_state, construct_prompt_with_state, generate_response
from utils.slot_extract import handle_rental_post

def fallback_or_escalate(user_input):
    escalate_keywords = ["告", "法院", "仲介賠償", "律師", "法律責任"]#可在更動
    if any(kw in user_input for kw in escalate_keywords):
        return "🚨 這可能涉及法律程序，建議諮詢律師或法律專業人士。"
    return None


# 初始化對話狀態
chat_state = {
    "fb_post_info": {},          # 使用者貼文資訊（例如：地點、租金）
    "user_questions": [],        # 使用者問過的問題
    "issues_reported": [],       # 使用者提過的租屋糾紛
    "region_context": None,      # 租屋區域
    "last_topic_type": None,      # 上次的任務類型
    "update_chance":True
}
model_name="liswei/Taiwan-ELM-270M-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name,trust_remote_code=True).eval()#.cuda()
generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
clf = joblib.load('intent_classifier.pkl')
def classify(text):
    emb = embedder.encode([text])
    return clf.predict(emb)[0]

def chat_loop_with_state(model=model, tokenizer=tokenizer, chat_state=chat_state):
    print("開始聊天，輸入空字串可退出")

    while True:
        user_input = input("你：").strip()
        if user_input == "":#空字串結束
            break

        #分類對話意圖+更新狀態
        classification = classify(user_input)
        update_state(user_input, classification)
        print(f"分類：{classification}")

        # 敏感字檢測
        warning = fallback_or_escalate(user_input)
        if warning:
            print("助理：", warning)
            #continue

        if classification == "greeting":#一般問候
            print("助理：哈囉～請問有什麼租屋相關的問題我可以幫忙？")
            continue
        
        elif classification=="other":
            print("請問租屋相關問題或在說的清楚一些")
            continue

        elif classification == "rental_post":#租屋貼文
            result = handle_rental_post(user_input)

            chat_state.setdefault("fb_post_info", {}).update(result["parsed_info"])
            chat_state["last_topic_type"] = "rental_post"
            missing = [k for k, v in result["parsed_info"].items() if v == "無"]
            if missing and chat_state["update_chance"]:
                #chat_state["pending_slots"] = missing
                print("助理：目前\n")
                print(result["advice"]+"建議補充\n")
                chat_state["update_chance"]=False
                continue
            else:
                # 若無缺失，直接產生建議
                print("助理：以下是目前擷取的內容：")
                print(result["parsed_info"])
                print("\n 根據上述內容，這是我的建議：")
                print(result["consequence"])
                continue


        else:
            rag_answer = rag_lookup(user_input)
            if rag_answer:
              print(f"助理（RAG）：{rag_answer}")
            else:
              prompt = construct_prompt_with_state(user_input)
              prompt += "\n請提供與租屋相關的建議或風險提醒："
              answer = generate_response(model,tokenizer,prompt)
              print(f"助理（LLM）：{answer}")

chat_loop_with_state()