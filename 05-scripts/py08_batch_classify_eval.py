# py08_batch_classify_eval.py
# 批量测试分级接口：30条消息 -> 对比期望级别 -> 统计准确率/L4召回 -> 输出badcase
# 用法：先确保 uvicorn 已在 04-rag 目录跑起来（http://localhost:8000），再运行本脚本
import requests

# 测试集：(消息, 期望级别)
TEST_CASES = [
    ("老板在吗？我是明天拍婚纱照的李小姐，航班提前了早上7点能到，能提前开门化妆吗？", "L4"),
    ("刚转了2000定金你收一下，档期给我锁5月2号别给别人了", "L4"),
    ("今天雨太大外景拍不了怎么办？能不能改期或者换室内？", "L4"),
    ("我到你们店门口了，门锁着没人，电话也打不通", "L4"),
    ("孩子突然发烧，今天下午亲子照来不了，定金能退吗？", "L4"),
    ("修了20天图还没给我？今天再不发我就退款加小红书曝光", "L4"),
    ("紧急！摄影棚灯光烧了一组，下午三点的客户怎么办？", "L4"),
    ("在吗在吗在吗？？？", "L4"),
    ("想问下10月3号还有档期吗？两个人拍情侣照", "L3"),
    ("套餐999和1299差在哪？能发下合同模板看看吗", "L3"),
    ("朋友推荐来的，她说你拍得好，怎么预约？", "L3"),
    ("那行就定你们家了，定金怎么付？", "L3"),
    ("美团上咨询的麻烦尽快回，平台说30分钟内回复有流量加权", "L3"),
    ("上次全家福很满意，爸妈金婚想再约一组，下周六方便吗", "L3"),
    ("照片选好了36张，编号发你邮箱了，查收一下", "L3"),
    ("明天拍摄要自己带什么衣服？再确认下集合地点", "L3"),
    ("在吗", "L2"),
    ("你们家拍照多少钱啊", "L2"),
    ("能发点客片看看吗", "L2"),
    ("你们店具体位置在哪呀", "L2"),
    ("宝宝百天照什么时候拍比较好？我先了解下", "L2"),
    ("哈哈哈这个表情包笑死我了", "L2"),
    ("周末有空一起吃饭不", "L2"),
    ("麻烦帮我朋友圈第一条点个赞谢谢", "L2"),
    ("【贷款】您有50万预授信额度待领取，点击链接", "L1"),
    ("诚招兼职刷单，日结300+", "L1"),
    ("@所有人 本周摄影行业直播课今晚8点开课", "L1"),
    ("需要发票代开请联系微信", "L1"),
    ("您的快递已放驿站", "L1"),
    ("新店开业礼服批发工厂直供欢迎同行合作", "L1"),
]

URL = "http://localhost:8000/classify"


def classify_one(message):
    """调一次分级接口，返回模型判的级别"""
    resp = requests.post(URL, json={"message": message}, timeout=30)
    return resp.json()["level"]


def main():
    results = []
    correct = 0
    l4_total = 0
    l4_caught = 0

    for idx, (msg, expected) in enumerate(TEST_CASES, start=1):
        try:
            pred = classify_one(msg)
        except Exception as e:
            pred = "ERROR"
            print(f"第{idx}条请求失败：{e}")

        ok = (pred == expected)
        if ok:
            correct += 1
        if expected == "L4":
            l4_total += 1
            if pred == "L4":
                l4_caught += 1

        results.append((idx, expected, pred, ok, msg))
        print(f"[{idx:>2}] 期望{expected} 预测{pred} {'对' if ok else '错 <-- badcase'}")

    total = len(TEST_CASES)
    print("\n========== 分级测试报告 ==========")
    print(f"总数：{total}  正确：{correct}")
    print(f"整体准确率：{correct/total*100:.1f}%   （目标≥85%）")
    l4_rate = l4_caught / l4_total * 100 if l4_total else 0
    print(f"L4召回率：{l4_caught}/{l4_total} = {l4_rate:.1f}%   （目标100%）")

    # 分级统计：模型把每个级别判成了什么
    print("\n--- 各级别判对情况 ---")
    for lv in ["L4", "L3", "L2", "L1"]:
        rows = [r for r in results if r[1] == lv]
        hit = sum(1 for r in rows if r[3])
        print(f"{lv}：{hit}/{len(rows)} 判对")

    print("\n--- 误判 badcase 明细 ---")
    bad = [r for r in results if not r[3]]
    if not bad:
        print("全部判对，无 badcase！")
    for idx, expected, pred, ok, msg in bad:
        print(f"#{idx} 期望{expected} 实际{pred}：{msg[:25]}")

    print("\n提示：把以上 badcase 和准确率记进《分级测试报告》，面试时就是硬数据。")


if __name__ == "__main__":
    main()
#（注：内容由AI生成）
