import platform
import subprocess
import socket
import json
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

if __name__ == "__main__":
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


    info = cgminer_api("10.2.1.5", "devs")
    print(info)