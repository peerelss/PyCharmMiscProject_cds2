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
    # The original curl request had specific, potentially old timestamps.
    # We will adjust it to cover the last 15 hours from now.
    date_range_end = current_timestamp_s
    date_range_start = current_timestamp_s - (15 * 3600)  # 15 hours ago

    data_payload = {
        "0": {"json": {"progressiveUserIds": [progressive_user_id], "currencyProfile": 1, "lastSeconds": 300}},
        "1": {"json": {"progressiveUserIds": [progressive_user_id], "currencyProfile": 1, "lastSeconds": 86400}},
        "2": {"json": {"progressiveUserIds": [progressive_user_id], "currencyProfile": 1, "lastSeconds": 300}},
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
            data=json.dumps(data_payload)  # The data must be sent as a JSON string
        )
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # The tRPC API returns JSON Lines (jsonl) when using 'trpc-accept: application/jsonl'
        # The response is a series of JSON objects separated by newlines.
        data_lines = response.text.strip().split('\n')

        print("✅ Request successful. Parsed data:")

        # Parse each line as a separate JSON object
        parsed_results = [json.loads(line) for line in data_lines]

        # The results are in the order of the functions in the URL/payload
        # You can now process the data for each call (e.g., hashrate, efficiency, workers)
        # For demonstration, we'll print a summary of the first few results

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
        # print(workers_data.get('workers', [])[0] if worker_count > 0 else "No workers data to show.")

        return parsed_results

    except requests.exceptions.RequestException as e:
        print(f"❌ An error occurred: {e}")
        print(f"Response content: {getattr(e.response, 'text', 'N/A')}")
        return None


if __name__ == "__main__":
    # 1. 调用函数获取结果列表
    data = fetch_luxor_pool_data()
    print(data)
