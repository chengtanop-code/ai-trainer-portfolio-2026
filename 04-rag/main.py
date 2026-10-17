from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from openai import OpenAI
import db  # 导入我们昨天写的数据库模块

load_dotenv()

app = FastAPI(title="紧急铃后端", version="0.1")

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

# 程序启动时，自动建表（表已存在也不会报错）
db.init_db()

# 接口1：Hello World
@app.get("/")
def read_root():
    return {"message": "紧急铃后端运行中"}

# 接口2：POST /chat —— 问答并存入数据库
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个简洁有用的助手"},
                {"role": "user", "content": request.question}
            ],
            temperature=0.7
        )
        answer = response.choices[0].message.content
        # 把这轮问答存进数据库
        db.insert_message(request.question, answer)
        return ChatResponse(answer=answer)
    except Exception as e:
        return ChatResponse(answer=f"调用失败: {e}")

# 接口3：GET /history —— 查最近10条问答
@app.get("/history")
def history():
    return {"messages": db.get_recent_messages(10)}