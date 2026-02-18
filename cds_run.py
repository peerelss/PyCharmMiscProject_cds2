import ob_monitor
import utils.utils_k
from mienr_info import get_miner_temp_by_ip, get_miner_hash_rate_by_ip
from utils.utils_k import ping_ip
from telegram import Bot
import asyncio
import schedule
import time
from datetime import datetime

now_local = datetime.now()
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["network_monitor"]
collection = db["ip_offline_logs"]
collection_over_heat = db["ip_over_heat"]

HASH_RATE = 200  # 默认算力
ONLINE_MINER = 1004  # 默认在线机器

BOT_TOKEN = "5802231356:AAGomB_cjbTKCNX4kDbnUykgRC2lGaI2GKk"

CHAT_ID = "750326239"
CHAT_ID_ZHANG_PENG = '8569953357'
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




def run_task_tele():
    try:
        ips = utils.utils_k.txt_2_list('ips.txt')
        ip_offline = []
        ip_over_heat = []
        time_now = datetime.now()
        for ip in ips:
            if not ping_ip(ip):
                print(f"{ip},离线时间为:{time_now}")
                ip_offline.append(ip)
            '''else:
                ip_hash=get_miner_hash_rate_by_ip(ip)
                if ip_hash and ip_hash>0:
                    pass
                else:
                    temp_ip = get_miner_temp_by_ip(ip)
                    if temp_ip and temp_ip['temp'] > 70:
                        ip_over_heat.append([ip, temp_ip['temp']])
                        print(f"{ip} 高温,温度为：{temp_ip['temp']},时间为:{time_now}")
                        '''
        if len(ip_offline) > 0:
            message_str = "离线ip".join(ip_offline)
            if len(message_str) < 4000:
                asyncio.run(send_tele(message_str))
            else:
                asyncio.run(send_tele("离线ip过多"))
            docs = [
                {
                    "ip": ip,
                    "status": "offline",
                    "created_at": datetime.now()
                }
                for ip in ip_offline
            ]
            collection.insert_many(docs)

        if len(ip_over_heat) > 0:
            message_str = "高温ip".join(ip_offline)

            docs = [
                {
                    "ip": ip,
                    "status": "over_heat",
                    "temp": ip_temp,
                    "created_at": datetime.now()
                }
                for ip, ip_temp in ip_over_heat
            ]
            collection_over_heat.insert_many(docs)
    except Exception as e:
        asyncio.run(send_tele(f" 故障！！！{e} "))


if __name__ == "__main__":
    asyncio.run(send_tele("启动BOT"))
    run_task_tele()
    schedule.every(5).minutes.do(run_task_tele)
    while True:
        schedule.run_pending()
        time.sleep(1)
