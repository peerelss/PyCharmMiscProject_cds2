import requests
from bs4 import BeautifulSoup
import datetime
import csv
import time

BASE_URL = "https://www.ercot.com/content/cdr/html/{}_real_time_spp.html"

start_date = datetime.date(2025, 12, 1)
end_date = datetime.date(2025, 12, 31)

# { date_str: { interval: price } }
matrix = {}

current = start_date
all_intervals = set()

while current <= end_date:
    date_str = current.strftime("%Y%m%d")
    url = BASE_URL.format(date_str)
    print(f"Fetching {date_str} ...")

    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch {date_str}:", e)
        current += datetime.timedelta(days=1)
        continue

    soup = BeautifulSoup(resp.text, "html.parser")
    rows = soup.find_all("tr")

    # find header row
    headers = [h.get_text(strip=True) for h in rows[0].find_all(["th", "td"])]
    if "HB_WEST" not in headers:
        print(f"HB_WEST missing for {date_str}")
        current += datetime.timedelta(days=1)
        continue

    idx_hb = headers.index("HB_WEST")
    idx_int = headers.index("Interval Ending")

    matrix[date_str] = {}

    # parse each 15-min row
    for row in rows[1:]:
        cols = [c.get_text(strip=True) for c in row.find_all(["td","th"])]
        if len(cols) > idx_hb:
            interval = cols[idx_int]
            try:
                price = float(cols[idx_hb])
            except:
                continue
            matrix[date_str][interval] = price
            all_intervals.add(interval)

    time.sleep(0.5)  # avoid rapid requests
    current += datetime.timedelta(days=1)

# sort intervals
sorted_intervals = sorted(all_intervals)

# write matrix CSV
with open("HB_WEST_202512_real_time_matrix.csv", "w", newline="") as f:
    writer = csv.writer(f)

    # header
    writer.writerow(["Date"] + sorted_intervals)

    for date in sorted(matrix.keys()):
        row = [date]
        for iv in sorted_intervals:
            row.append(matrix[date].get(iv, ""))  # empty if missing
        writer.writerow(row)

print("Saved to HB_WEST_202512_real_time_matrix.csv")
