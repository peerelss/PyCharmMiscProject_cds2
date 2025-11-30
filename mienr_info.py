import socket
import json


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
        print("原始返回：", raw)
        return None
# ------------------ 测试 ------------------

def get_miner_hash_rate_by_ip(ip):
    miner_info=cgminer_summary(ip)
    print(miner_info)
    if miner_info is None:
        return None
    else:
        return miner_info["SUMMARY"][0]["MHS av"]


if __name__ == "__main__":
   print("")