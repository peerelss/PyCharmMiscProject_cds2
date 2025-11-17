from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
TOKEN = '0054997437:AAEo96sEDCsDoCGG2vWBw_3fudGCulRBpTU'
TOKEN_Test = '5802231356:AAGomB_cjbTKCNX4kDbnUykgRC2lGaI2GKk'
KEVIN="750326239"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! 我是你的Telegram机器人。")

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"你好 {update.effective_user.first_name}!")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("hello", hello))

app.run_polling()
