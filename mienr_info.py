import socket
import json
import re


def split_json_objects(text):
    objs = []
    buf = ""
    depth = 0

    for ch in text:
        if ch == "{":
            depth += 1
        if depth > 0:
            buf += ch
        if ch == "}":
            depth -= 1
            if depth == 0:
                objs.append(buf)
                buf = ""

    return objs


def merge_cgminer_json(text):
    result = {}

    for js in split_json_objects(text):
        try:
            obj = json.loads(js)
            result.update(obj)
        except json.JSONDecodeError:
            pass

    return result


def cgminer_status(ip, timeout=1.0):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, 4028))

        payload = json.dumps({"command": "stats"}).encode()
        s.sendall(payload)

        chunks = []
        while True:
            try:
                data = s.recv(4096)
                if not data:
                    break
                chunks.append(data)
            except socket.timeout:
                break

        s.close()

        raw = b"".join(chunks)
        text = raw.decode("utf-8", errors="ignore")

        # 去 NULL
        text = text.replace("\x00", "")

        # 拆分并合并多个 JSON
        return merge_cgminer_json(text)

    except Exception:
        return None


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


# ------------------ 测试 ------------------

def get_miner_hash_rate_by_ip(ip):
    miner_info = cgminer_summary(ip)
    if miner_info is None:
        return None
    else:
        return miner_info["SUMMARY"][0]["MHS av"]


def parse_temp_info(text: str):
    pattern = r"Temp\[(\d+)\]\s+TMax\[(\d+)\]\s+TAvg\[(\d+)\]"
    match = re.search(pattern, text)

    if not match:
        return None

    return {
        "temp": int(match.group(1)),
        "tmax": int(match.group(2)),
        "tavg": int(match.group(3))
    }


def get_miner_temp_by_ip(ip):
    miner_info = cgminer_status(ip)
    if miner_info is None:
        return None
    else:
        try:
            temp_str = miner_info["STATS"][0]['MM ID0']
            info = parse_temp_info(temp_str)
            return (info)
        except Exception as e:
            return None


if __name__ == "__main__":
    print(get_miner_hash_rate_by_ip('10.1.4.28'))
    #print(get_miner_temp_by_ip('10.3.1.75'))
