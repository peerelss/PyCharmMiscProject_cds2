import socket


def send_miner_command(ip, port=4028):
    # 构建与你命令行中一致的 payload
    # echo -n "ascset|0,workmode,2"
    command = "ascset|0,workmode,2"

    try:
        # 1. 创建 TCP Socket
        # socat -t 300 表示超时时间
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(300)

        # 2. 连接到矿机
        sock.connect((ip, port))

        # 3. 发送指令
        sock.sendall(command.encode('utf-8'))

        # 4. 接收返回结果 (shut-none 模式下通常会等待矿机吐回数据)
        response = b""
        while True:
            data = sock.recv(4096)
            if not data:
                break
            response += data
            # 如果收到特定的结束符也可以提前跳出
            if b'\x00' in data:
                break

        print(f"矿机响应: {response.decode('utf-8', errors='ignore')}")

    except Exception as e:
        print(f"连接失败: {e}")
    finally:
        sock.close()


# 执行
send_miner_command("10.1.1.11")