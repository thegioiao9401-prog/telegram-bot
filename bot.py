from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import json
import os

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Bot lưu code PRO đã sẵn sàng!")

# /save python print("hi")
async def save_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Cách dùng: /save python code...")
        return

    tag = context.args[0]
    code = " ".join(context.args[1:])

    data = load_data()
    new_id = len(data) + 1

    data.append({
        "id": new_id,
        "tag": tag,
        "code": code
    })

    save_data(data)

    await update.message.reply_text(f"✅ Đã lưu với ID {new_id}")

# /list python
async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()

    if not data:
        await update.message.reply_text("Chưa có dữ liệu!")
        return

    if context.args:
        tag = context.args[0]
        data = [d for d in data if d["tag"] == tag]

    msg = ""
    for d in data[:20]:
        msg += f'{d["id"]}. [{d["tag"]}] {d["code"]}\n'

    await update.message.reply_text(msg or "Không có kết quả")

# /search python
async def search_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Nhập từ khóa!")
        return

    keyword = " ".join(context.args).lower()
    data = load_data()

    results = [d for d in data if keyword in d["code"].lower()]

    msg = ""
    for d in results[:20]:
        msg += f'{d["id"]}. [{d["tag"]}] {d["code"]}\n'

    await update.message.reply_text(msg or "Không tìm thấy")

# /delete 1
async def delete_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Nhập ID cần xoá")
        return

    delete_id = int(context.args[0])
    data = load_data()

    new_data = [d for d in data if d["id"] != delete_id]

    save_data(new_data)

    await update.message.reply_text(f"🗑️ Đã xoá ID {delete_id}")

import os

TOKEN = os.getenv("8651273302:AAEU_uh0nJzY4YqhKcF9P-aHGTEr5GKdcuA")
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("save", save_cmd))
app.add_handler(CommandHandler("list", list_cmd))
app.add_handler(CommandHandler("search", search_cmd))
app.add_handler(CommandHandler("delete", delete_cmd))

print("🔥 Bot PRO đang chạy...")
app.run_polling()
