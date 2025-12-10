import socket
import time
from typing import Optional, Tuple

# -----------------------------
# 配置
# -----------------------------
# 矿机 IP 列表
miner_ips = [
    "10.1.1.3",
]

# 端口
PORT = 4028
DEFAULT_PORT = 4028
# 要发送的命令
# 示例：停止 ASIC
COMMAND = "ascset|0,softoff"
COMMAND_SLEEP = "ascset|0,softoff"
COMMAND_WAKE = "ascset|0,reboot,1"


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


def send_tcp_command(host: str, command: str, port: int = DEFAULT_PORT, timeout: int = 30) -> Tuple[bool, str]:
    """
    通过 TCP 连接向指定地址发送命令并接收响应。

    Args:
        host (str): 目标服务器的 IP 地址或主机名。
        command (str): 要发送的命令字符串 (例如: "ascset|0,reboot,0")。
        port (int): 目标服务器的端口号。默认为 4028。
        timeout (int): socket 操作的超时时间（秒）。默认为 30 秒。

    Returns:
        Tuple[bool, str]:
            - 第一个元素 (bool) 表示操作是否成功。
            - 第二个元素 (str) 包含接收到的响应（成功时）或错误信息（失败时）。
    """
    data_to_send = command.encode('utf-8')

    try:
        # 1. 使用 socket.create_connection 尝试连接
        # socket.create_connection(address, timeout=..., source_address=...)
        # 它会自动处理创建 socket, 设置超时, 和连接 (Connect) 三个步骤。
        with socket.create_connection((host, port), timeout=timeout) as s:

            # 2. 发送数据
            # 使用 s.sendall() 确保所有数据都被发送
            s.sendall(data_to_send)

            # 3. 接收响应
            # 阻塞式接收数据。如果服务器发送的数据小于 4096 字节，
            # 且服务器随后关闭了连接或执行了 shutdown(SHUT_WR)，recv 将返回实际接收到的数据。
            # 否则它会等待直到缓冲区满或超时。
            data = s.recv(4096)

            # 4. 返回成功状态和解码后的响应
            return True, data.decode('utf-8').strip()

    except socket.timeout:
        return False, f"错误：连接或数据传输超时 ({timeout}s)。"
    except ConnectionRefusedError:
        return False, "错误：连接被拒绝，请检查端口是否开放，服务是否运行。"
    except Exception as e:
        # 捕获其他所有 socket 相关的错误（如主机名解析失败等）
        return False, f"发生连接错误: {e}"


# -----------------------------
# 主程序
# -----------------------------
if __name__ == "__main__":
    for ip in miner_ips:
        print(f"Sending command to {ip} ...")
        response = send_command(ip, COMMAND)
        print(f"{ip} response: {response}")
        time.sleep(0.5)  # 可以加短延时，防止网络拥堵
