import os
from dotenv import load_dotenv
from openai import OpenAI

# 读取 .env 里的 Key
load_dotenv()
print("调试：Key =", os.getenv("DEEPSEEK_API_KEY"))
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"  # DeepSeek兼容OpenAI接口
)

def ask_llm(question):
    """调用DeepSeek大模型，传入问题，返回回答"""
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个简洁有用的助手"},
                {"role": "user", "content": question}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"调用出错: {e}"

# 直接运行这个文件时测试一下
if __name__ == "__main__":
    answer = ask_llm("你好，请用一句话介绍你自己")
    print(answer)