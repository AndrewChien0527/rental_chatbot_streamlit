import streamlit as st
def add_chat(role, content):
    with st.chat_message(role):
        st.markdown(content)
    st.session_state.messages.append({"role": role, "content": content})

def handle_common_problem():
   
    add_chat("assistant", "請描述你遇到的問題，我會提供可能處理方式，例如申訴單位、法律依據或溝通技巧。")
    if "post_input" not in st.session_state:
        st.session_state.post_input = ""

    if not st.session_state.post_input:
        user_text = st.chat_input(" ")
        if user_text:
            st.session_state.post_input = user_text
            return f"收到：\n\n🧐 分析中……（你提供的是：{user_text})"
        else:
            return "請提供事實內容，我才能幫你判斷是否有風險。"
    else:
        # simulate analysis
        return "✅ 根據你提供的資訊，以下是建議您的應對方式。"