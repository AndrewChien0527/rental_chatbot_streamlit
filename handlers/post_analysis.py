import streamlit as st
import pandas as pd
from utils.slot_extract import rule_based_extract, slot_info
from handlers.common_problems import add_chat, build_history
from utils.rag import rag_lookup
from utils.flow_manage import gen_prompt, generate_response

def generate_google_maps_link(destination_address):
    base_url = "https://www.google.com/maps/dir/?api=1"
    origin = "國立陽明交通大學"  # or use full English address if needed
    destination = destination_address.replace(" ", "+")
    return f"{base_url}&origin={origin}&destination={destination}&travelmode=transit"

def gen_propertyinfo(property_data) :
    """
    將租屋資訊轉成適合放入 prompt 的文字格式。
    只會包含 slot_info 設定為 show == "1" 的欄位。
    """
    visible_info = []
    for slot, meta in slot_info.items():
        if meta.get("show", "1") == "1":
            val = property_data.get(slot, "")
            if val and val != "無":
                visible_info.append(f"{slot}：{val}")
    
    if not visible_info:
        return ""
    
    return "\n".join(visible_info)

import re

import re

def risk_analysis(data):
    risks = []

    # === 租金、坪數風險 ===
    try:
        rent = int(data.get("租金", "0").replace(",", ""))
        size = float(data.get("坪數", "0"))
        if size > 0 and rent / size > 1500:
            risks.append("⚠️ 單位租金高於平均（>1500元/坪）")
        if size > 0 and rent / size < 800:
            risks.append("⚠️ 單位租金遠低於平均（<800元/坪），小心詐騙")
    except:
        rent = 0  # 順便給 rent 預設值，供押金用
        size = 0

    # === 押金風險（數值判斷）===
    try:
        deposit = int(data.get("押金", "0").replace(",", ""))
        if rent > 0 and deposit / rent > 2:
            risks.append("⚠️ 押金超過兩個月租金")
    except:
        pass

    # === 押金風險（文字判斷）===
    deposit_text = data.get("押金", "").strip()
    if re.search(r"(三個?月|3個?月|兩個半月|2\.5個?月)", deposit_text):
        risks.append("⚠️ 押金文字描述超過兩個月租金")
    elif re.search(r"(四|五|六|七|八|九|十)個?月", deposit_text):
        risks.append("⚠️ 押金文字描述過高，請特別留意")

    # === 資訊不足風險 ===
    valid_fields = sum(1 for k, v in data.items() if v.strip() and v != "無")
    if valid_fields < 5:
        risks.append("⚠️ 屋主提供資訊過少，建議審慎考慮")

    # === 必要欄位缺失風險 ===
    if data.get("地址", "").strip()=="無" or len(data.get("地址", "").strip())<4:
        risks.append("⚠️ 地址資訊缺少或不齊全，無法判斷地點風險")
    if data.get("租金", "").strip()=="無":
        risks.append("⚠️ 缺少租金資訊，無法評估價格合理性")
    if data.get("坪數", "").strip()=="無":
        risks.append("⚠️ 缺少坪數資訊，無法計算單位租金")

    return risks


def render_chat_interface():
    st.subheader("💬 與租屋小幫手對話")

    # Show chart if requested
    if "table_to_show" in st.session_state:
        df = st.session_state.table_to_show.copy()

    # 為每一筆資料加上風險評估欄位（合併為一行文字）
        if isinstance(df, pd.DataFrame):
            def summarize_risks(row):
                risks = risk_analysis(row.to_dict())
                return "\n".join(risks) if risks else "✅ 無明顯風險"

            df["風險評估"] = df.apply(summarize_risks, axis=1)

        # 轉置顯示，使每筆資料為一欄（變成長表格）
            df_transposed = df.transpose()

            st.markdown("📋 已儲存物件比較表（含風險）：")
            st.dataframe(df_transposed, use_container_width=True)

        st.session_state.pop("table_to_show")
    # Show extracted warnings
    current = st.session_state.get("current_data", {})
    if current:
        warnings = []
        for slot, val in current.items():
            if slot in st.session_state.ignored_slots:
                continue
            if not val or val.strip() == "" or val.strip() == "無":
                warnings.append(f"❗ **{slot}** 缺少，可能影響評估")
        if warnings:
            st.markdown("⚠️ 以下欄位可能不完整：\n\n" + "\n\n".join(warnings))

        risks = risk_analysis(current)
        if risks:
            st.markdown("🧠 系統風險評估：")
            for r in risks:
                st.markdown(r)
        address = st.session_state.current_data .get("地址")
        if address and address != "無":
            maps_url = generate_google_maps_link(address)
            st.markdown(f"🗺️ [查看通勤路線（Google 地圖）]({maps_url})", unsafe_allow_html=True)

    # LLM QA interface
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_text = st.chat_input("問我任何有關這筆租屋資訊的問題...")
    if user_text and user_text.strip():
        add_chat("user", user_text.strip())

        try:
            with st.spinner("思考中..."):
                # Do RAG retrieval
                context = rag_lookup(user_text, top_k=3, threshold=0.5)
                if not context:
                    context = ""

                # Generate prompt + response
                prompt = gen_prompt(user_text,history='', context=context+gen_propertyinfo(st.session_state.current_data))
                answer = generate_response(prompt)

            # Display answer
            add_chat("assistant", answer)

        except Exception as e:
            add_chat("assistant", f"⚠️ 發生錯誤：{str(e)}")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

def render_input_sidebar():
    st.header("📥 貼上租屋貼文")

    user_text = st.text_area("請貼上租屋貼文內容", height=150)

    if user_text:
        extracted = rule_based_extract(user_text)
            #st.write("Extracted Data:", extracted)

        st.session_state.current_data = extracted
        st.session_state.post_input = user_text
    else:
        st.warning("請先貼上貼文")

    if not st.session_state.get("current_data"):
        return
    with st.expander("📋 編輯租屋資訊（點擊展開）", expanded=False):
        edited_data = {}
        for slot in slot_info:
            val = st.session_state.current_data.get(slot, "無")
            if isinstance(val, dict):
                val = ", ".join([f"{k}: {v}" for k, v in val.items()])

            col1, col2 = st.columns([4, 1])
            with col1:
                edited_data[slot] = st.text_input(slot, value=val, key=f"edit_{slot}")
            with col2:
                ignore = st.checkbox("忽略", key=f"ignore_{slot}",
                                 value=(slot_info[slot].get("show", "1") == "0"))
                if ignore:
                    st.session_state.ignored_slots.add(slot)
                else:
                    st.session_state.ignored_slots.discard(slot)

        st.session_state.current_data = edited_data
    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💾 儲存"):
            if len(st.session_state.saved_listings) < 3:
                st.session_state.saved_listings.append(edited_data.copy())
                st.success("已儲存")
            else:
                st.warning("最多只能儲存 3 筆")

    with col2:
        if st.button("🗑️ 清除"):
            st.session_state.saved_listings = []
            st.success("已清除儲存物件")

    with col3:
            
        if st.button("📊 顯示表格"):
            visible_keys = [k for k, v in slot_info.items() if v.get("show", "1") == "1"]
            compare_data = [{k: item.get(k, "無") for k in visible_keys}
                            for item in st.session_state.saved_listings]
            df = pd.DataFrame(compare_data)
            st.session_state.table_to_show = df
   


def handle_post_analysis():
   
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


