from typing import Dict, List

chat_state = {
    "fb_post_info": {},          # 使用者貼文資訊（例如：地點、租金）
    "user_questions": [],        # 使用者問過的問題
    "issues_reported": [],       # 使用者提過的租屋糾紛
    "region_context": None,      # 租屋區域
    "last_topic_type": None,      # 上次的任務類型
    "update_chance":True
}
def update_state(user_input: str, classification: str, extracted_data: Dict = None):
    global chat_state

    # 根據分類更新不同欄位
    chat_state["last_topic_type"] = classification

    if classification == "greeting":
        # 無須紀錄
        return

    elif classification == "legal":
        chat_state["user_questions"].append(user_input)
        # 簡易抓問題主題，可改為 NER、關鍵字(未來可以再改方式或增加類別)
        if "漲租" in user_input:
            chat_state["issues_reported"].append("房東漲租")
        elif "押金" in user_input:
            chat_state["issues_reported"].append("押金糾紛")

    elif classification == "rental_post":
        if extracted_data:
            chat_state["fb_post_info"].update(extracted_data)
            # 嘗試從地點推斷區域
            if not chat_state["region_context"] and "地點" in extracted_data:
                chat_state["region_context"] = extracted_data["地點"]

    elif classification == "unknown":
        chat_state["user_questions"].append(user_input)

def construct_prompt_with_state(user_input: str):
    prompt = f"使用者提問：{user_input}\n"

    if chat_state["fb_post_info"]:
        fb_summary = "\n".join([f"{k}：{v}" for k, v in chat_state["fb_post_info"].items()])
        prompt += f"\n目前收集到的租屋資訊如下：\n{fb_summary}\n"

    if chat_state["issues_reported"]:
        issue_summary = ", ".join(chat_state["issues_reported"])
        prompt += f"\n使用者曾提過的問題：{issue_summary}\n"

    if chat_state["region_context"]:
        prompt += f"\n地區脈絡：{chat_state['region_context']}\n"

    return prompt

def gen_prompt(user_input):
    return f"""[INST] <<SYS>>
你是一個專業的法律助理，請根據提供的資訊回答問題。
<</SYS>>

{user_input} [/INST]"""

def generate_response(model,tokenizer, prompt, max_new_tokens=128):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=0.5,
        top_p=0.9,
        repetition_penalty=1.2,
        pad_token_id=tokenizer.eos_token_id
    )
    result = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return result.strip()