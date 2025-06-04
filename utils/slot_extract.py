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
slot_info = load_slot_info("data/slot.csv")
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
