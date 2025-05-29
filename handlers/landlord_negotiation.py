import streamlit as st
from PIL import Image
import pytesseract

# Import your existing prompt and generation functions
from flow_manage import gen_prompt, generate_response  # replace with your actual filename

# Import your model and tokenizer initialization (assuming they are initialized elsewhere)
from back_end import model, tokenizer  # adjust if your setup differs

def extract_text_from_image(image):
    img = Image.open(image)
    text = pytesseract.image_to_string(img, lang='chi_tra+eng')
    return text

def handle_landlord_negotiation():
    st.title("📷 上傳 LINE 對話截圖或輸入文字描述")
    
    uploaded_file = st.file_uploader("上傳圖片", type=["png", "jpg", "jpeg"])
    user_text = ""
    
    if uploaded_file:
        with st.spinner("擷取圖片文字中..."):
            user_text = extract_text_from_image(uploaded_file)
            st.text_area("擷取的文字", user_text, height=300)
    
    if not user_text:
        user_text = st.text_area("請輸入房東要求內容（或上傳截圖）")

    if st.button("分析對話"):
        if not user_text.strip():
            st.warning("請輸入或上傳有效內容")
            return
        
        prompt = gen_prompt(
            f"請根據以下房東要求的描述，判斷是否有不合理或違法行為，並提出應對建議：\n\n{user_text}"
        )
        with st.spinner("分析中..."):
            response = generate_response(model, tokenizer, prompt, max_new_tokens=256)
            st.markdown("### 分析結果")
            st.write(response)




def add_chat(role, content):
    with st.chat_message(role):
        st.markdown(content)
    st.session_state.messages.append({"role": role, "content": content})

def handle_landlord_negotiation123():
    
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