import streamlit as st
from utils.slot_extract import rule_based_extract,slot_info

def add_chat(role, content):
    with st.chat_message(role):
        st.markdown(content)
    st.session_state.messages.append({"role": role, "content": content})
'''
def handle_post_analysis():
    

    add_chat("assistant", "請貼上你看到的租屋貼文或與房東/仲介的對話，我可以幫你分析是否有風險或違法。")
    if "post_input" not in st.session_state:
        st.session_state.post_input = ""

    if not st.session_state.post_input:
        user_text = st.chat_input(" ")
        if user_text:
            st.session_state.post_input = user_text
            return f"收到貼文內容：\n\n🧐 分析中……（你提供的是：{user_text})"
        else:
            return "請提供貼文內容，我才能幫你判斷是否有風險。"
    else:
        # simulate analysis
        return "✅ 根據你提供的資訊，此貼文內容存在一些疑點，例如未簽約、租金過低或無權出租等。建議勿貿然聯絡。"
        '''
def handle_post_analysis():
    #add_chat("assistant", "請貼上你看到的租屋貼文或與房東/仲介的對話，我可以幫你分析是否有風險或違法。")

    if "post_input" not in st.session_state:
        st.session_state.post_input = ""

    if "ignored_slots" not in st.session_state:
        st.session_state.ignored_slots = set()

    user_text = st.chat_input("請貼上租屋資訊後按 Enter")

    if user_text:
        st.session_state.post_input = user_text
        add_chat("user", user_text)

    if st.session_state.post_input:
        post_text = st.session_state.post_input
        extracted = rule_based_extract(post_text, slot_info)

        # --- Sidebar: Form ---
        with st.sidebar:
            st.header("📋 表單欄位（可編輯）")
            edited_data = {}
            for slot in slot_info.keys():
                default_val = extracted.get(slot, "無")
                if isinstance(default_val, dict):
                    default_val = ", ".join([f"{k}: {v}" for k, v in default_val.items()])
                col1, col2 = st.columns([4, 1])
                with col1:
                    edited_data[slot] = st.text_input(f"{slot}", value=default_val, key=f"slot_{slot}")
                with col2:
                    ignore = st.checkbox("忽略", key=f"ignore_{slot}")
                    if ignore:
                        st.session_state.ignored_slots.add(slot)
                    else:
                        st.session_state.ignored_slots.discard(slot)

        # --- Main Chat: Feedback Analysis ---
        warnings = []
        for slot, value in edited_data.items():
            if slot in st.session_state.ignored_slots:
                continue
            if not value or value.strip() == "" or value.strip() == "無":
                warnings.append(
                    f"- **{slot}**：{slot_info[slot]['consequence']}\n 建議：{slot_info[slot]['advice']}"
                )

        if warnings:
            with st.chat_message("assistant"):
                st.markdown("⚠️ 以下欄位可能有缺漏，建議補充：\n\n" + "\n\n".join(warnings))
        else:
            add_chat("assistant", "✅ 表單欄位完整，未發現明顯風險。")
