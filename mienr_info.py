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

        # -------------------------
        # 关键：清理脏数据
        # -------------------------

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
if __name__ == "__main__":
    ip = "10.1.1.1"   # 替换为你的矿机 IP
    info = cgminer_summary(ip)

    if info:
        print("\n=== SUMMARY 信息 ===")
        print(json.dumps(info, indent=4))