import utils.utils_k
from utils.utils_k import ping_ip
from telegram import Bot
import asyncio
import schedule
import time
BOT_TOKEN = "5802231356:AAGomB_cjbTKCNX4kDbnUykgRC2lGaI2GKk"
CHAT_ID = "750326239"

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
    run_task_tele()
    schedule.every(5).minutes.do(run_task_tele)
    while True:
        schedule.run_pending()
        time.sleep(1)