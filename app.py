import streamlit as st
from handlers.post_analysis import handle_post_analysis
from handlers.landlord_negotiation import handle_landlord_negotiation
from handlers.contract_checklist import handle_contract_checklist
from handlers.tax_and_subsidy import handle_tax_and_subsidy
from handlers.common_problems import handle_common_problem

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
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 按鈕列表與對應回覆
topics = {
    "1️⃣ 幫我判斷貼文內容 / 聊天紀錄": handle_post_analysis,
    "2️⃣ 教我如何應對房東的要求": handle_landlord_negotiation,
    "3️⃣ 找房子要注意什麼？": lambda: add_chat("assistant", '''找房建議注意：交通、租金行情、房東身分、合約條款、押金規則，以及環境安全。🔍 一、房東與房屋的合法性
確認房東身分是否為房屋所有人
可要求房東出示「房屋權狀」或「最近一期的房屋稅單」，確認他是否為登記所有人。

是否為合法用途的住宅
查詢「使用分區」是否允許當住宅使用。有些辦公大樓、工業用地不能作為住宅出租。

違建或分租套房要特別小心
違建可能隨時被拆除，居住安全堪慮；分租套房若無消防設施，也有重大安全疑慮。

📝 二、租約內容要清楚
一定要簽訂書面契約
書面契約是保障雙方權益的基礎，建議使用內政部提供的【定型化契約範本】。

明確列出租金、押金、租期、水電費、管理費等費用計算方式

是否可以提前解約？違約金怎麼計算？
有些房東會要求提前解約需付違約金，一定要在契約內寫清楚條件與金額。

押金最多不得超過兩個月租金（依《民法》第450條）

🏠 三、入住前實地檢查
檢查水電管線、冷氣熱水器是否正常
發現問題要拍照或錄影存證，並在契約中註明由誰負責修繕。

清點與紀錄家具家電的現況
可列出清單並附在租約後方（作為附件）。

⚠️ 四、注意房東違法行為
強制收看電視、限制用水用電、限制訪客進出等行為，可能違反《住宅法》或《民法》。

房東若無你同意就進屋，涉嫌侵犯隱私或違法侵入住居。

📌 小技巧與建議
多看幾間房子再決定，避免衝動租房。

保留租屋對話紀錄（LINE、email、簡訊），日後如發生爭議有憑有據。

若對租約條款不確定，可委託律師或向當地法律扶助基金會諮詢。'''),
    "4️⃣ 租約簽訂前怎麼檢查？": handle_contract_checklist,
    "5️⃣ 想了解補助、報稅、或法律資源": handle_tax_and_subsidy,
    "6️⃣ 遇到問題怎麼處理？（水電、室友等）": handle_common_problem}



# 顯示按鈕並處理點擊
def handle_topic_flow(label):
    if label == "1️⃣ 幫我判斷貼文內容 / 聊天紀錄":
        return handle_post_analysis()
    elif label == "2️⃣ 教我如何應對房東的要求":
        return handle_landlord_negotiation()
    elif label == "3️⃣ 找房子要注意什麼？":
        return '''找房建議注意：交通、租金行情、房東身分、合約條款、押金規則，以及環境安全。🔍 一、房東與房屋的合法性
確認房東身分是否為房屋所有人
可要求房東出示「房屋權狀」或「最近一期的房屋稅單」，確認他是否為登記所有人。

是否為合法用途的住宅
查詢「使用分區」是否允許當住宅使用。有些辦公大樓、工業用地不能作為住宅出租。

違建或分租套房要特別小心
違建可能隨時被拆除，居住安全堪慮；分租套房若無消防設施，也有重大安全疑慮。

📝 二、租約內容要清楚
一定要簽訂書面契約
書面契約是保障雙方權益的基礎，建議使用內政部提供的【定型化契約範本】。

明確列出租金、押金、租期、水電費、管理費等費用計算方式

是否可以提前解約？違約金怎麼計算？
有些房東會要求提前解約需付違約金，一定要在契約內寫清楚條件與金額。

押金最多不得超過兩個月租金（依《民法》第450條）

🏠 三、入住前實地檢查
檢查水電管線、冷氣熱水器是否正常
發現問題要拍照或錄影存證，並在契約中註明由誰負責修繕。

清點與紀錄家具家電的現況
可列出清單並附在租約後方（作為附件）。

⚠️ 四、注意房東違法行為
強制收看電視、限制用水用電、限制訪客進出等行為，可能違反《住宅法》或《民法》。

房東若無你同意就進屋，涉嫌侵犯隱私或違法侵入住居。

📌 小技巧與建議
多看幾間房子再決定，避免衝動租房。

保留租屋對話紀錄（LINE、email、簡訊），日後如發生爭議有憑有據。

若對租約條款不確定，可委託律師或向當地法律扶助基金會諮詢。'''  # static reply
    elif label == "4️⃣ 租約簽訂前怎麼檢查？":
        return handle_contract_checklist()
    elif label == "5️⃣ 想了解補助、報稅、或法律資源":
        return handle_tax_and_subsidy()
    elif label == "6️⃣ 遇到問題怎麼處理？（水電、室友等）":
        return handle_common_problem()
    else:
        return "請選擇一個有效的主題。"

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
