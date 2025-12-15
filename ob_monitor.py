from threading import active_count

import requests
import json
import time


def fetch_luxor_pool_data():
    """
    Sends a batched tRPC request to the Luxor mining pool API to fetch
    watcher statistics like hashrate, efficiency, and workers.
    """
    url = 'https://app.luxor.tech/api/trpc/pool.watcher.getHashrate,pool.watcher.getHashrate,pool.watcher.getActiveMiners,pool.watcher.getEfficiency,pool.watcher.getUptime,pool.watcher.getPendingBalance,pool.watcher.getRevenue,pool.watcher.getHashrateAndEfficiencyHistory,pool.watcher.getWorkers,pool.watcher.incrementWatcherViewCount?batch=1'

    # The token is part of the URL and the headers, and the progressiveUserId is in the payload.
    # Replace with a valid token if the original one expires.
    watcher_token = 'watcher-cfabb00ab508bff0db810c5f1c92a003'
    progressive_user_id = 1174665
    current_timestamp_s = int(time.time())

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'content-type': 'application/json',
        'origin': 'https://app.luxor.tech',
        'priority': 'u=1, i',
        'referer': f'https://app.luxor.tech/en/views/watcher?token={watcher_token}',
        'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'trpc-accept': 'application/jsonl',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'x-lux-watcher-token': watcher_token,
        'x-trpc-source': 'nextjs-react',
    }

    cookies = {
        'slug': 'luxor',
        'i18next': 'en',
    }

    # The date range for 'getHashrateAndEfficiencyHistory' needs to be calculated
    # based on the current time to ensure the request is valid.
    date_range_end = current_timestamp_s
    date_range_start = current_timestamp_s - (15 * 3600)  # 15 hours ago

    data_payload = {
        "0": {"json": {"progressiveUserIds": [progressive_user_id], "currencyProfile": 1, "lastSeconds": 300}},
        "1": {"json": {"progressiveUserIds": [progressive_user_id], "currencyProfile": 1, "lastSeconds": 86400}},
        "2": {"json": {"progressiveUserIds": [progressive_user_id], "currencyProfile": 1, "lastSeconds": 300}},
        # Target function
        "3": {"json": {"progressiveUserIds": [progressive_user_id], "currencyProfile": 1, "lastSeconds": 300}},
        "4": {"json": {"progressiveUserIds": [progressive_user_id], "currencyProfile": 1, "lastSeconds": 86400}},
        "5": {"json": {"progressiveUserIds": [progressive_user_id], "currencyProfile": 1}},
        "6": {"json": {"progressiveUserIds": [progressive_user_id], "currencyProfile": 1, "lastSeconds": 86400}},
        "7": {
            "json": {
                "progressiveUserIds": [progressive_user_id],
                "currencyProfile": 1,
                "dateRange": {
                    "$typeName": "google.protobuf.Timestamp",
                    "startDate": {"$typeName": "google.protobuf.Timestamp", "seconds": str(date_range_start),
                                  "nanos": 0},
                    "endDate": {"$typeName": "google.protobuf.Timestamp", "seconds": str(date_range_end), "nanos": 0}
                },
                "granularityMinutes": 5
            },
            "meta": {"values": {"dateRange.startDate.seconds": ["bigint"], "dateRange.endDate.seconds": ["bigint"]},
                     "v": 1}
        },
        "8": {
            "json": {
                "currencyProfile": 1,
                "progressiveUserIds": [progressive_user_id],
                "pagination": {"pageNumber": 1, "pageSize": 10},
                "lastSeconds": 900,
                "filter": {"name": "", "status": 1, "sorting": {"id": "workername", "desc": False}}
            }
        },
        "9": {"json": {}}
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            cookies=cookies,
            data=json.dumps(data_payload)
        )
        response.raise_for_status()

        data_lines = response.text.strip().split('\n')
        parsed_results = [json.loads(line) for line in data_lines]

        print("✅ Request successful. Data summary:")

        # --- Active Miners Extraction ---
        # The result for 'pool.watcher.getActiveMiners' is at index 2
        active_miners_result = parsed_results[2]

        # Structure path: [2] -> 'result' -> 'data' -> 'json' -> [2] -> [0] -> [0] -> 'activeMiners'
        try:
            active_miners_count = (
                active_miners_result
                .get('result', {})
                .get('data', {})
                .get('json', [])[2][0][0]
                .get('activeMiners')
            )
            print(f"\n--- 💰 ACTIVE MINERS ---")
            print(f"Active Miners: {active_miners_count}")
        except (IndexError, TypeError, KeyError) as e:
            print(f"\n❌ Error extracting Active Miners data: {e}")
            active_miners_count = "N/A"
        # -------------------------------

        # 0: pool.watcher.getHashrate (300s)
        print(f"\n--- 300s Hashrate ---")
        hashrate_300s = parsed_results[0].get('result', {}).get('data', {}).get('json', {})
        print(f"Hashrate: {hashrate_300s.get('hashrate')} {hashrate_300s.get('unit')}")

        # 3: pool.watcher.getEfficiency (300s)
        print(f"\n--- 300s Efficiency ---")
        efficiency_300s = parsed_results[3].get('result', {}).get('data', {}).get('json', {})
        print(f"Efficiency: {efficiency_300s.get('efficiency', 'N/A')}")

        # 8: pool.watcher.getWorkers (900s)
        print(f"\n--- Workers Summary (Page 1) ---")
        workers_data = parsed_results[8].get('result', {}).get('data', {}).get('json', {})
        worker_count = len(workers_data.get('workers', []))
        total_workers = workers_data.get('totalCount')
        print(f"Found {worker_count} of {total_workers} total workers in the list.")

        return parsed_results

    except requests.exceptions.RequestException as e:
        print(f"❌ An error occurred: {e}")
        print(f"Response content: {getattr(e.response, 'text', 'N/A')}")
        return None

def get_active_miner_and_hashrate():
    data = fetch_luxor_pool_data()
    active_count = 0
    active_hashrate = 0
    for d in data:
        dd = list(d['json'])
        for d3 in dd[2]:
            for d4 in d3:
                if type(d4) is dict:
                    if 'activeMiners' in d4:
                        d4c = int(d4['activeMiners'])
                        if d4c > active_count:
                            active_count = d4c
                    if 'hashrateLastPeriod' in d4:
                        d4h = float(d4['hashrateLastPeriod'])/1000/1000/1000/1000/1000
                        if d4h > active_hashrate:
                            active_hashrate = d4h
    return active_count, active_hashrate

if __name__ == "__main__":
    # 1. 调用函数获取结果列表
    ac,ah=get_active_miner_and_hashrate()
    print(ac)
    print(ah)