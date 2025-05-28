import streamlit as st


def add_chat(role, content):
    with st.chat_message(role):
        st.markdown(content)
    st.session_state.messages.append({"role": role, "content": content})

def handle_landlord_negotiation():
    
    add_chat("assistant", "請描述房東的要求內容（例如趕人、漲租、拒修），我會幫你評估處理方式與權益保障。")
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