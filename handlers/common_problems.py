import streamlit as st
from rag import rag_lookup
from flow_manage import gen_prompt, generate_response
def add_chat(role, content):
    with st.chat_message(role):
        st.markdown(content)
    st.session_state.messages.append({"role": role, "content": content})

def handle_common_problem():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "intro_shown" not in st.session_state:
        st.session_state.intro_shown = False

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Show initial prompt once
    if not st.session_state.intro_shown:
        intro_msg = "請描述你遇到的問題，我會提供可能處理方式，例如申訴單位、法律依據或溝通技巧。"
        add_chat("assistant", intro_msg)
        st.session_state.intro_shown = True

    # Wait for new input
    user_text = st.chat_input("請輸入問題")
    if user_text:
        add_chat("user", user_text)

        # RAG lookup
        try:
            context = rag_lookup(user_text, top_k=3, threshold=0.1) or "（無相關資料）"
            prompt = gen_prompt(user_text, context=context)
            answer = generate_response(prompt)

            # Show context and answer
            add_chat("assistant", f"{answer}")
            #add_chat("assistant", f"✅ 我生成的建議如下：\n\n{answer}")

        except Exception as e:
            add_chat("assistant", f"⚠️ 發生錯誤：{str(e)}")
