import streamlit as st
from rag import rag_lookup
# Assuming rag_lookup is imported or defined in this scope
# And embedding_model, nn_model, qa_data are already initialized

def add_chat(role, content):
    with st.chat_message(role):
        st.markdown(content)
    st.session_state.messages.append({"role": role, "content": content})

def handle_common_problem():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "post_input" not in st.session_state:
        st.session_state.post_input = ""

    # Prompt user to enter problem if no input yet
    if not st.session_state.post_input:
        add_chat("assistant", "請描述你遇到的問題，我會提供可能處理方式，例如申訴單位、法律依據或溝通技巧。")
        user_text = st.chat_input(" ")
        if user_text:
            st.session_state.post_input = user_text
            add_chat("user", user_text)
            st.experimental_rerun()
        else:
            return

    # We have user input, do RAG lookup
    user_text = st.session_state.post_input
    add_chat("assistant", "🧐 分析中……請稍候。")

    answer = rag_lookup(user_text, top_k=3, threshold=0.6)
    if answer:
        add_chat("assistant", f"✅ 我找到相關建議給你：\n\n{answer}")
    else:
        add_chat("assistant", "抱歉，我找不到相關資料。建議您嘗試更詳細描述或聯絡專業人士。")

    # Reset input for next round
    st.session_state.post_input = ""

