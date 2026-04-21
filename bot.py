# 🔥 PERFECT FIXED PANDA BOT (ALL WORKING) 😈💎

import telebot, instaloader, time, os, pyotp, threading, json
from telebot import types
from concurrent.futures import ThreadPoolExecutor

ADMIN_ID = 2019654506
DB_FILE = "users.json"
LOG_FILE = "success_log.json"

# ===== USER DB =====
def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(list(users), f)

all_users = load_users()

# ===== LOG =====
def load_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return []

def save_logs():
    with open(LOG_FILE, "w") as f:
        json.dump(success_logs, f)

success_logs = load_logs()

bot = telebot.TeleBot("8793208985:AAGLTtfmUwodJF2gQcYVERk1Vd9KDBl4a-0")
bot.remove_webhook()

user_sessions = {}

# ===== START =====
@bot.message_handler(commands=['start'])
def start_cmd(message):
    all_users.add(message.chat.id)
    save_users(all_users)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("পান্ডা এখন বাঁশ খাবে", "❌ CANCEL")

    bot.send_message(message.chat.id, "🔱 PANDA MODE ON 😈", reply_markup=markup)

# ===== ADMIN =====
@bot.message_handler(commands=['admin21'])
def admin_panel(message):
    if message.chat.id != ADMIN_ID:
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📢 Broadcast", "👥 Users", "⏱ Last 10h Stats")

    bot.send_message(message.chat.id, "🔐 ADMIN PANEL 💎", reply_markup=markup)

# ===== ADMIN BUTTONS =====
@bot.message_handler(func=lambda m: m.text == "👥 Users")
def users_count(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, f"👥 Total Users: {len(all_users)}")

@bot.message_handler(func=lambda m: m.text == "📢 Broadcast")
def ask_broadcast(message):
    if message.chat.id != ADMIN_ID:
        return

    msg = bot.send_message(message.chat.id, "📢 Send message:")
    bot.register_next_step_handler(msg, send_all)

def send_all(message):
    for user in all_users:
        try:
            bot.send_message(user, f"📢 ADMIN:\n\n{message.text}")
        except:
            pass

    bot.send_message(message.chat.id, "✅ Broadcast Done")

@bot.message_handler(func=lambda m: m.text == "⏱ Last 10h Stats")
def last_10h(message):
    if message.chat.id != ADMIN_ID:
        return

    now = time.time()
    count = sum(1 for t in success_logs if now - t <= 36000)

    bot.send_message(message.chat.id, f"📊 Last 10 Hours Success:\n\n✅ Total: {count}")

# ===== CANCEL =====
@bot.message_handler(func=lambda m: m.text == "❌ CANCEL")
def cancel(message):
    user_sessions.pop(message.chat.id, None)
    bot.send_message(message.chat.id, "🚫 Cancelled")

# ===== FLOW =====
@bot.message_handler(func=lambda m: m.text == "পান্ডা এখন বাঁশ খাবে")
def step1(message):
    chat_id = message.chat.id
    user_sessions[chat_id] = {'results': []}

    msg = bot.send_message(chat_id, "👤 USER LIST:")
    bot.register_next_step_handler(msg, step2)

def step2(message):
    chat_id = message.chat.id
    user_sessions[chat_id]['u_list'] = message.text.splitlines()

    msg = bot.send_message(chat_id, "🔑 PASSWORD:")
    bot.register_next_step_handler(msg, step3)

def step3(message):
    chat_id = message.chat.id
    user_sessions[chat_id]['pass'] = message.text

    msg = bot.send_message(chat_id, "🔐 2FA KEY:")
    bot.register_next_step_handler(msg, final_step)

# ===== LOGIN =====
def login_worker(chat_id, u, p, k):
    if chat_id not in user_sessions:
        return

    L = instaloader.Instaloader(quiet=True)

    try:
        L.login(u, p)
        save_success(chat_id, L, u, p)
    except:
        try:
            totp = pyotp.TOTP(k.replace(" ", ""))
            L.two_factor_login(totp.now())
            save_success(chat_id, L, u, p)
        except:
            bot.send_message(chat_id, f"❌ FAILED: {u}")

def save_success(chat_id, L, u, p):
    cookies = L.context._session.cookies.get_dict()
    ck = "; ".join([f"{k}={v}" for k,v in cookies.items()])

    user_sessions[chat_id]['results'].append(f"{u} | {p} | {ck}")
    success_logs.append(time.time())
    save_logs()

    bot.send_message(chat_id, f"✅ SUCCESS: {u}")

def final_step(message):
    chat_id = message.chat.id
    keys = message.text.splitlines()
    u_list = user_sessions[chat_id]['u_list']
    p = user_sessions[chat_id]['pass']

    bot.send_message(chat_id, "⏳ Processing...")

    executor = ThreadPoolExecutor(max_workers=30)
    for i in range(len(u_list)):
        executor.submit(login_worker, chat_id, u_list[i], p, keys[i])

    def finalize():
        executor.shutdown(wait=True)
        results = user_sessions[chat_id]['results']

        if results:
            filename = f"MAXVIP_{chat_id}.txt"

            with open(filename, "w") as f:
                f.write(" \n\n")
                f.write("\n".join(results))

            with open(filename, "rb") as f:
                bot.send_document(chat_id, f)

            os.remove(filename)
        else:
            bot.send_message(chat_id, "❌ No results")

        user_sessions.pop(chat_id, None)

    threading.Thread(target=finalize).start()

print("🔥 BOT RUNNING PERFECTLY...")
bot.infinity_polling()
