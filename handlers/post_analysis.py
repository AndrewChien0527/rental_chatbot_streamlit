import streamlit as st


def add_chat(role, content):
    with st.chat_message(role):
        st.markdown(content)
    st.session_state.messages.append({"role": role, "content": content})

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