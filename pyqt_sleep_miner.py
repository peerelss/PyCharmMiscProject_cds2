import requests
from bs4 import BeautifulSoup
from collections import defaultdict

def fetch_rt_grouped(date_str):
    url = f"https://www.ercot.com/content/cdr/html/{date_str}_real_time_spp.html"
    r = requests.get(url, timeout=10)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    headers = [h.get_text(strip=True) for h in soup.find("tr").find_all(["th","td"])]

    idx_hb = headers.index("HB_WEST")

    prices = []

    # 取出全部 96 个 15min 数据
    for row in soup.find_all("tr")[1:]:
        cols = [c.get_text(strip=True) for c in row.find_all(["td","th"])]
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
        grouped[h] = prices[h*4:(h+1)*4]  # Hour Ending 1–24

    return grouped


if __name__ == "__main__":
    print(fetch_rt_grouped("20260219"))