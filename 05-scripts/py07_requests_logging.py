import requests
import logging
import time

# ========== logging 配置（写日志到文件）==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='api_call.log',  # 日志会写到这个文件里
    filemode='a'  # a=追加，不会覆盖之前的日志
)
logger = logging.getLogger(__name__)

# ========== 带重试的API调用函数 ==========
def call_api_with_retry(url, max_retries=3):
    """调用API，失败自动重试3次，每次等1秒"""
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"第{attempt}次尝试调用: {url}")
            
            # 发GET请求，超时5秒
            response = requests.get(url, timeout=5)
            
            # 检查HTTP状态码（200=成功，404=找不到，500=服务器崩了）
            response.raise_for_status()
            
            # 把返回的JSON转成Python字典
            data = response.json()
            logger.info(f"调用成功，状态码: {response.status_code}")
            return data
            
        except requests.exceptions.Timeout:
            logger.warning(f"第{attempt}次超时，1秒后重试...")
            time.sleep(1)
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP错误: {e}")
            time.sleep(1)
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            time.sleep(1)
    
    logger.error(f"重试{max_retries}次后仍然失败")
    return None

# ========== 主程序 ==========
if __name__ == "__main__":
    # 用"一言"免费API（不需要注册，返回一句随机文案）
    api_url = "https://v1.hitokoto.cn/"
    
    print("正在调用免费API...")
    result = call_api_with_retry(api_url)
    
    if result:
        print("\n=== API返回成功 ===")
        print(f"文案: {result.get('hitokoto', '无')}")
        print(f"来源: {result.get('from', '未知')}")
        logger.info(f"获取到文案: {result.get('hitokoto', '')}")
    else:
        print("API调用失败，请查看 api_call.log 日志文件")
    
    print("\n日志已写入 api_call.log，可以打开看看记录了什么")