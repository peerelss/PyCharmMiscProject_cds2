# 监控在线算力和机器数量， 发现机器数量或者在线算力大幅波动时，发出提醒
import utils.utils_k
from mienr_info import get_miner_hash_rate_by_ip
from utils.get_hour_power_price import get_ercot_hb_west_prices
from utils.utils_k import ping_ip
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
HASH_RATE=200 # 默认算力
ONLINE_MINER=1004 #默认在线机器
import datetime
import pandas as pd
def get_all_online_ips_hash():
    ips = utils.utils_k.txt_2_list('ips.txt')
    with ThreadPoolExecutor(max_workers=30) as pool:
        return dict(pool.map(get_miner_hash_rate_by_ip, ips))


def get_hashrate_and_active_miner_online():
    results = get_all_online_ips_hash()
    save_data_2_excel(results)
    print(results)
    ok_count = sum(1 for v in results.values() if v['code'] == 0)
    bad_count = sum(1 for v in results.values() if v['code'] != 0)

    total = len(results)

    print(f"总数: {total}")
    print(f"正常: {ok_count}")
    print(f"异常: {bad_count}")


def save_data_2_excel(results):
    df = pd.DataFrame.from_dict(results, orient='index')
    now = datetime.datetime.now()

    # 定义时间戳格式
    # 推荐格式：YYYYMMDD_HHMMSS
    # 例如：20251215_103045
    timestamp_str = now.strftime("%Y%m%d_%H%M%S")
    # 可选：将索引（IP 地址）转换为一个普通的列
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'IP_Address'}, inplace=True)

    # 2. 格式化哈希率 (Hashrate)
    # 为了让数据在 Excel 中更易读，通常需要将哈希率进行单位转换或格式化
    df['hashrate'] = df['hashrate'].apply(lambda x: f"{x / 10 ** 6:.2f} M/s")
    # 示例：将 H/s 转换为 M/s (MegaHash/秒) 并保留两位小数

    # 3. 写入 Excel 文件
    base_filename = "Miner_Status_Report"
    file_extension = ".xlsx"

    # 最终文件名： Miner_Status_Report_20251215_103045.xlsx
    output_file_name = f"{base_filename}_{timestamp_str}{file_extension}"
    df.to_excel(output_file_name,
                index=False,  # 不将 DataFrame 索引写入 Excel (因为 IP 已经作为列)
                sheet_name='Miner Data')

    print(f"数据已成功写入到文件: {output_file_name}")

if __name__ == "__main__":
    get_hashrate_and_active_miner_online()
