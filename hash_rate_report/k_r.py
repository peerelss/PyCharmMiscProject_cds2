import socket
import json
import concurrent.futures
import schedule
import ob_monitor
import utils.utils_k
import pymongo
import time
from datetime import datetime
# MongoDB 配置
client = pymongo.MongoClient("mongodb://localhost:27017/")  # 连接到本地 MongoDB
db = client["mining_data"]  # 数据库名称
collection = db["hash_rates"]  # 集合名称


def cgminer_summary(ip, timeout=1.0):
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((ip, 4028))

        payload = json.dumps({"command": "summary"}).encode()
        s.send(payload)

        raw = s.recv(4096)
        s.close()

        text = raw.decode("utf-8", errors="ignore")

        # 1) 按 NULL 分割（CGMiner 常用）
        text = text.split("\x00")[0]

        # 2) 如果多个 JSON 拼接，取第一个
        if "}{" in text:
            text = text.split("}{")[0] + "}"

        # 3) 去除 BOM 和其他垃圾字符
        text = text.strip()

        # 解析 JSON
        return json.loads(text)

    except Exception as e:
        print(f"访问 {ip} 时出错: {e}")
        return None


def get_miner_hash_rate_by_ip(ip):
    miner_info = cgminer_summary(ip)
    if miner_info is None:
        return 0
    else:
        return miner_info["SUMMARY"][0]["MHS av"]


def get_hash_rate_online():
    for i in range(1, 6):
        try:
            h_online = ob_monitor.fetch_luxor_kpi()
            if h_online is not None and h_online > 0:
                return h_online
        except Exception as e:
            print(f"获取在线算力时出错: {e}")
        time.sleep(30)
    return 0



def get_total_hash_locate():
    try:
        ips = utils.utils_k.txt_2_list('../ips.txt')  # 示例 IP 列表

        # 记录程序开始时间
        start_time = time.time()

        total_hash_rate = 0  # 初始化总算力

        # 使用线程池并行请求所有 IP
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = executor.map(get_miner_hash_rate_by_ip, ips)

            # 计算总算力
            total_hash_rate = sum(results) / 1000 / 1000 / 1000

        # 记录程序结束时间
        end_time = time.time()

        print(f"所有IP的总算力: {total_hash_rate}")  # 打印总算力

        # 输出运行时间
        print(f"程序运行时间: {end_time - start_time:.2f} 秒")
        return total_hash_rate
    except Exception as e:
        print(f"获取总算力时出错: {e}")
        return 0


# 存储数据到 MongoDB 的函数
def store_hash_rate():
    try:
        # 获取当前时间，格式：YYYYMMDD_HHMM
        current_time = datetime.now().strftime("%Y%m%d_%H%M")

        # 获取矿机算力总和
        hash_rate_locate = get_total_hash_locate()
        hash_rate_online = get_hash_rate_online()

        # 存储到 MongoDB
        record = {
            "data_time": current_time,
            "hash_rate_locate": hash_rate_locate,
            "hash_rate_online": hash_rate_online
        }
        print(record)

        # 插入数据到 MongoDB
        collection.insert_one(record)
        print(f"存储数据成功：{current_time} - {hash_rate_locate} TH/s")

    except Exception as e:
        print(f"存储数据时出错: {e}")


# 设置每 15 分钟执行一次存储任务

if __name__ == "__main__":
    schedule.every(15).minutes.do(store_hash_rate)

    # 永久运行以持续执行任务
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            print(f"调度任务执行时出错: {e}")
            time.sleep(60)  # 如果调度任务执行时发生异常，休息 1 分钟后重试
