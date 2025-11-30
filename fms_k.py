import socket
import time

# -----------------------------
# 配置
# -----------------------------
# 矿机 IP 列表
miner_ips = [
    "10.1.1.3",
]

# 端口
PORT = 4028

# 要发送的命令
# 示例：停止 ASIC
COMMAND = "ascset|0,softoff"

# 如果想恢复挖矿，可以改成
# COMMAND = "ascset|0,softon"
# 或控制算力
# COMMAND = "ascset|0,hashpower,0"

# -----------------------------
# 批量发送函数
# -----------------------------
def send_command(ip, command, timeout=30):
    try:
        with socket.create_connection((ip, PORT), timeout=timeout) as s:
            s.sendall(command.encode())
            # 等待响应
            data = s.recv(4096)
            return data.decode()
    except Exception as e:
        return f"Error: {e}"

# -----------------------------
# 主程序
# -----------------------------
if __name__ == "__main__":
    for ip in miner_ips:
        print(f"Sending command to {ip} ...")
        response = send_command(ip, COMMAND)
        print(f"{ip} response: {response}")
        time.sleep(0.5)  # 可以加短延时，防止网络拥堵
