import sqlite3
conn = sqlite3.connect("E:/前端/ai-trainer-portfolio-2026/04-rag/ai.db")
cur = conn.cursor()

# 1. 总共有多少条问答
cur.execute("SELECT COUNT(*) FROM messages")
print("问答总数：", cur.fetchone()[0])

# 2. 查最近5条问题
cur.execute("SELECT id, question FROM messages ORDER BY id DESC LIMIT 5")
print("最近5条：", cur.fetchall())

# 3. 按id查某一条
cur.execute("SELECT question, answer FROM messages WHERE id = 1")
print("第1条：", cur.fetchone())

conn.close()