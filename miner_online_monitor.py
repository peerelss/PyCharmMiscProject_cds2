# 监控在线算力和机器数量， 发现机器数量或者在线算力大幅波动时，发出提醒
import utils.utils_k
from mienr_info import get_miner_hash_rate_by_ip
from utils.get_hour_power_price import get_ercot_hb_west_prices
from utils.utils_k import ping_ip
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
HASH_RATE=200 # 默认算力
ONLINE_MINER=1004 #默认在线机器

def get_all_online_ips_hash():
    ips = utils.utils_k.txt_2_list('ips.txt')
    with ThreadPoolExecutor(max_workers=30) as pool:
        return dict(pool.map(get_miner_hash_rate_by_ip, ips))


def get_hashrate_and_active_miner_online():
    pass


if __name__ == "__main__":
    results=get_all_online_ips_hash()
    print(results)
    ok_count = sum(1 for v in results.values() if v['code'] == 0)
    bad_count = sum(1 for v in results.values() if v['code'] != 0)

    total = len(results)

    print(f"总数: {total}")
    print(f"正常: {ok_count}")
    print(f"异常: {bad_count}")
