import streamlit as st
from utils.slot_extract import rule_based_extract,slot_info
import streamlit as st
from utils.slot_extract import rule_based_extract, slot_info
import urllib.parse

import pandas as pd

def add_chat(role, content):
    with st.chat_message(role):
        st.markdown(content)
    st.session_state.messages.append({"role": role, "content": content})

def generate_google_maps_link(destination_address):
    base_url = "https://www.google.com/maps/dir/?api=1"
    origin = "國立陽明交通大學"  # or use full English address if needed
    destination = destination_address.replace(" ", "+")
    return f"{base_url}&origin={origin}&destination={destination}&travelmode=transit"




def handle_post_analysis():
    #add_chat("assistant", "請貼上你看到的租屋貼文或與房東/仲介的對話，我可以幫你分析是否有風險或違法。")

    if "post_input" not in st.session_state:
        st.session_state.post_input = ""

    if "ignored_slots" not in st.session_state:
        st.session_state.ignored_slots = set()

    user_text = st.chat_input("請貼上租屋資訊後按 Enter")

    if user_text:
        st.session_state.post_input = user_text
        add_chat("user", user_text)

    if st.session_state.post_input:
        post_text = st.session_state.post_input
        extracted = rule_based_extract(post_text)

        # --- Sidebar: Form ---
        with st.sidebar:
            st.header("📋 表單欄位（可編輯）")
            edited_data = {}
            for slot in slot_info.keys():
                default_val = extracted.get(slot, "無")
                if isinstance(default_val, dict):
                    default_val = ", ".join([f"{k}: {v}" for k, v in default_val.items()])
                col1, col2 = st.columns([4, 1])
                with col1:
                    edited_data[slot] = st.text_input(f"{slot}", value=default_val, key=f"slot_{slot}")
                with col2:
                    default_show = slot_info[slot].get("show", "1")
                    ignore = st.checkbox("忽略", key=f"ignore_{slot}", value=(default_show == "0"))

                    #ignore = st.checkbox("忽略", key=f"ignore_{slot}")
                    if ignore:
                        st.session_state.ignored_slots.add(slot)
                    else:
                        st.session_state.ignored_slots.discard(slot)

        # --- Main Chat: Feedback Analysis ---
        warnings = []
        for slot, value in edited_data.items():
            if slot in st.session_state.ignored_slots:
                continue
            address = edited_data.get("地址")  # depends on your slot name
            if address and address != "無":
                maps_url = generate_google_maps_link(address)
                st.markdown(f"🗺️ [查看通勤路線（Google 地圖）]({maps_url})", unsafe_allow_html=True)

            if not value or value.strip() == "" or value.strip() == "無":
                warnings.append(
                    f"- **{slot}**：{slot_info[slot]['consequence']}\n\n 建議：{slot_info[slot]['advice']}"
                )

        if warnings:
            with st.chat_message("assistant"):
                st.markdown("⚠️ 以下欄位可能有缺漏，建議補充：\n\n" + "\n\n".join(warnings))
        else:
            add_chat("assistant", "✅ 表單欄位完整，未發現明顯風險。")


def handle_post_analysis():
    if "post_input" not in st.session_state:
        st.session_state.post_input = ""

    if "ignored_slots" not in st.session_state:
        st.session_state.ignored_slots = set()

    if "saved_listings" not in st.session_state:
        st.session_state.saved_listings = []

    user_text = st.chat_input("請貼上租屋資訊後按 Enter")

    if user_text:
        st.session_state.post_input = user_text
        add_chat("user", user_text)

    if st.session_state.post_input:
        post_text = st.session_state.post_input
        extracted = rule_based_extract(post_text)

        # --- Sidebar: Form ---
        with st.sidebar:
            st.header("📋 表單欄位（可編輯）")
            edited_data = {}
            for slot in slot_info.keys():
                default_val = extracted.get(slot, "無")
                if isinstance(default_val, dict):
                    default_val = ", ".join([f"{k}: {v}" for k, v in default_val.items()])
                col1, col2 = st.columns([4, 1])
                with col1:
                    edited_data[slot] = st.text_input(f"{slot}", value=default_val, key=f"slot_{slot}")
                with col2:
                    default_show = slot_info[slot].get("show", "1")
                    ignore = st.checkbox("忽略", key=f"ignore_{slot}", value=(default_show == "0"))
                    if ignore:
                        st.session_state.ignored_slots.add(slot)
                    else:
                        st.session_state.ignored_slots.discard(slot)

        # --- Google Maps Link (if address exists) ---
        address = edited_data.get("地址")
        if address and address != "無":
            maps_url = generate_google_maps_link(address)
            st.markdown(f"🗺️ [查看通勤路線（Google 地圖）]({maps_url})", unsafe_allow_html=True)

        # --- Save Listing ---
        if st.button("💾 儲存此物件（最多3筆）"):
            if len(st.session_state.saved_listings) < 3:
                st.session_state.saved_listings.append(edited_data.copy())
                st.success(f"已儲存，目前共 {len(st.session_state.saved_listings)} 筆。")
            else:
                st.warning("已達最多 3 筆儲存限制，請先清除部分物件。")

        if st.session_state.saved_listings:
            st.markdown("### 📌 已儲存物件")
            for i, listing in enumerate(st.session_state.saved_listings):
                summary = listing.get("地址", "無地址") + " | " + listing.get("租金", "無租金")
                st.markdown(f"**{i+1}. {summary}**")
            if st.button("🗑️ 清除所有儲存物件"):
                st.session_state.saved_listings = []
                st.success("已清除所有儲存物件")

        # --- Main Chat: Feedback Analysis ---
        warnings = []
        for slot, value in edited_data.items():
            if slot in st.session_state.ignored_slots:
                continue
            if not value or value.strip() == "" or value.strip() == "無":
                warnings.append(
                    f"- **{slot}**：{slot_info[slot]['consequence']}\n"#\n 建議：{slot_info[slot]['advice']}"
                )

        if warnings:
            with st.chat_message("assistant"):
                st.markdown("⚠️ 以下欄位可能有缺漏，建議補充：\n\n" + "\n\n".join(warnings))
        else:
            add_chat("assistant", "✅ 表單欄位完整，未發現明顯風險。")