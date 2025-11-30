import socket
import json
import re

def fix_cgminer_json(data):
    """修复 cgminer 非标准 JSON"""

    # 去掉不可见控制字符
    data = ''.join(ch for ch in data if ord(ch) >= 32 or ch in '\n\r\t')

    # 替换 key=value 为 "key":"value"
    data = re.sub(r'(\w+)=', r'"\1":', data)

    # 将 | 分隔符替换为 ,
    data = data.replace("|", ",")

    # 处理多个 JSON 拼接 "}{" → "},{"
    data = data.replace("}{", "},{")

    # 加上外层大括号
    if not data.startswith("{"):
        data = "{" + data
    if not data.endswith("}"):
        data = data + "}"

    # 尝试解析
    try:
        return json.loads(data)
    except:
        return {"raw_data": data, "error": "JSON 格式仍无法解析"}

def cgminer_api(ip, command):
    """发送 cgminer API 指令"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((ip, 4028))
        send_data = json.dumps({"command": command})
        s.send(send_data.encode())

        data = s.recv(65535).decode()
        s.close()

        return fix_cgminer_json(data)

    except Exception as e:
        return {"error": str(e)}

def get_all_cgminer_info(ip):
    commands = ["summary", "stats", "devs", "pools", "config", "notify", "check"]

    result = {}
    for cmd in commands:
        print(f"获取 {cmd} ...")
        result[cmd] = cgminer_api(ip, cmd)

    return result

if __name__ == "__main__":
    ip = "10.4.11.247"   # 修改你的矿机 IP
    info = get_all_cgminer_info(ip)

    print(json.dumps(info, indent=4, ensure_ascii=False))
