import utils.utils_k
from utils.get_hour_power_price import get_ercot_hb_west_prices
from utils.utils_k import ping_ip
from telegram import Bot
import asyncio
import schedule
import time
BOT_TOKEN = "5802231356:AAGomB_cjbTKCNX4kDbnUykgRC2lGaI2GKk"
CHAT_ID = "750326239"
CHAT_ID_ZHANG_PENG='8569953357'
bot = Bot(token=BOT_TOKEN)
def sort_ips_from_txt(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        ips = [line.strip() for line in f if line.strip()]

    # 使用 sort(key=...) 按每段数字排序
    ips.sort(key=lambda ip: list(map(int, ip.split('.'))))

    return ips

async def send_tele(message):
    bot = Bot(BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=message)
    await bot.send_message(chat_id=CHAT_ID_ZHANG_PENG, text=message)

def get_higher_70_power_price():
    date_string_tomorrow = utils.utils_k.date_to_string_tomorrow()
    url = "https://www.ercot.com/content/cdr/html/DATE_STRING_dam_spp.html".replace("DATE_STRING", date_string_tomorrow)
    date_price_d = get_ercot_hb_west_prices(url)

    high_price_messages = []

    if date_price_d:
        print(f"--- ERCOT HB_WEST 20251205 每小时电价 ---")
        for hour, price in date_price_d.items():
            if price>70:
                print(f"小时 {hour:02d}: ${price:.2f}")
                message = f"小时 {hour:02d}: ${price:.2f}"
                high_price_messages.append(message)
        output_string = "\n".join(high_price_messages)
        asyncio.run(send_tele("离线ip".join(output_string)))
    else:
        print("未能成功获取电价数据。")

def run_task_tele():
    ips = utils.utils_k.txt_2_list('ips.txt')
    ip_offline = []
    for ip in ips:
        if not ping_ip(ip):
            print(ip)
            ip_offline.append(ip)
    if len(ip_offline) > 0:
        asyncio.run(send_tele("离线ip".join(ip_offline)))


if __name__ == "__main__":
    asyncio.run(send_tele("启动BOT"))
    run_task_tele()
    schedule.every().day.at("14:00").do(get_higher_70_power_price)
    schedule.every(5).minutes.do(run_task_tele)
    while True:
        schedule.run_pending()
        time.sleep(1)