import utils.utils_k
from mienr_info import get_miner_hash_rate_by_ip
import concurrent.futures
import time

if __name__ == "__main__":

    start_time = time.time()
    total_hash_rate=0
    ips = utils.utils_k.txt_2_list('ips.txt')
    for ip in ips:
        hash_rate = get_miner_hash_rate_by_ip(ip)
        total_hash_rate += hash_rate
        # 记录程序结束时间
    end_time = time.time()

    print(f"所有IP的总算力: {total_hash_rate}")  # 打印总算力

    # 输出运行时间
    print(f"程序运行时间: {end_time - start_time:.2f} 秒")
