import requests
import json


def fetch_luxor_kpi():
    # 1. 基础配置
    url = "https://app.luxor.tech/api/trpc/watcherV2.getKpi,watcherV2.getKpi,watcherV2.getKpi"
    params = {"batch": "1"}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "trpc-accept": "application/jsonl",  # 关键：告知服务器我们接受行分隔的 JSON
        "x-lux-watcher-token": "watcher-cfabb00ab508bff0db810c5f1c92a003",
        "x-trpc-source": "nextjs-react",
        "Referer": "https://app.luxor.tech/zh/views/v2?token=watcher-cfabb00ab508bff0db810c5f1c92a003",
        "Origin": "https://app.luxor.tech"
    }

    # 2. 构造请求 Payload
    payload = {
        "0": {
            "json": {
                "currencyProfile": 1,
                "workspaceId": "",
                "kpiType": 5,
                "subaccounts": {"ids": [1174665], "names": []}
            }
        },
        "1": {
            "json": {
                "kpiType": 2,
                "currencyProfile": 1,
                "workspaceId": "",
                "subaccounts": {"ids": [1174665], "names": []},
                "dateRange": {
                    "startDate": {"$typeName": "google.protobuf.Timestamp", "seconds": "1771394400", "nanos": 0},
                    "endDate": {"$typeName": "google.protobuf.Timestamp", "seconds": "1771441286", "nanos": 966000000}
                },
                "granularityMinutes": 5
            },
            "meta": {
                "values": {
                    "dateRange.startDate.seconds": ["bigint"],
                    "dateRange.endDate.seconds": ["bigint"]
                },
                "v": 1
            }
        },
        "2": {
            "json": {
                "currencyProfile": 1,
                "workspaceId": "",
                "kpiType": 8,
                "subaccounts": {"ids": [1174665], "names": []},
                "pagination": {"pageIndex": 1, "pageSize": 10},
                "lastSeconds": 900,
                "sorting": [],
                "workers": {"status": 0, "name": ""}
            }
        }
    }

    try:
        # 3. 发送 POST 请求 (使用 stream=True 以便逐行处理)
        response = requests.post(url, params=params, headers=headers, json=payload, stream=True)
        response.raise_for_status()
        results = []
        for line in response.iter_lines():
            if line:
                results.append(json.loads(line))
        h5 = 0
        # 现在 results 是一个列表，包含了 0, 1, 2 三个请求的结果
        for i, result in enumerate(results):
            print(f"--- Result for part {i} ---")
        #    print(json.dumps(result, indent=2, ensure_ascii=False))
            if i==6:
                target_kpi = result["json"][2][0][0]["kpi"]["value"]["hashrateFiveMinutes"]

                last_period =  (target_kpi["lastPeriod"])
                h5=int(last_period)/1000/1000/1000/1000/1000
                print(f"5分钟算力 (lastPeriod): {last_period}")
                print(f"5分钟算力 (h5): {h5}")
        print("--- 开始解析返回数据 ---")

        return h5

    except Exception as e:
        print(f"程序运行出错: {e}")
        return 0


if __name__ == "__main__":
    fetch_luxor_kpi()