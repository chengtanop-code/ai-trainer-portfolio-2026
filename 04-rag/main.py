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
你是旅拍工作室的消息分级助手，根据标准判断客户消息的紧急等级。

【L4 紧急】数小时内不回复会直接丢钱/违约/出事故：
- 已付定金/尾款，且伴随当天或次日改期、退款退单
- 客户已到店但联系不上、拍摄日当天天气/设备事故
- 拍摄日当天或次日客户临时提前到达、要求提前开门/化妆（如"航班提前了，早上7点到，能提前开门吗"）
- 投诉升级（差评/曝光/12315）
- 连续重复催促（如"在吗在吗在吗？？？"、短时间内连发多条、带明显情绪）

【L3 重要】成交推进中的订单（2-4小时内处理）：
- 给具体日期问档期、要合同、对比套餐、确认套餐
- 问"怎么预约""定金怎么付"（这是询问付款方式，不是已付款）
- 朋友推荐/转介绍、老客复购、平台限时客资
- 选好照片发编号/发邮箱、拍摄前确认集合地点/带什么衣服

【L2 可延后】常规咨询、未明确意向：
- "在吗""多少钱""发点客片""地址在哪"
- 群求赞、朋友闲聊、节日祝福

【L1 垃圾】营销广告、刷单、代开发票、同行批发、群@所有人、模板通知

【关键区分，务必遵守】
- "定金怎么付/怎么交"（还没付，只是询问）=L3；只要客户说"刚转了定金/已付定金/定金发你了"，不管是"你收一下、锁档期"还是"改期/退款/事故"，都=L4（钱已实际到账，必须立刻核实收款或锁定，避免重复卖给别人）
- "明天确认带什么/集合地点"（没有时间变更）是常规确认=L3；"明天临时提前到达、要求提前开门/改期/事故/到店联系不上"才L4
- 求赞/点赞是L2，不是L1
- 不要只看到"定金/明天/紧急"就判L4，要先分清是"询问/确认"还是"已发生事故"

请只输出两部分：1. level（L1/L2/L3/L4） 2. reason（一句话理由）
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