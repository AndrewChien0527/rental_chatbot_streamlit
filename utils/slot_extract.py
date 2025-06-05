import csv
import re

def load_slot_info(csv_path):
    slot_info = {}
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            slot = row['slot']
            slot_info[slot] = {
                "regex": str(row['regex']),
                "advice": row['advice'],
                "consequence": row['consequence']
            }
    return slot_info

# Usage
slot_info = {
    "地址": {
        "regex": r"(地址|地點|位置)[:：]\s*([^\n\r]+)",
        "advice": "請補上詳細地址，例如「台北市大安區信義路三段123號」。",
        "consequence": "無法評估地段、比價、生活機能或治安風險。",
        "show": "1",
    },
    "格局": {
        "regex": r"(格局|房型|房間配置)[:：]\s*([^\n\r]+)",
        "advice": "請問格局為何？例如「2房1廳1衛」。",
        "consequence": "無法判斷空間是否符合需求與租金是否合理。",
        "show": "1",
    },
    "坪數": {
        "regex": r"(坪數|大小|面積)[:：]\s*([^\n\r]+)",
        "advice": "請提供坪數資訊，例如「20坪」。",
        "consequence": "無法計算單坪租金，也無法評估是否狹小或空間浪費。",
        "show": "1",
    },
    "樓層": {
        "regex": r"(樓層|樓層數|層數)[:：]\s*([^\n\r]+)",
        "advice": "請問所在樓層為何？例如「5樓/共12樓」。",
        "consequence": "無法評估通風、日照、噪音或逃生風險。",
        "show": "1",
    },
    "租金": {
        "regex": r"(租金|房租|租費)[:：]\s*([^\n\r]+)",
        "advice": "請提供租金金額，例如「25000元/月」。",
        "consequence": "無法進行性價比分析，也無法評估是否偏高。",
        "show": "1",
    },
    "租金含": {
        "regex": r"(租金含|租金包含|含租金)[:：]\s*([^\n\r]+)",
        "advice": "租金包含哪些項目？例如網路、水電、第四台等。",
        "consequence": "可能另有隱藏費用，影響實際支出。",
        "show": "1",
    },
    "管理費": {
        "regex": r"(管理費|管理費用|管理費用)[:：]\s*([^\n\r]+)",
        "advice": "請問管理費多少？或是否已包含在租金內？",
        "consequence": "忽略額外支出，導致誤判總成本。",
        "show": "1",
    },
    "帳單": {
        "regex": r"(水費|電費|帳單)[:：]\s*([^\n\r]+)",
        "advice": "水電費怎麼算？依帳單、均分還是定額？",
        "consequence": "可能產生爭議或額外負擔。",
        "show": "1",
    },
    "機車位": {
        "regex": r"(機車位|機車停車位|機車車位)[:：]\s*([^\n\r]+)",
        "advice": "有機車停車位嗎？是免費還需額外付費？",
        "consequence": "對通勤族不便或額外開銷。",
        "show": "1",
    },
    "汽車位": {
        "regex": r"(汽車位|汽車停車位|汽車車位)[:：]\s*([^\n\r]+)",
        "advice": "有汽車車位嗎？若有是怎麼計費的？",
        "consequence": "開車族無法評估是否適合長期停放。",
        "show": "0",
    },
    "電梯": {
        "regex": r"(電梯|有無電梯|是否有電梯)[:：]\s*([^\n\r]+)",
        "advice": "大樓有電梯嗎？",
        "consequence": "無電梯對高樓層者不便，也影響搬家與緊急狀況。",
        "show": "0",
    },
    "寵物": {
        "regex": r"(寵物|養寵物|可養寵物)[:：]\s*([^\n\r]+)",
        "advice": "是否可養寵物？例如「可養貓狗」、「不可養寵物」。",
        "consequence": "飼主未確認可能導致違約或被趕出。",
        "show": "1",
    },
    "禁菸": {
        "regex": r"(禁菸|禁煙|是否禁菸)[:：]?\s*([^\n\r]+)?",
        "advice": "是否禁菸？",
        "consequence": "吸菸者未問明可能違反規定，非吸菸者可能擔憂空氣品質。",
        "show": "1",
    },
    "建案": {
        "regex": r"(建案|社區|建案名稱)[:：]\s*([^\n\r]+)",
        "advice": "請問建案名稱為何？若是社區型大樓更需要此資訊。",
        "consequence": "無法進一步查詢管理品質、社區評價。",
        "show": "0",
    },
    "類型": {
        "regex": r"(類型|房屋類型|型態)[:：]\s*([^\n\r]+)",
        "advice": "房屋類型是套房、雅房、整層住家，還是其他？",
        "consequence": "無法判斷隱私程度與空間分配是否適合。",
        "show": "1",
    },
    "飲水機": {
        "regex": r"(飲水機|提供飲水機)[:：]\s*([^\n\r]+)",
        "advice": "是否提供飲水機？",
        "consequence": "無法得知是否需自備飲水設備，可能影響日常生活便利性與成本。",
        "show": "1",
    },
    "曬衣空間": {
        "regex": r"(曬衣空間|晾衣空間|曬衣場)[:：]\s*([^\n\r]+)",
        "advice": "是否提供曬衣空間？",
        "consequence": "無法判斷衣物乾燥方式，恐需另尋曬衣替代方案，影響居住實用性。",
        "show": "0",
    },
    "頂樓加蓋": {
        "regex": r"(頂樓加蓋|頂樓加蓋物|頂樓加蓋狀況)[:：]\s*([^\n\r]+)",
        "advice": "是否為頂樓加蓋？",
        "consequence": "無法掌握結構安全與夏季溫度問題，影響居住舒適與安全性。",
        "show": "1",
    },
    "垃圾處理": {
        "regex": r"(垃圾處理|垃圾回收|垃圾處理方式)[:：]\s*([^\n\r]+)",
        "advice": "如何處理垃圾回收？例如：子母車、代收、自行處理等。",
        "consequence": "無法掌握垃圾處理機制，可能增加生活困擾。",
        "show": "1",
    },
    "對外窗": {
        "regex": r"(對外窗|窗戶|外窗)[:：]\s*([^\n\r]+)",
        "advice": "是否有對外窗？",
        "consequence": "無窗或採光不足會影響通風與心情，可能導致發霉或潮濕問題。",
        "show": "1",
    },
    "廚房": {
        "regex": r"(廚房|烹飪區|廚房設備)[:：]\s*([^\n\r]+)",
        "advice": "有無廚房？是否可開火或使用電磁爐？",
        "consequence": "無廚房或禁火限制恐影響日常飲食安排。1",
        "show": "",
    },
    "設籍報稅": {
        "regex": r"(設籍|報稅|設籍報稅)[:：]\s*([^\n\r]+)",
        "advice": "是否可報稅設籍？是否為合法建物？",
        "consequence": "無法報稅或設籍會影響補助、學區、居留等權益，也可能涉違建。",
        "show": "1",
    },
    "家具": {
        "regex": r"(家具|傢俱|家具設備)[:：]\s*([^\n\r]+)",
        "advice": "是否有基本家具？例如床、衣櫃、書桌等",
        "consequence": "缺乏家具需自備，會增加初期搬遷成本與不便。",
        "show": "1",
    },
    "租期條件": {
        "regex": r"(租期條件|租約條件|租期)[:：]\s*([^\n\r]+)",
        "advice": "最短租期與提前解約條件為何？",
        "consequence": "無法彈性調整生活規劃，亦可能面臨解約違約金。",
        "show": "1",
    },
    "安全設備": {
        "regex": r"(安全設備|消防設備|安全裝置)[:：]\s*([^\n\r]+)",
        "advice": "是否有火災警報器、滅火器或緊急逃生通道？",
        "consequence": "安全設備不明，發生災害時風險上升。",
        "show": "0",
    },
    "網路": {
        "regex": r"(網路|網路速度|網路提供)[:：]\s*([^\n\r]+)",
        "advice": "網路速度與提供方式？為共用或獨立？",
        "consequence": "共用網路可能不穩定，影響工作與生活品質。",
        "show": "0",
    },
}
patterns = {slot: info["regex"] for slot, info in slot_info.items()}

# Define required slots
required_slots = list(slot_info.keys())
def rule_based_extract(text,patterns=patterns):
    result = {}
    for slot, pattern in patterns.items():
        if not isinstance(pattern,str):
            continue
        match = re.search(pattern, text)
        if match:
            if match.groupdict():
                result[slot] = {k: v for k, v in match.groupdict().items() if v}
            elif match.lastindex:
                result[slot] = match.group(match.lastindex).strip()
            else:
                result[slot] = True
        else:
            result[slot] = "無"
    return result
def handle_rental_post(text):
    found = rule_based_extract(text)

    # Construct human-friendly summary
    filled = [f"✅ {k}：{v}" for k, v in found.items() if v != "無"]
    consequence=[
        f"缺少「{slot}」 影響：{slot_info[slot]['consequence']}"
        for slot in found if found[slot] == "無"
    ]
    advice = [
        f"⚠️ 缺少「{slot}」\n👉 建議：{slot_info[slot]['advice']}\n"
        for slot in found if found[slot] == "無"
    ]
    consequence='\n'.join(consequence)
    #consequence=generate_response("請整合以下建議:"+consequence)
    advice='\n'.join(advice)

    return {
        "parsed_info": found,
        "advice":advice,
        "consequence": consequence
    }
