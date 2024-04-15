import telebot
from telebot import custom_filters
import json
import random
from datetime import datetime, timedelta
import schedule
import threading
import time
import os
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import operator
import sys

pole_open = False
initial_pole_day = {"pole_user": "", "pole_done": False, "subpole_user": "", "subpole_done": False, "bronce_user": "", "bronce_done": False}

print("Attempting to read token...")
try:
    with open('storage/.token') as f:
        token = f.read()
except:
    print("Expected .token file with Telegram API token in the current directory")
    exit(1)

if token == "":
    print("Expected .token file with Telegram API token in the current directory")
    exit(1)

try:
    with open('storage/score.json') as f:
        json.load(f)
except:
    with open("storage/score.json", "w") as f:
        f.write("{}")

def get_data(chat_id):
    with open('storage/pole_day.json') as f:
        json_dict = json.load(f)
    if str(chat_id) not in list(json_dict.keys()):
        json_dict[str(chat_id)] = initial_pole_day
        with open('storage/pole_day.json', 'w') as f:
            json.dump(json_dict, f, indent=4)
    return json_dict[str(chat_id)]


try:
    with open('storage/pole_day.json') as f:
        pole_day = json.load(f)
except:
    with open("storage/pole_day.json", "w") as f:
        f.write("{}")


def update_score(chat_id, user, username, pole_type):
    with open("storage/score.json", "r") as f:
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
    with open("storage/score.json", "w") as f:
        json.dump(score_data, f, indent=4)

def update_data(chat_id, data):
    with open('storage/pole_day.json') as f:
        json_dict = json.load(f)
    json_dict[str(chat_id)] = data
    with open('storage/pole_day.json', 'w') as f:
        json.dump(json_dict, f, indent=4)

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
    with open("storage/score.json", "r") as f:
        score = json.load(f)
    if str(message.chat.id) in list(score.keys()):
        bot.send_message(message.chat.id, "El bot ya está ejecutándose en este chat")
    else:
        score[message.chat.id] = {}
        with open("storage/score.json", "w") as f:
            json.dump(score, f, indent=4)
        bot.send_message(message.chat.id, "Pole bot iniciado en este chat!")

@bot.message_handler(commands=["info"])
def info(message):
    bot.send_message(message.chat.id, \
    "Pole bot por @Aobies59\nFuncionamiento: Todos los días, entre las 20:00 y 23:59, avisará de que faltan cinco minutos. Cinco minutos después, se activará la pole.\nPara reclamar la pole, debes escribir 'pole', 'subpole' o 'bronce'. Pole son 3 puntos, subpole 1 y bronce 0.5.")

@bot.message_handler(func=lambda message: message.text.lower() == "pole")
def react_to_pole(message):
    with open('storage/score.json') as f:
        score_data = json.load(f)
    if str(message.chat.id) not in score_data:
        bot.reply_to(message, "El bot no está inicializado en este chat. Haz /start para inicializarlo")
        return
    data = get_data(message.chat.id)
    global pole_open
    if pole_open and message.from_user.id != data["pole_user"] and not data["pole_done"]:
        data['pole_user'] = message.from_user.id
        data['pole_done'] = True
        update_data(message.chat.id, data)
        if message.from_user.username:
            update_score(message.chat.id, message.from_user.id, message.from_user.username, "pole")
            bot.reply_to(message, f"El usuario {message.from_user.username} ha conseguido la pole")
        else:
            update_score(message.chat.id, message.from_user.id, message.from_user.first_name, "pole")
            bot.reply_to(message, f"El usuario {message.from_user.first_name} ha conseguido la pole")
    elif pole_open and data["pole_done"] and message.from_user.id != data["pole_user"]:
        bot.reply_to(message, "Casi...")
    elif pole_open and data["pole_done"]:
        bot.reply_to(message, "Ya la tienes, calma")
    elif not pole_open:
        bot.reply_to(message, "Aún no, crack")

