import platform
import subprocess
import socket
import json
from datetime import datetime , timedelta

MONGODB_URL = 'mongodb+srv://kevin_miner_test:Peerless123@cluster0.458zxp3.mongodb.net/?retryWrites=true&w=majority'


def txt_2_list(txt_path):
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            lines = f.readlines()  # 每行作为列表元素
            lines = [line.strip() for line in lines]  # 去掉换行符
        return lines
    except Exception as e:
        print(f"读取 Excel 文件时出错: {e}")
        return []


def ping_ip(ip: str, timeout=1) -> bool:
    """判断IP是否可达"""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        result = subprocess.run(
            ["ping", param, "1", ip],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return "reply from" in result.stdout.lower() or "ttl=" in result.stdout.lower()
    except Exception:
        return False


def date_to_string():
    # 获取当前的日期和时间
    current_date = datetime.now()

    # 格式化日期对象为指定的字符串格式：
    # %Y 代表四位数年份 (2025)
    # %m 代表两位数月份 (12)
    # %d 代表两位数日期 (05)
    date_string = current_date.strftime("%Y%m%d")

    # 打印结果
    print(date_string)
    return date_string

def cgminer_api(ip, command="summary"):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    s.connect((ip, 4028))
    s.send(json.dumps({"command": command}).encode())
    data = s.recv(4096).decode()
    s.close()

    # cgminer 返回是 key=val 格式，需要修复成 JSON
    data = data.replace('\x00', '')
    if not data.endswith('}'):
        data += '}'
    return json.loads(data)
def date_to_string_tomorrow():
    """
    获取明天的日期，并将其格式化为 YYYYMMDD 格式的字符串。
    """
    # 1. 获取当前的日期和时间
    current_date = datetime.now()

    # 2. 计算明天的日期：当前日期 + 1 天
    # timedelta(days=1) 是实现日期加减的关键
    tomorrow_date = current_date + timedelta(days=1)

    # 3. 格式化日期对象为指定的字符串格式：
    # %Y 代表四位数年份 (2025)
    # %m 代表两位数月份 (12)
    # %d 代表两位数日期 (06)
    date_string = tomorrow_date.strftime("%Y%m%d")

    # 打印结果
    print(date_string)
    return date_string

if __name__ == "__main__":
    info = cgminer_api("10.2.1.5", "devs")
    print(info)
