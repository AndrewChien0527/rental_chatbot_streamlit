import streamlit as st
from utils.rag import rag_lookup
from utils.flow_manage import gen_prompt, generate_response


def add_chat(role, content):
    with st.chat_message(role):
        st.markdown(content)
    st.session_state.messages.append({"role": role, "content": content})
# utils/conversation.py



def build_history(user_input, context=""):
    messages = st.session_state.get("messages", [])
    history_text = ""
    for msg in messages:
        role = "使用者" if msg["role"] == "user" else "助理"
        history_text += f"{role}：{msg['content']}\n"
    return history_text
   


def handle_common_problem(intro_msg = "請描述你遇到的問題，我會提供可能處理方式，例如申訴單位、法律依據或溝通技巧。"):
    # Initialize session state once
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "intro_shown" not in st.session_state:
        st.session_state.intro_shown = False

    # Render Clear Chat button at the top (not sidebar)
    if st.button("🔄 清除對話"):
        st.session_state.clear()
        st.rerun()

    # Display existing chat 
    '''
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    '''
    # Show the intro message only once
    if not st.session_state.intro_shown:
        intro_msg = intro_msg
        add_chat("assistant", intro_msg)
        st.session_state.intro_shown = True

    # Wait for user input
    user_text = st.chat_input("請輸入問題")
    if user_text and user_text.strip():
        add_chat("user", user_text.strip())

        try:
            with st.spinner("思考中..."):
                # Do RAG retrieval
                context = rag_lookup(user_text, top_k=3, threshold=0.5)
                if not context:
                    context = ""

                # Generate prompt + response
                prompt = gen_prompt(user_text,history=build_history(), context=context)
                answer = generate_response(prompt)

            # Display answer
            add_chat("assistant", answer)

        except Exception as e:
            add_chat("assistant", f"⚠️ 發生錯誤：{str(e)}")