@bot.message_handler(func=lambda message: message.text.lower() == "subpole")
def react_to_subpole(message):
    with open('storage/score.json') as f:
        score_data = json.load(f)
    if str(message.chat.id) not in score_data:
        bot.reply_to(message, "El bot no está inicializado en este chat. Haz /start para inicializarlo")
        return
    data = get_data(message.chat.id)
    global pole_open
    if pole_open and message.from_user.id != data['subpole_user'] and not data['subpole_done'] and message.from_user.id != data['pole_user'] and data["pole_done"]:
        data['subpole_user'] = message.from_user.id
        data['subpole_done'] = True
        update_data(message.chat.id, data)
        if message.from_user.username:
            update_score(message.chat.id, message.from_user.id, message.from_user.username, "subpole")
            bot.reply_to(message, f"El usuario {message.from_user.username} ha conseguido la subpole")
        else:
            update_score(message.chat.id, message.from_user.id, message.from_user.first_name, "subpole")
            bot.reply_to(message, f"El usuario {message.from_user.first_name} ha conseguido la subpole")

@bot.message_handler(func=lambda message: message.text.lower() == "bronce")
def react_to_bronce(message):
    with open('storage/score.json') as f:
        score_data = json.load(f)
    if str(message.chat.id) not in score_data:
        bot.reply_to(message, "El bot no está inicializado en este chat. Haz /start para inicializarlo")
        return
    data = get_data(message.chat.id)
    global pole_open
    if pole_open and message.from_user.id != data['bronce_user'] and not data['bronce_done'] and message.from_user.id != data['subpole_user'] and \
    data['subpole_done'] and message.from_user.id != data['pole_user'] and data["pole_done"]: 
        data['bronce_user'] = message.from_user.id
        data['bronce_done'] = True
        update_data(message.chat.id, data)
        if message.from_user.username:
            update_score(message.chat.id, message.from_user.id, message.from_user.username, "bronce")
            bot.reply_to(message, f"El usuario {message.from_user.username} ha conseguido el bronce")
        else:
            update_score(message.chat.id, message.from_user.id, message.from_user.first_name, "bronce")
            bot.reply_to(message, f"El usuario {message.from_user.first_name} ha conseguido el bronce")

@bot.message_handler(commands=["score"])
def print_score(message):
    try:
        with open('storage/score.json') as f:
            score_data = json.load(f)
    except:
        with open('storage/score.json', 'w') as f:
            json.dump({}, f)
            score_data = {}
    if str(message.chat.id) not in score_data:
        bot.reply_to(message, "El bot no está inicializado en este chat. Haz /start para inicializarlo")
        return
    score = score_data[str(message.chat.id)]

    score = dict(sorted(score.items(), key=lambda x: x[1]["score"], reverse=True))

    if score == {}:
        bot.reply_to(message, "Nadie ha conseguido la pole aún")
    else:
        message_string = ""
        for item in score:
            message_string += f"{score[item]['username']}: {score[item]['score']}\n"
        bot.reply_to(message, message_string)
   
@bot.message_handler(func=lambda message: "pilarica" in message.text.lower())
def reply_to_pilarica(message):
    bot.reply_to(message, "No me hables de esa puta")

@bot.message_handler(func=lambda message: message.text.lower() == "hola")
def reply_to_hola(message):
    bot.reply_to(message, "Que te calles la puta boca subnormal")

@bot.message_handler(func=lambda message: message.text.lower() == "pole canaria")
def pole_canaria(message):
    bot.reply_to(message, "Callate africano")

@bot.message_handler(func=lambda message: message.text.lower() == "pole andaluza")
def pole_canaria(message):
    bot.reply_to(message, "Gitano")

