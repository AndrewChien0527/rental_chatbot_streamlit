import streamlit as st
from back_end import chatbot_response  # Your chatbot logic

st.set_page_config(page_title="租屋助理聊天機器人", page_icon="🤖")
st.title("🏡 租屋助理聊天機器人")

# Initialize conversation state
if "chat_state" not in st.session_state:
    st.session_state.chat_state = {
        "fb_post_info": {},
        "user_questions": [],
        "issues_reported": [],
        "region_context": None,
        "last_topic_type": None,
        "update_chance": True
    }

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"text": "你好，我是你的租屋助理！有什麼我可以幫忙的嗎？", "is_user": False}
    ]

# Display chat history
for msg in st.session_state.messages:
    role = "user" if msg["is_user"] else "assistant"
    with st.chat_message(role):
        st.markdown(msg["text"])

# User input
if user_input := st.chat_input("請輸入訊息…"):
    # Show user message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"text": user_input, "is_user": True})

    # Generate bot reply
    bot_reply = chatbot_response(user_input, st.session_state.chat_state)

    # Show bot reply
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
    st.session_state.messages.append({"text": bot_reply, "is_user": False})
