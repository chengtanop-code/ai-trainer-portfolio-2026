import sqlite3
from datetime import datetime

DB_NAME = "ai.db"

def get_conn():
    """获取数据库连接，每次操作完要close"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # 让查询结果能按列名取
    return conn

def init_db():
    """建表（如果不存在）"""
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("建表成功")

def insert_message(question, answer):
    """插入一条问答记录"""
    conn = get_conn()
    conn.execute(
        "INSERT INTO messages (question, answer, created_at) VALUES (?, ?, ?)",
        (question, answer, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

def get_recent_messages(limit=10):
    """查最近N条记录"""
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM messages ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# 直接运行测试
if __name__ == "__main__":
    init_db()
    insert_message("测试问题", "测试回答")
    print("当前记录：", get_recent_messages())