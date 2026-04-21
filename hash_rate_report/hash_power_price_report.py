import requests
from bs4 import BeautifulSoup
import pymongo
import csv
from collections import defaultdict

client_url = "mongodb+srv://kevin_miner_test:Peerless123@cluster0.458zxp3.mongodb.net/?retryWrites=true&w=majority"
client_online = pymongo.MongoClient(client_url)  # 连接到 MongoDB Atlas
db_online = client_online["mining_data"]
collection = db_online["hash_rates"]

TARGET_DATE = "20260219"


# ---------- 获取实时电价 ----------
def fetch_rt_grouped(date_str):
    url = f"https://www.ercot.com/content/cdr/html/{date_str}_real_time_spp.html"
    r = requests.get(url, timeout=10)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    headers = [h.get_text(strip=True) for h in soup.find("tr").find_all(["th", "td"])]

    idx_hb = headers.index("HB_WEST")

    prices = []

    # 取出全部 96 个 15min 数据
    for row in soup.find_all("tr")[1:]:
        cols = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
        if len(cols) > idx_hb:
            try:
                prices.append(float(cols[idx_hb]))
            except:
                pass

    if len(prices) != 96:
        raise ValueError(f"{date_str}: Expected 96 intervals, got {len(prices)}")

    # 和 fetch_rt_prices 一致的结构
    grouped = defaultdict(list)

    for h in range(24):
        grouped[h] = prices[h * 4:(h + 1) * 4]  # Hour Ending 1–24

    return grouped


# ---------- 获取 DAM 电价 ----------
def fetch_da_prices(date_str):
    url = f"https://www.ercot.com/content/cdr/html/{date_str}_dam_spp.html"
    hourly = {}

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except:
        return hourly

    soup = BeautifulSoup(r.text, "html.parser")
    headers = [h.get_text(strip=True) for h in soup.find("tr").find_all(["th", "td"])]

    if "Hour Ending" not in headers or "HB_WEST" not in headers:
        return hourly

    idx_hr = headers.index("Hour Ending")
    idx_hb = headers.index("HB_WEST")

    for row in soup.find_all("tr")[1:]:
        cols = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
        if len(cols) > idx_hb:
            try:
                hr = int(cols[idx_hr])
                price = float(cols[idx_hb])
                hourly[hr - 1] = price  # 转成 0-23
            except:
                pass

    return hourly


# ---------- 1) 电价 ----------

rt_price_map = fetch_rt_grouped(TARGET_DATE)
avg_rt = {h: (sum(v) / len(v) if v else 0) for h, v in rt_price_map.items()}

da_price_map = fetch_da_prices(TARGET_DATE)

# ---------- 2) Hash 每小时平均 ----------
query = {"data_time": {"$regex": f"^{TARGET_DATE}_"}}
records = list(collection.find(query))

hourly_hash = defaultdict(lambda: {"locate": [], "online": []})

for r in records:
    hour = int(r["data_time"].split("_")[1][:2])
    hourly_hash[hour]["locate"].append(r.get("hash_rate_locate", 0))
    hourly_hash[hour]["online"].append(r.get("hash_rate_online", 0))

# ---------- 3) 写 CSV ----------
csv_file = f"{TARGET_DATE}_combined_hash_price_5.csv"

with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow([
        "Hour",
        'status',
        "Avg_Hash_Locate(TH/s)",
        "Avg_Hash_Online(TH/s)",
        "DAM_Price($/MWh)",
        "Avg_RT_Price($/MWh)"
    ])
    status = 'on'
    for h in range(24):
        loc_list = hourly_hash[h]["locate"]
        onl_list = hourly_hash[h]["online"]

        avg_loc = sum(loc_list) / len(loc_list) if loc_list else 0
        avg_onl = sum(onl_list) / len(onl_list) if onl_list else 0

        dam = da_price_map.get(h, 0)
        rt = avg_rt.get(h+1, 0)
        if avg_loc == 0:
            status = 'off'
        writer.writerow([
            TARGET_DATE + "_" + str(h), status,
            round(avg_loc, 4),
            round(avg_onl, 4),
            round(dam, 3),
            round(rt, 3)
        ])

print(f"Saved => {csv_file}")
