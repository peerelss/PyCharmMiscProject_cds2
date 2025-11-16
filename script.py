import ipaddress
import socket
import json
import requests

# --------------------------
# 端口检测
# --------------------------
def check_port(ip, port, timeout=0.3):
    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect((ip, port))
        return True
    except:
        return False
    finally:
        s.close()

# --------------------------
# 判断是否为 Avalon Web
# --------------------------
def is_avalon_web(ip):
    try:
        r = requests.get(f"http://{ip}/", timeout=0.5)
        if "Avalon" in r.text or "Canaan" in r.text:
            return True
    except:
        pass
    return False

# --------------------------
# 调用 CGMiner API
# --------------------------
def cgminer_cmd(ip, command="summary", timeout=0.8):
    s = socket.socket()
    s.settimeout(timeout)
    s.connect((ip, 4028))
    payload = json.dumps({"command": command}).encode()
    s.send(payload)
    data = s.recv(4096)
    s.close()
    return json.loads(data.decode("utf-8", errors="ignore"))

# --------------------------
# 扫描整个网段
# --------------------------
def scan_network(prefix="10.1.1.0/24"):
    net = ipaddress.ip_network(prefix)
    results = []

    print(f"开始扫描网段：{prefix}")

    for ip_obj in net.hosts():
        ip = str(ip_obj)

        # 检查 80 端口（Web）
        if check_port(ip, 80):
            if is_avalon_web(ip):
                results.append({"ip": ip, "type": "Avalon Miner (Web)"})
                print(f"[+] 发现 Avalon Web：{ip}")
                continue

        # 检查 4028 端口（CGMiner API）
        if check_port(ip, 4028):
            try:
                r = cgminer_cmd(ip, "summary")
                if "SUMMARY" in r:
                    results.append({"ip": ip, "type": "Avalon (CGMiner)"})
                    print(f"[+] 发现 CGMiner 设备：{ip}")
            except Exception as e:
                pass

    return results

# --------------------------
# 测试运行
# --------------------------
if __name__ == "__main__":
    devices = scan_network("10.1.1.0/24")
    print("\n扫描结果：")
    print(devices)
