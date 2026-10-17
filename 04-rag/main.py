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
class ClassifyRequest(BaseModel):
    message: str

class ClassifyResponse(BaseModel):
    level: str
    reason: str

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

# 接口4：POST /classify —— 判断消息紧急等级
@app.post("/classify", response_model=ClassifyResponse)
def classify(request: ClassifyRequest):
    # 系统提示词：把四级定义告诉AI
    system_prompt = """
你是一个旅拍工作室的消息分级助手。请根据下面的标准，判断客户消息的紧急等级。

【L4 紧急】定金/退单、当天或次日档期、到店联系不上、事故投诉、30分钟内连催3次且内容紧急
【L3 重要】具体日期咨询、合同付款、复购转介绍、限时客资、议价赠品
【L2 可延后】开场白、泛泛问价、要客片、售后小问题、闲聊
【L1 垃圾】贷款刷单发票、同行广告、@所有人、乱码

请先在心里分析，然后只输出两部分：
1. level：等级（L1/L2/L3/L4）
2. reason：一句话说明判断理由
"""
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ],
            temperature=0.0  # 分级要稳定，用0
        )
        result = response.choices[0].message.content

        # 简单解析：从回答里找出等级
        level = "L2"  # 默认
        for lv in ["L4", "L3", "L2", "L1"]:
            if lv in result:
                level = lv
                break

        return ClassifyResponse(level=level, reason=result)
    except Exception as e:
        return ClassifyResponse(level="L2", reason=f"判断失败: {e}")