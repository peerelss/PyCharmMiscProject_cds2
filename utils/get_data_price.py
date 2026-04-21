import requests
from bs4 import BeautifulSoup
import datetime
import csv
import time

HB_WEST='HB_WEST'
LZ_WEST='LZ_WEST'


BASE_URL = "https://www.ercot.com/content/cdr/html/{}_dam_spp.html"

start_date = datetime.date(2025, 12, 1)
end_date = datetime.date(2025, 12, 31)

# 二维数据字典 {date: {hour: price}}
matrix = {}

current = start_date

while current <= end_date:
    date_str = current.strftime("%Y%m%d")
    url = BASE_URL.format(date_str)

    print(f"Fetching {date_str} ...")

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except:
        print(f"Failed: {date_str}")
        current += datetime.timedelta(days=1)
        continue

    soup = BeautifulSoup(resp.text, "html.parser")

    header_row = soup.find("tr")
    headers = [h.get_text(strip=True) for h in header_row.find_all(["th", "td"])]

    if "HB_WEST" not in headers:
        print(f"HB_WEST not found: {date_str}")
        current += datetime.timedelta(days=1)
        continue

    idx = headers.index("HB_WEST")

    matrix[date_str] = {}

    for row in soup.find_all("tr")[1:]:
        cols = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
        if len(cols) > idx:
            try:
                hour = int(cols[1])
                price = float(cols[idx])
                matrix[date_str][hour] = price
            except:
                continue

    time.sleep(0.5)
    current += datetime.timedelta(days=1)

# -------- 输出二维CSV --------

with open("HB_WEST_2512.csv", "w", newline="") as f:
    writer = csv.writer(f)

    # 表头：Date + 1-24小时
    header = ["Date"] + [str(h) for h in range(1, 25)]
    writer.writerow(header)

    # 每一行一个日期
    for date in sorted(matrix.keys()):
        row = [date]
        for h in range(1, 25):
            row.append(matrix[date].get(h, ""))  # 没数据就空
        writer.writerow(row)

print("Saved to HB_WEST.csv")
