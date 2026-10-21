# sql_practice.py
# SQL四大基本功：SELECT / WHERE / GROUP BY / JOIN
# 自包含练习库，运行一次对照输出即可，不影响你的 ai.db
import sqlite3

conn = sqlite3.connect("sql_demo.db")
cur = conn.cursor()

# 建两张表：客户表 + 消息表
cur.execute("DROP TABLE IF EXISTS customers")
cur.execute("DROP TABLE IF EXISTS messages")
cur.execute("""
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    level TEXT,     -- 客户等级 VIP/普通
    paid INTEGER    -- 是否已付定金 1/0
)
""")
cur.execute("""
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,   -- 关联到 customers.id（外键）
    text TEXT,
    created_at TEXT
)
""")

cur.executemany("INSERT INTO customers VALUES (?,?,?,?)", [
    (1, "李小姐", "VIP", 1),
    (2, "王先生", "普通", 0),
    (3, "张阿姨", "普通", 1),
])
cur.executemany("INSERT INTO messages VALUES (?,?,?,?)", [
    (1, 1, "明天能提前开门吗", "2026-10-18 08:00"),
    (2, 1, "定金转了", "2026-10-18 08:05"),
    (3, 2, "多少钱", "2026-10-18 09:00"),
    (4, 3, "想改期", "2026-10-18 10:00"),
])
conn.commit()

print("==== 1. SELECT：决定要哪些列 ====")
cur.execute("SELECT * FROM customers")
print("所有列：", cur.fetchall())
cur.execute("SELECT name, level FROM customers")
print("只要名字和等级：", cur.fetchall())

print("\n==== 2. WHERE：决定要哪些行（过滤） ====")
cur.execute("SELECT name FROM customers WHERE paid = 1")
print("已付定金的客户：", cur.fetchall())
cur.execute("SELECT text FROM messages WHERE text LIKE '%钱%'")
print("内容含'钱'的消息：", cur.fetchall())

print("\n==== 3. GROUP BY：把同类归堆，再统计 ====")
cur.execute("SELECT level, COUNT(*) FROM customers GROUP BY level")
print("各客户等级人数：", cur.fetchall())
cur.execute("SELECT customer_id, COUNT(*) FROM messages GROUP BY customer_id")
print("每个客户发了几条消息：", cur.fetchall())

print("\n==== 4. JOIN：两张表靠共同字段拼成一张 ====")
cur.execute("""
SELECT customers.name, messages.text
FROM messages
JOIN customers ON messages.customer_id = customers.id
""")
print("客户名 + 他发的消息：")
for row in cur.fetchall():
    print("  ", row)

conn.close()
print("\n练完 sql_demo.db 可删。接下来把同样四招用到你的 ai.db。")
