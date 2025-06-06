import streamlit as st
import easyocr
import fitz
from utils.rag import rag_lookup
from utils.flow_manage import gen_prompt, generate_response
import re
def extract_text_from_pdf(uploaded_file):
    # Read the uploaded file as a stream
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def add_chat(role, content):
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

import re
def analyze_contract(text):
    # 關鍵條款比對表：{ regex: (風險說明, 違反定型化契約?, 建議文字) }
    unfair_patterns = {
        r"押金不予退還": (
            "押金全額不退，可能導致租客損失重大資金。",
            True,
            "押金應於租約結束後無違約情況下退還，建議您要求明確退還機制。"
        ),
        r"甲方有權無條件.*押金": (
            "甲方可無條件扣押押金，租客缺乏保障。",
            True,
            "建議將押金扣除標準明列於契約中，如實際修繕費用、發票佐證等。"
        ),
        r"每日加收\d+%逾期利息": (
            "逾期租金將被高額利息懲罰，增加租客負擔。",
            True,
            "內政部契約建議逾期利息不得超過年利率10%，建議調整。"
        ),
        r"不得異議": (
            "租客無法對不公平條款提出異議，權益受限。",
            True,
            "建議移除此字眼，契約雙方應有平等表意與協議權利。"
        ),
        r"甲方得立即終止契約": (
            "甲方可隨意終止契約，租客不易保障租屋權益。",
            True,
            "除非重大違約，房東終止契約應有合理通知期。"
        ),
        r"不得拒絕甲方.*進入房屋": (
            "租客無法阻擋房東或其親友進入，隱私權可能受侵犯。",
            True,
            "依定型契約，房東應提前通知並經同意後進入房屋。"
        ),
        r"違者甲方得立即驅逐": (
            "租客稍有違規即被驅逐，權益不易保障。",
            True,
            "建議設立合理違規程序與改善期，保障雙方權益。"
        ),
        r"甲方得強制驅逐": (
            "甲方有強制驅逐權，可能導致租客失去住所。",
            True,
            "依法驅離須由法院裁定，不得自行驅離，請刪除該條。"
        ),
        r"不得提出任何法律訴訟": (
            "租客喪失透過法律途徑維權的權利。",
            True,
            "此條違反憲法基本權利，建議立即刪除。"
        ),
        r"甲方單方面解釋決定": (
            "契約條款解釋權完全在房東，租客無法抗辯。",
            True,
            "契約應雙方協議解釋，建議刪除此條。"
        )
    }

    combined_pattern = re.compile("|".join(unfair_patterns.keys()), flags=re.IGNORECASE)
    unfair_clauses = []

    for paragraph in text.split("\n"):
        match = combined_pattern.search(paragraph)
        if match:
            clause = paragraph.strip()
            for pattern, (desc, is_violation, advice) in unfair_patterns.items():
                if re.search(pattern, clause, flags=re.IGNORECASE):
                    unfair_clauses.append({
                        "clause": clause,
                        "consequence": desc,
                        #"violation": is_violation,
                        "advice": advice
                    })
                    break

    return unfair_clauses


def display_analysis(analysis):
    if not analysis:
        add_chat("assistant", "✅ 未發現明顯的不公平條款，但請您仍詳細閱讀條文並保持警覺。")
        return

    all_results = "🔍 **不公平條款偵測結果**\n\n"
    for idx, item in enumerate(analysis, 1):
        #violation_tag = "🛑 違反定型化契約" if item["violation"] else "⚠️ 可能風險"
        all_results += f"""
### 第 {idx} 條
> `{item['clause']}`
📉 **影響說明**：{item['consequence']}  
🛠️ **建議調整**：{item['advice']}
---
"""
    all_results += f"\n📘 共偵測到 **{len(analysis)}** 條可能不公平條款。建議與房東確認或諮詢專業律師。"
    add_chat("assistant", all_results)

def render_input_sidebar():
    st.header("📄 契約文件分析區")

    uploaded_file = st.file_uploader("上傳契約文件", type=["jpg", "jpeg", "png", "pdf"])
    if uploaded_file:
        with st.spinner("正在辨識與分析..."):
            extracted_text = handle_file_upload(uploaded_file)
            st.session_state.current_data["text"] = extracted_text
            st.success("✅ 成功辨識，請檢視分析結果")

            #with st.expander("📃 原始契約文字"):
            #    st.text_area("契約原文", extracted_text, height=250, key="orig_contract")

            contract_text = st.text_area("✏️ OCR 辨識結果（可修改）", extracted_text, height=300, key="editable_contract")
            analysis = analyze_contract(contract_text)
            
            if st.button("🔍 重新分析"):
                st.session_state.current_data["text"] = contract_text
                analysis = analyze_contract(contract_text)
            st.session_state.current_data["analysis"] = analysis
            display_analysis(analysis)

    if st.button("🔄 清除分析與對話"):
        st.session_state.clear()
def render_chat_interface():
    st.header("💬 合約諮詢小助理")
    if "intro_shown" not in st.session_state:
        st.session_state.intro_shown = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
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

💡 建議使用內政部的[「定型化租賃契約」](https://www.ey.gov.tw/Page/AABD2F12D8A6D561/58973c69-07f0-4b88-88a2-8b0b91f28241)作為參考，保障雙方權益。
"""
        add_chat("assistant", intro_msg)
        st.session_state.intro_shown = True
    # Display chat history
    for msg in st.session_state.get("messages", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_text = st.chat_input("請輸入問題")
    if user_text and user_text.strip():
        add_chat("user", user_text.strip())
        try:
            with st.spinner("思考中..."):
                context = rag_lookup(user_text, top_k=3, threshold=0.1)
                prompt = gen_prompt(user_text, history=intro_msg, context=context)
                answer = generate_response(prompt)
            add_chat("assistant", answer)
        except Exception as e:
            add_chat("assistant", f"⚠️ 發生錯誤：{str(e)}")

def handle_contract_checklist():
    if "saved_listings" not in st.session_state:
        st.session_state.saved_listings = []
    if "ignored_slots" not in st.session_state:
        st.session_state.ignored_slots = set()
    if "current_data" not in st.session_state:
        st.session_state.current_data = {}

    # Layout
    col2, col1 = st.columns([2, 1])
    
    with col1:
        render_input_sidebar()
    with col2:
        render_chat_interface()
