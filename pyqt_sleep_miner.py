import requests
import json

# 设置会话
session = requests.Session()

# 设置请求头
headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://app.luxor.tech",
    "priority": "u=1, i",
    "referer": "https://app.luxor.tech/zh/views/v2?token=watcher-cfabb00ab508bff0db810c5f1c92a003",
    "sec-ch-ua": "\"Not(A:Brand);v=\"8\", \"Chromium\";v=\"144\", \"Microsoft Edge\";v=\"144\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "trpc-accept": "application/jsonl",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0",
    "x-lux-watcher-token": "watcher-cfabb00ab508bff0db810c5f1c92a003",
    "x-trpc-source": "nextjs-react"
}

# 设置 cookies
session.cookies.set('slug', 'luxor', domain='.luxor.tech', path='/')
session.cookies.set('i18next', 'zh', domain='app.luxor.tech', path='/')

# 请求体数据
data = {
    "0": {
        "json": {
            "currencyProfile": 1,
            "workspaceId": "",
            "kpiType": 5,
            "subaccounts": {
                "ids": [1174665],
                "names": []
            }
        }
    },
    "1": {
        "json": {
            "kpiType": 2,
            "currencyProfile": 1,
            "workspaceId": "",
            "subaccounts": {
                "ids": [1174665],
                "names": []
            },
            "dateRange": {
                "startDate": {
                    "$typeName": "google.protobuf.Timestamp",
                    "seconds": "1771394400",
                    "nanos": 0
                },
                "endDate": {
                    "$typeName": "google.protobuf.Timestamp",
                    "seconds": "1771441121",
                    "nanos": 548000000
                }
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
            "subaccounts": {
                "ids": [1174665],
                "names": []
            },
            "pagination": {
                "pageIndex": 1,
                "pageSize": 10
            },
            "lastSeconds": 900,
            "sorting": [],
            "workers": {
                "status": 0,
                "name": ""
            }
        }
    }
}

# 发送 POST 请求
url = "https://app.luxor.tech/api/trpc/watcherV2.getKpi,watcherV2.getKpi,watcherV2.getKpi?batch=1"
response = session.post(url, headers=headers, json=data)

# 打印响应的状态码和内容
print(f"响应状态码: {response.status_code}")
print(f"响应内容: {response.json()}")