@bot.message_handler(func=lambda message: message.text.lower() == "chibi")
def chibi(message):
    chibi_images_folder = os.path.abspath("storage/chibi_images")
    chibi_images = [f for f in os.listdir(chibi_images_folder)]
    if not chibi_images:
        bot.reply_to(message, "Error: no tengo imágenes de chibi :(")
    random_chibi = random.choice(chibi_images)

    with open(os.path.join(chibi_images_folder, random_chibi), 'rb') as random_chibi_image:
        image_data = random_chibi_image.read()

    bot.send_photo(message.chat.id, image_data)

@bot.message_handler(func=lambda message: message.text == ":c")
def alexia(message):
    bot.reply_to(message, "Callate alexia")

@bot.message_handler(func=lambda message: message.text == ":(")
def sad_face(message):
    bot.reply_to(message, ":)")

@bot.message_handler(commands=["chibitext"])
def chibi_text(message):
    try:
        image = Image.open("storage/Chibi_meditativo.png")
    except:
        bot.reply_to(message, "Chibi meditativo no está disponible")
        return

    try:
        font = ImageFont.truetype("storage/sans.ttf", 20)
    except:
        bot.reply_to(message, "Chibi meditativo no está disponible")
        return

    draw = ImageDraw.Draw(image)

    max_line_length = 33
    words = message.text[11:].split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= max_line_length:
            current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "

    if current_line:
        lines.append(current_line)

    text = "\n".join(lines)

    # get text height to center text vertically
    ascent, descent = font.getmetrics()
    text_height = (ascent + descent) * len(lines)
    draw.multiline_text((10, (image.height - text_height) // 2), text, font=font, fill="white")

    image.save("storage/chibi_text.png")

    with open("storage/chibi_text.png", 'rb') as chibi_text:
        image_data = chibi_text.read()

    bot.send_photo(message.chat.id, image_data)

    os.remove("storage/chibi_text.png")

def schedule_functionality():
    def send_reminder(set_time = None):
        global pole_open
        pole_open = False
        with open('storage/pole_day.json', 'w') as f:
            json_content = {}
            with open("storage/score.json", "r") as score:
                score = json.load(score)
            for i in score.keys():
                json_content[i] = initial_pole_day
            json.dump(json_content, f, indent=4)


        if not set_time:
            # generate a random hour between 8pm and 12am
            hour = random.randint(20, 23)
            minute = random.randint(0, 59)
            # schedule the "five minutes left" message
            target_time = datetime.now().replace(hour=hour, minute=minute)
        else:
            hour = set_time[0]
            minute = set_time[1]
            target_time = datetime.now().replace(hour=hour, minute=minute)

        print(target_time)

        def send_five_minutes_left():
            with open("storage/score.json", "r") as f:
                score = json.load(f)
            for i in score.keys():
                bot.send_message(i, "5 minutos para la pole...")

        def send_done():
            with open("storage/score.json", "r") as f:
                score = json.load(f)
            for i in score.keys():
                bot.send_message(i, "La pole está activa!")
            global pole_open
            pole_open = True

        delay = (target_time - datetime.now()).total_seconds()

        timer = threading.Timer(delay, send_five_minutes_left)
        timer.start()

        if len(sys.argv) == 1:
            delay += 300
        else:
            delay += 1
        timer = threading.Timer(delay, send_done)
        timer.start()

    schedule.every().day.at("00:00", "Europe/Madrid").do(send_reminder)

    current_time = datetime.now()
    if len(sys.argv) == 1:
        if current_time.hour > 20:  # if after 20pm, send reminder at a random time of the day
            hour = random.randint(current_time.hour, 23)
            if hour == current_time.hour:
                minute = random.randint(current_time.minute, 59)
            elif hour == 23:
                minute = random.randint(0, 54)
            else:
                minute = random.randint(0, 59)
            send_reminder((hour, minute))
        else:
            send_reminder()
    else:
        send_reminder([current_time.hour, current_time.minute])
    

    while True:
        schedule.run_pending()
        time.sleep(1)

schedule_thread = threading.Thread(target=schedule_functionality)
schedule_thread.start()

print("Started functionality!")

bot.infinity_polling()
