import streamlit as st
import easyocr
import fitz
from utils.rag import rag_lookup
from utils.flow_manage import gen_prompt, generate_response
def extract_text_from_pdf(uploaded_file):
    # Read the uploaded file as a stream
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def add_chat(role, content):
    with st.chat_message(role):
        st.markdown(content)
    st.session_state.messages.append({"role": role, "content": content})


reader = easyocr.Reader(['ch_tra'])
def extract_text_from_image(image_path):
    result = reader.readtext(image_path, detail=0, paragraph=True)
    return '\n'.join(result)

def handle_file_upload(uploaded_file):
    if uploaded_file.type in ["image/jpeg", "image/png"]:
        return extract_text_from_image(uploaded_file)
    elif uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)
    else:
        return "Unsupported file type."


def analyze_contract(text):
    clauses = []
    risks = []
    if "提前解約" in text:
        clauses.append("提前解約條款")
    if "違約金" in text:
        risks.append("可能存在違約金條款")
    return {"clauses": clauses, "risks": risks}

def handle_contract_checklist():
    if "intro_shown" not in st.session_state:
        st.session_state.intro_shown = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if st.button("🔄 清除對話"):
        st.session_state.clear()
        st.rerun()
    if not st.session_state.intro_shown:
        intro_msg = """
以下是您在簽訂租屋契約前應該特別注意的重要事項：

1. **確認房東身分與產權**  
   - 要求出示房屋權狀或房屋稅單，確認房東是否為合法擁有人。  
   - 若非屋主本人簽約，須確認是否有合法委託書。

2. **檢查房屋現況與設備**  
   - 親自查看房屋現況，確認與廣告內容一致。  
   - 記錄房內家具、家電與其損耗狀況，可用拍照或影片方式保存證據。

3. **詳細閱讀並確認租賃契約內容**  
   - 包括租金、押金、租期、繳款方式、水電費與其他雜費的分擔方式。  
   - 確認是否允許轉租、養寵物、訪客過夜等條款。  
   - 應要求簽署書面契約，避免僅口頭約定。

4. **押金與租金的支付與收據**  
   - 押金不得超過兩個月租金。  
   - 租金應定期支付，付款後應索取正式收據或匯款證明。

5. **提前解約與違約條款**  
   - 明確規定提前解約的條件與違約金額，避免爭議。  
   - 若有違反條約的情況，需清楚定義雙方責任。

6. **報修與維修責任歸屬**  
   - 明訂房屋設備損壞由哪一方負責維修。  
   - 建議在契約中載明日後修繕與維護的責任歸屬。

7. **警惕二房東或非法轉租**  
   - 檢查房東是否為真正屋主，避免遭遇二房東非法轉租的情況。  
   - 可向地政事務所查詢產權登記資料。

8. **避免口頭承諾，盡量白紙黑字**  
   - 所有重要條件應以書面列入契約內，保障雙方權益。

9. **確認是否需報稅及是否開立租金發票**  
   - 有些房東未依法報稅，租客可能無法報稅或申請補助。

10. **租屋保險與火災責任**  
    - 建議了解是否需購買租屋險，並清楚火災或意外事故責任歸屬。

---

💡 建議使用內政部的「定型化租賃契約」作為參考，保障雙方權益。
"""
        add_chat("assistant", intro_msg)
        st.session_state.intro_shown = True
    user_text = st.chat_input("請輸入問題")
    if "post_input" not in st.session_state:
        st.session_state.post_input = ""
    uploaded_file = st.file_uploader("上傳租賃契約文件", type=["jpg", "jpeg", "png", "pdf"])
    if uploaded_file:
        extracted_text = handle_file_upload(uploaded_file)
        analysis = analyze_contract(extracted_text)
        add_chat("assistant", f"分析結果：\n\n條款：{analysis['clauses']}\n風險：{analysis['risks']}")
    if user_text and user_text.strip():
        add_chat("user", user_text.strip())

        try:
            with st.spinner("思考中..."):
                # Do RAG retrieval
                context = rag_lookup(user_text, top_k=3, threshold=0.1)
                if not context:
                    context = "（無相關資料）"

                # Generate prompt + response
                prompt = gen_prompt(user_text, context=context)
                answer = generate_response(prompt)

            # Display answer
            add_chat("assistant", answer)

        except Exception as e:
            add_chat("assistant", f"⚠️ 發生錯誤：{str(e)}")