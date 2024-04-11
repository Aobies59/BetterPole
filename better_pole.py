import telebot
from telebot import custom_filters
import json
import random
from datetime import datetime, timedelta
import schedule
import threading
import time

pole_open = False
initial_pole_day = {"pole_user": "", "pole_done": False, "subpole_user": "", "subpole_done": False, "bronce_user": "", "bronce_done": False}

try:
    with open('.token') as f:
        token = f.read()
except:
    print("Expected .token file with Telegram API token in the current directory")

try:
    with open('score.json') as f:
        json.load(f)
except:
    with open("score.json", "w") as f:
        f.write("{}")

def get_data(chat_id):
    with open('pole_day.json') as f:
        json_dict = json.load(f)
    if str(chat_id) not in list(json_dict.keys()):
        json_dict[str(chat_id)] = initial_pole_day
        with open('pole_day.json', 'w') as f:
            json.dump(json_dict, f, indent=4)
    return json_dict[str(chat_id)]

try:
    with open('pole_day.json') as f:
        pole_day = json.load(f)
except:
    with open("pole_day.json", "w") as f:
        f.write("{}")

def update_score(chat_id, user, username, pole_type):
    with open("score.json", "r") as f:
        score_data = json.load(f)
    score = score_data[str(chat_id)]
    user = str(user)
    if user not in list(score.keys()):
        score[user] = {"username": username, "score": 0}

    if pole_type == "pole":
        score[user]["score"] += 3
    elif pole_type == "subpole":
        score[user]["score"] += 1
    elif pole_type == "bronce":
        score[user]["score"] += 0.5
    else:
        print(f"Wrong pole type: {pole_type}")
    score_data[str(chat_id)] = score
    with open("score.json", "w") as f:
        json.dump(score_data, f, indent=4)

def update_data(chat_id, data):
    with open('pole_day.json') as f:
        json_dict = json.load(f)
    json_dict[str(chat_id)] = data
    with open('pole_day.json', 'w') as f:
        json.dump(json_dict, f, indent=4)

def update_json(dictionary):
    with open('pole_day.json', 'w') as f:
                f.write(json.dumps(dictionary, indent=4))

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
    with open("score.json", "r") as f:
        score = json.load(f)
    if str(message.chat.id) in list(score.keys()):
        bot.send_message(message.chat.id, "El bot ya está ejecutándose en este chat")
    else:
        score[message.chat.id] = {}
        with open("score.json", "w") as f:
            json.dump(score, f, indent=4)
        bot.send_message(message.chat.id, "Pole bot iniciado en este chat!")

@bot.message_handler(commands=["info"])
def info(message):
    bot.send_message(message.chat.id, \
    "Pole bot por @Aobies59\n \
Funcionamiento: Todos los días, entre las 20:00 y 23:59, avisará de que faltan cinco minutos. Cinco minutos después, se activará la pole.\n \
Para reclamar la pole, debes escribir 'pole', 'subpole' o 'bronce'. Pole son 3 puntos, subpole 1 y bronce 0.5.")

@bot.message_handler(func=lambda message: message.text == "pole")
def react_to_pole(message):
    data = get_data(message.chat.id)
    global pole_open
    if pole_open and message.from_user.id != data["pole_user"] and not data["pole_done"]:
        data['pole_user'] = message.from_user.id
        data['pole_done'] = True
        update_data(message.chat.id, data)
        update_score(message.chat.id, message.from_user.id, message.from_user.username, "pole")
        bot.reply_to(message, f"El usuario {message.from_user.username} ha conseguido la pole")
    elif pole_open and data["pole_done"] and message.from_user.id != data["pole_user"]:
        bot.reply_to(message, "Casi...")
    elif pole_open and data["pole_done"]:
        bot.reply_to(message, "Ya la tienes, calma")
    elif not pole_open:
        bot.reply_to(message, "Aún no, crack")

@bot.message_handler(func=lambda message: message.text == "subpole")
def react_to_subpole(message):
    data = get_data(message.chat.id)
    global pole_open
    if pole_open and message.from_user.id != data['subpole_user'] and not data['subpole_done'] and message.from_user.id != data['pole_user'] and data["pole_done"]:
        data['subpole_user'] = message.from_user.id
        data['subpole_done'] = "True"
        update_data(message.chat.id, data)
        update_score(message.chat.id, message.from_user.id, message.from_user.username, "subpole")
        bot.reply_to(message, f"El usuario {message.from_user.username} ha conseguido la subpole")

@bot.message_handler(func=lambda message: message.text == "bronce")
def react_to_bronce(message):
    data = get_data(message.chat.id)
    global pole_open
    if pole_open and message.from_user.id != data['bronce_user'] and not data['bronce_done'] and message.from_user.id != data['subpole_user'] and \
    data['subpole_done'] and message.from_user.id != data['pole_user'] and data["pole_done"]: 
        data['bronce_user'] = message.from_user.id
        data['bronce_done'] = "True"
        update_data(message.chat.id, data)
        update_score(message.chat.id, message.from_user.id, message.from_user.username, "bronce")
        bot.reply_to(message, f"El usuario {message.from_user.username} ha conseguido el bronce")

@bot.message_handler(commands=["score"])
def print_score(message):
    with open('score.json') as f:
        score = json.load(f)[str(message.chat.id)]
    if score == {}:
        bot.reply_to(message, "Nadie ha conseguido la pole aún")
    else:
        message_string = ""
        for item in score:
            message_string += f"{score[item]['username']}: {score[item]['score']}\n"
        bot.reply_to(message, message_string)

def send_reminder(set_time = None):
    global pole_open
    pole_open = False
    with open('pole_day.json', 'w') as f:
        json_content = {}
        with open("score.json", "r") as score:
            score = json.load(score)
        for i in score.keys():
            json_content[i] = initial_pole_day
        json.dump(json_content, f, indent=4)


    if not set_time:
        # generate a random hour between 8pm and 12am
        hour = random.randint(20, 23)
        minute = random.randint(0, 59)
         # schedule the "five minutes left" message
        target_time = datetime.now() + timedelta(hours=hour, minutes=minute)
    else:
        hour = set_time[0]
        minute = set_time[1]
        target_time = datetime(datetime.now().year, datetime.now().month, datetime.now().day, hour, minute)

    print(target_time)

    def send_five_minutes_left():
        with open("score.json", "r") as f:
            score = json.load(f)
        for i in score.keys():
            bot.send_message(i, "5 minutos para la pole...")

    def send_done():
        with open("score.json", "r") as f:
            score = json.load(f)
        for i in score.keys():
            bot.send_message(i, "La pole está activa!")
        global pole_open

    delay = (target_time - datetime.now()).total_seconds()

    timer = threading.Timer(delay, send_five_minutes_left)
    timer.start()

    timer = threading.Timer(delay + 300, send_done)
    timer.start()
        
schedule.every().day.at("00:00", "Europe/Madrid").do(send_reminder)
pole_open = True

send_reminder([20,00])  # the first time it will run at 20:00

def schedule_functionality():
    while True:
        schedule.run_pending()
        time.sleep(1)

schedule_thread = threading.Thread(target=schedule_functionality)
schedule_thread.start()

print("Started functionality!")

bot.infinity_polling()


