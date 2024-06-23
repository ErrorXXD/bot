import sqlite3
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Your Telegram Bot API token
bot_token = '7108764954:AAFbBqX-vGNsXkfz6Q20-3RPUFWccGA9Xkc'
bot_owner_id = '6181269269'  # Your Telegram user ID

# Database setup
conn = sqlite3.connect('redeem_bot.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS redeem_codes
             (code TEXT PRIMARY KEY, prize TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS redeemed_codes
             (username TEXT, code TEXT)''')
conn.commit()

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Welcome to the Redeem Code Bot!')

def createcode(update: Update, context: CallbackContext):
    if str(update.message.from_user.id) == bot_owner_id:
        try:
            code, prize = context.args
            with sqlite3.connect('redeem_bot.db') as conn:
                c = conn.cursor()
                c.execute("INSERT INTO redeem_codes (code, prize) VALUES (?, ?)", (code, prize))
                conn.commit()
            update.message.reply_text(f"Redeem code created: {code} for prize: {prize}")
        except ValueError:
            update.message.reply_text("Usage: /createcode CODE PRIZE")
    else:
        update.message.reply_text("Only the bot owner can create redeem codes.")

def redeem(update: Update, context: CallbackContext):
    try:
        code = context.args[0]
        with sqlite3.connect('redeem_bot.db') as conn:
            c = conn.cursor()
            c.execute("SELECT prize FROM redeem_codes WHERE code = ?", (code,))
            result = c.fetchone()
            if result:
                prize = result[0]
                username = update.message.from_user.username
                c.execute("INSERT INTO redeemed_codes (username, code) VALUES (?, ?)", (username, code))
                conn.commit()
                update.message.reply_text(f"Congratulations! You have redeemed the code for: {prize}")
            else:
                update.message.reply_text("Invalid redeem code.")
    except (ValueError, IndexError):
        update.message.reply_text("Usage: /redeem CODE")

def checkredeems(update: Update, context: CallbackContext):
    if str(update.message.from_user.id) == bot_owner_id:
        with sqlite3.connect('redeem_bot.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM redeemed_codes")
            logs = c.fetchall()
            log_text = "Redeemed Codes Log:\n"
            for log in logs:
                log_text += f"Username: {log[0]}, Code: {log[1]}\n"
            update.message.reply_text(log_text)
    else:
        update.message.reply_text("Only the bot owner can check redeem logs.")

def main():
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("createcode", createcode))
    dp.add_handler(CommandHandler("redeem", redeem))
    dp.add_handler(CommandHandler("checkredeems", checkredeems))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
