# jsonl_to_csv.py — 把电商客服 jsonl 转成 Label Studio 可导入的 CSV（提取客户提问）
# 入职应用：公司给的数据经常是各种格式（jsonl/json），第一步就是清洗成标注平台能吃的结构
import json
import csv
import random

SRC = r"E:\前端\data\E_commerce_Customer_Service\dev_clean_v2.jsonl"
DST = r"E:\前端\data\customer_messages_100.csv"
N = 100  # 抽样条数

rows = []
with open(SRC, encoding="utf-8") as f:
    for line in f:
        msgs = json.loads(line)["messages"]
        user_text = next((m["content"] for m in msgs if m["role"] == "user"), "")
        if user_text.strip():
            rows.append(user_text.strip())

random.seed(42)  # 固定种子，结果可复现
picked = random.sample(rows, min(N, len(rows)))

with open(DST, "w", newline="", encoding="utf-8-sig") as f:  # utf-8-sig 防Excel中文乱码
    w = csv.writer(f)
    w.writerow(["text"])  # Label Studio 按列名 text 识别待标注文本
    w.writerows([[t] for t in picked])

print(f"原始客户消息 {len(rows)} 条，抽样 {len(picked)} 条 -> {DST}")
