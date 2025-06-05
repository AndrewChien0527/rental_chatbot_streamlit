import csv


csv_data = """slot,regex,regex_complex,advice,consequence,show
地址,(地址|地點|位置)[:：]\\s*([^\\n\\r]+),(地址|地點)：?([\\u4e00-\\u9fa5a-zA-Z0-9]+市[\\u4e00-\\u9fa5a-zA-Z0-9]+路),請補上詳細地址，例如「台北市大安區信義路三段123號」。,無法評估地段、比價、生活機能或治安風險。,1
格局,(格局|房型|房間配置)[:：]\\s*([^\\n\\r]+),格局：?(\\d+房)?/?(\\d+廳)?/?(\\d+衛)?/?(\\d+陽台)?,請問格局為何？例如「2房1廳1衛」。,無法判斷空間是否符合需求與租金是否合理。,1
坪數,(坪數|大小|面積)[:：]\\s*([^\\n\\r]+),(室內)?坪數[:：]?[^\d]*(\\d+\\.?\\d*)坪,請提供坪數資訊，例如「20坪」。,無法計算單坪租金，也無法評估是否狹小或空間浪費。,1
"""  # Add the full CSV content here

# Parse the CSV
slot_info = {}
with open("data/slot.csv", encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
          
        slot_info[row['slot']] = {
        "regex": row['regex'],
        "advice": row['advice'],
        "consequence": row['consequence'],
        "show": row['show']
    }

# Print Python hardcoded dictionary
print("slot_info = {")
for key, value in slot_info.items():
    print(f'    "{key}": {{')
    for k, v in value.items():
        print(f'        "{k}": r"{v}",' if k == "regex" else f'        "{k}": "{v}",')
    print("    },")
print("}")
