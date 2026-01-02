import logging
import os
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import utils.utils_k
from utils.get_hour_power_price import get_ercot_hb_west_prices
from utils.utils_k import ping_ip

# 1. 配置日志记录 (可选，但推荐)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# 设置 telegram 库的日志级别为 WARNING，减少输出
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# --- 2. 消息处理函数 ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /start 命令，并回复欢迎消息。"""
    user = update.effective_user
    # 使用 reply_html 方法，可以利用 HTML 标签进行格式化
    await update.message.reply_html(
        f"你好, {user.mention_html()}! 我是一个回声 Bot。",
        # 可以添加 keyboard 选项，但这里省略
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /help 命令。"""
    await update.message.reply_text("你可以发送任何文本消息给我，我会把它回显给你。")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理所有文本消息，并回复相同的内容。"""
    # update.message.text 包含用户发送的文本内容
    user_message = update.message.text
    chat_id = update.effective_chat.id
    user_message = update.message.text

    # 2. 记录 chat_id (例如：打印到控制台)
    print(f"接收到来自 Chat ID: {chat_id} 的消息。")
    print(f"消息内容: {user_message}")
    # 使用 update.message.reply_text() 是最直接的回复方式
    await update.message.reply_text(f"你说了: {user_message}")


# --- 3. 主函数和运行逻辑 ---

def main() -> None:
    """启动 Bot。"""

    # ⚠️ 替换为您的 Bot Token
    # 推荐从环境变量中读取 Token，更加安全
    # BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    BOT_TOKEN = "5802231356:AAGomB_cjbTKCNX4kDbnUykgRC2lGaI2GKk"

    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("请替换您的 BOT_TOKEN 变量！")
        return

    # 1. 创建 Application 实例
    application = Application.builder().token(BOT_TOKEN).build()

    # 2. 注册 Handlers (处理器)
    # CommandHandler: 处理以 / 开头的命令 (如 /start, /help)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # MessageHandler: 处理普通的消息
    # filters.TEXT & ~filters.COMMAND: 筛选出所有文本消息，但不包括命令
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # 3. 运行 Bot (轮询模式)
    logger.info("Bot 正在启动...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)




if __name__ == "__main__":
    ips = utils.utils_k.txt_2_list('ips.txt')
    ip_offline = []
    time_now = datetime.now()
    for ip in ips:
        if not ping_ip(ip):
            print(f"{ip},离线时间为:{time_now}")
            ip_offline.append(ip)
