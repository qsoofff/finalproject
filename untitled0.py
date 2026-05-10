!pip install Telebot

!pip install sqlite3

!pip install datetime

import telebot
import sqlite3
from datetime import datetime

BOT_TOKEN = "enter your token here(do not remove quotation marks)"
ADMIN_ID = 

FAQ = {
    "как оформить заказ": "Выберите товар, нажмите 'В корзину', затем оформите заказ.",
    "как узнать статус заказа": "Войдите в аккаунт → раздел 'Мои заказы'.",
    "как отменить заказ": "Срочно напишите сюда, отменим до отправки.",
    "товар пришел поврежденным": "Пришлите фото сюда — поможем с возвратом.",
    "как связаться с техподдержкой": "Напишите в этот чат или по телефону на сайте.",
    "как узнать о доставке": "На странице оформления заказа на сайте."
}


def save_request(user_id, name, department, text):
    conn = sqlite3.connect("requests.db")
    conn.execute("""CREATE TABLE IF NOT EXISTS requests
                    (id INTEGER PRIMARY KEY, user_id INT, name TEXT,
                     department TEXT, text TEXT, date TEXT)""")
    conn.execute("INSERT INTO requests (user_id, name, department, text, date) VALUES (?,?,?,?,?)",
                 (user_id, name, department, text, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()


bot = telebot.TeleBot(BOT_TOKEN)


def main_keyboard():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Отдел продаж", " Отдел программистов")
    kb.row(" Частые вопросы")
    return kb

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "Добро пожаловать в поддержку!\n\nВыберите нужный раздел:",
                     reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: m.text == "Частые вопросы")
def faq(message):
    text = "ЧАСТЫЕ ВОПРОСЫ:\n\n"
    for q, a in FAQ.items():
        text += f"• {q}\n  → {a}\n\n"
    bot.send_message(message.chat.id, text[:4000])

@bot.message_handler(func=lambda m: m.text == "Отдел продаж")
def sales(message):
    save_request(message.from_user.id, message.from_user.first_name, "продажи", "ожидает вопрос")
    bot.send_message(message.chat.id, "Отдел продаж. Напишите ваш вопрос:")

@bot.message_handler(func=lambda m: m.text == "Отдел программистов")
def tech(message):
    save_request(message.from_user.id, message.from_user.first_name, "программисты", "ожидает вопрос")
    bot.send_message(message.chat.id, "Отдел программистов. Напишите ваш вопрос:")

@bot.message_handler(func=lambda m: True)
def save_question(message):
    if message.text.startswith("/"):
        return
    save_request(message.from_user.id, message.from_user.first_name, "общий", message.text)
    bot.send_message(message.chat.id, "Вопрос принят! Специалист ответит.\n/start - в меню")

@bot.message_handler(commands=['requests'])
def show_requests(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "Нет доступа")
        return

    conn = sqlite3.connect("requests.db")
    rows = conn.execute("SELECT id, name, department, text, date FROM requests ORDER BY id DESC LIMIT 10").fetchall()
    conn.close()

    if not rows:
        bot.reply_to(message, "Нет обращений")
        return

    out = "ПОСЛЕДНИЕ ОБРАЩЕНИЯ:\n\n"
    for r in rows:
        out += f"#{r[0]} | {r[1]} | {r[2]}\n{r[3][:50]}\n{r[4]}\n\n"
    bot.send_message(message.chat.id, out[:4000])

print("Бот запущен!")
bot.infinity_polling()
