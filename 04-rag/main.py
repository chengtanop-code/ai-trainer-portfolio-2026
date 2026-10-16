from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载.env里的Key
load_dotenv()

# 创建FastAPI应用
app = FastAPI(title="紧急铃后端", version="0.1")

# 初始化DeepSeek客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 定义请求体的数据结构（前端发来的JSON长这样）
class ChatRequest(BaseModel):
    question: str

# 定义响应体的数据结构（返回给前端的JSON长这样）
class ChatResponse(BaseModel):
    answer: str

# ========== 接口1：Hello World（测试用）==========
@app.get("/")
def read_root():
    return {"message": "紧急铃后端运行中"}

# ========== 接口2：POST /chat（收问题→调DeepSeek→返回回答）==========
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
        return ChatResponse(answer=answer)
    except Exception as e:
        return ChatResponse(answer=f"调用失败: {e}")