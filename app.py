import streamlit as st
from handlers.post_analysis import handle_post_analysis
from handlers.contract_checklist import handle_contract_checklist
from handlers.common_problems import handle_common_problem,handle_first_rent,handle_tax
from handlers.post_analysis import handle_post_analysis

st.set_page_config(page_title="租屋助理", layout="wide")
st.title("🏡 租屋助理聊天機器人")

# 初始化聊天紀錄
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_topic" not in st.session_state:
    st.session_state.current_topic = None
 
def add_chat(role, content):
    with st.chat_message(role):
        st.markdown(content)
    st.session_state.messages.append({"role": role, "content": content})

# 顯示歷史聊天
#for msg in st.session_state.messages:
 #   with st.chat_message(msg["role"]):
  #      st.markdown(msg["content"])
topics = {
    "幫我評估房屋資訊": handle_post_analysis,
    
    "租約簽訂前怎麼檢查？": handle_contract_checklist,
    
    "遇到問題怎麼處理？（水電、室友、房東等）": handle_common_problem,
    "想了解補助、報稅、或法律資源": handle_tax,
    "找房子要注意什麼？": handle_first_rent,}


if "buttons_hidden" not in st.session_state:
    st.session_state.buttons_hidden = False
if not st.session_state.current_topic:
    st.write("請選擇你想了解的主題：")
    for label, handler in topics.items():
        if st.button(label):
            st.session_state.current_topic = label
            st.rerun()
else:
    handler = topics.get(st.session_state.current_topic)
    if handler:
        handler()
    if st.button("🔁 想問其他主題"):
        st.session_state.current_topic = None
        st.session_state.post_input = ""
        st.session_state.clear()  # 清除所有狀態
        st.rerun()
