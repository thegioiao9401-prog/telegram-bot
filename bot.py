from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask, request
import json
import os
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "data.json"

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

# ===== DATA =====
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ===== COMMANDS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Bot webhook PRO đã sẵn sàng!")

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

    await update.message.reply_text(f"✅ Đã lưu ID {new_id}")

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

async def delete_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Nhập ID cần xoá")
        return

    try:
        delete_id = int(context.args[0])
    except:
        await update.message.reply_text("ID không hợp lệ")
        return

    data = load_data()
    new_data = [d for d in data if d["id"] != delete_id]

    save_data(new_data)

    await update.message.reply_text(f"🗑️ Đã xoá ID {delete_id}")

# ===== ADD HANDLERS =====
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("save", save_cmd))
bot_app.add_handler(CommandHandler("list", list_cmd))
bot_app.add_handler(CommandHandler("search", search_cmd))
bot_app.add_handler(CommandHandler("delete", delete_cmd))

# ===== WEBHOOK =====
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.update_queue.put_nowait(update)
    return "ok"

# route test
@app.route("/")
def index():
    return "Bot is running"

# ===== RUN =====
if __name__ == "__main__":
    asyncio.run(bot_app.initialize())
    asyncio.run(bot_app.start())

    port = int(os.environ.get("PORT", 10000))
    print("🔥 Bot webhook đang chạy...")
    app.run(host="0.0.0.0", port=port)
