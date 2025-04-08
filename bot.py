import telebot
import requests

# TOKEN BotFather
BOT_TOKEN = "YOUR_BOT_TOKEN"  
bot = telebot.TeleBot(BOT_TOKEN)

# API ExchangeRatesAPI
API_KEY = "YOUR_API_KEY" 
BASE_URL = "https://api.exchangeratesapi.io/v1/latest"

user_data = {}

# /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hi! I'm a currency exchange bot — with me, you'll always know the current exchange rate. To get started, please enter the source currency (e.g., USD): ")
    user_data[message.chat.id] = {"step": 1}


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        bot.reply_to(message, "Press /start to begin!")
        return

    step = user_data[chat_id]["step"]

    if step == 1:
        user_data[chat_id]["from_currency"] = message.text.upper()
        bot.reply_to(message, "Enter the target currency (e.g., EUR): ")
        user_data[chat_id]["step"] = 2

    elif step == 2:
        user_data[chat_id]["to_currency"] = message.text.upper()
        bot.reply_to(message, "Enter your amount: ")
        user_data[chat_id]["step"] = 3

    elif step == 3:
        try:
            amount = float(message.text)
            from_currency = user_data[chat_id]["from_currency"]
            to_currency = user_data[chat_id]["to_currency"]

            # Запрос к API
            response = requests.get(f"{BASE_URL}?access_key={API_KEY}&base={from_currency}&symbols={to_currency}")
            data = response.json()

            if not data.get("success"):
                bot.reply_to(message, "Error: invalid currency or API issue.")
                return

            rate = data["rates"][to_currency]
            result = amount * rate

            bot.reply_to(message, f"{amount} {from_currency} = {result:.2f} {to_currency}\nКурс: 1 {from_currency} = {rate:.4f} {to_currency}")
            del user_data[chat_id]  

        except ValueError:
            bot.reply_to(message, "Enter a valid number!")
        except KeyError:
            bot.reply_to(message, "Error: check the currency code!")
        except Exception as e:
            bot.reply_to(message, f"Error: {str(e)}")

# RUN
bot.polling()