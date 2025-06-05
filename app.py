import streamlit as st
from handlers.post_analysis import handle_post_analysis
from handlers.contract_checklist import handle_contract_checklist
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

# 
first_rent_intro_message='''找房建議注意：交通、租金行情、房東身分、合約條款、押金規則，以及環境安全
🔍 一、房東與房屋的合法性
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

若對租約條款不確定，可委託律師或向當地法律扶助基金會諮詢。'''
tax_intro_msg = '''
一、常見的租屋補助方案
| 補助名稱                | 適用對象         | 金額                       | 申請條件                       |
| ------------------- | ------------ | ------------------------ | -------------------------- |
| **租金補貼**            | 弱勢族群、青年、家庭   | 每月最高 8,000 元（依縣市與家戶人數分級） | 有租賃契約、有報稅、有設籍，且家庭收入在一定標準以下 |
| **包租代管補助**          | 房東、房客均可申請    | 房客每月補助租金、房東享稅賦優惠         | 須透過政府認可之代管業者簽訂契約           |
| **青年租屋補助**          | 年輕族群（20～40歲） | 北北基最多每月 5,000 元          | 須有正式租約、家庭所得限制              |
| **中低收入戶、身心障礙者租屋補助** | 特殊身份         | 補助額度較高                   | 須有設籍與身份證明                  |


二、租金報稅與相關稅務規範
對房客（你）來說：
✅ 你可以報稅節稅（列舉扣除額）

條件：有「正式租賃契約」與「房東報稅或開立收據」。

可在綜合所得稅報稅時申報 租金支出，每年最多可抵稅 12 萬元（即每月 10,000 元內）。

⚠️ 若房東未報稅，你報稅將可能導致房東被查稅

建議與房東溝通是否願意開立「租金收據」並報稅。

二、租金報稅與相關稅務規範
對房客（你）來說：
✅ 你可以報稅節稅（列舉扣除額）

條件：有「正式租賃契約」與「房東報稅或開立收據」。

可在綜合所得稅報稅時申報 租金支出，每年最多可抵稅 12 萬元（即每月 10,000 元內）。

⚠️ 若房東未報稅，你報稅將可能導致房東被查稅

建議與房東溝通是否願意開立「租金收據」並報稅。

三、免費法律資源（協助租屋糾紛）
🧑‍⚖️ 法律諮詢與協助管道：
| 資源單位                  | 提供內容             | 聯絡方式                                     |
| --------------------- | ---------------- | ---------------------------------------- |
| **法律扶助基金會**           | 免費法律諮詢、必要時提供律師協助 | [www.laf.org.tw](https://www.laf.org.tw) |
| **各縣市政府法扶窗口**         | 定期開放法律諮詢時段       | 可電話或網路預約                                 |
| **司法院法律諮詢網站**         | 基本法律問題線上諮詢       | [law.moj.gov.tw](https://law.moj.gov.tw) |
| **社區法律諮詢（民意代表、社區中心）** | 通常不定期辦理，免費       | 可留意當地公告                                  |


'''
topics = {
    "幫我評估房屋資訊": handle_post_analysis,
    "找房子要注意什麼？": handle_common_problem(first_rent_intro_message),
    "租約簽訂前怎麼檢查？": handle_contract_checklist,
    "想了解補助、報稅、或法律資源": handle_common_problem(tax_intro_msg),
    "遇到問題怎麼處理？（水電、室友、房東等）": handle_common_problem}


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
