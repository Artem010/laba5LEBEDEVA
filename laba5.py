import telebot, requests, random
import xml.etree.ElementTree as ET

token = '5087558707:AAH7Xp-BNy65rpJfArEca1bxxDg9oZ0wbmg'
bot = telebot.TeleBot(token);
url = "https://cbr.ru/scripts/XML_daily.asp"

words = ['вышка', 'телеграм', 'боты', 'лабораторки', 'десятка']
userWord = {} #userID:[word, word_now]


@bot.message_handler(commands=['start', 'info', 'getallrates', 'getrate', 'game'])
def start_handler(message):
    if(message.text == '/start'):
        bot.send_message(message.chat.id, f'*{message.from_user.first_name}, приветcтвую в моем телеграм боте!*', parse_mode= "Markdown")
    if(message.text == '/info'):
        text = "Этот бот умеет: Приветствовать пользователя, отправлять информаицю о боте (/info) Парсить курсы валют ЦБ (/getallrates или /getrate ) Играть в слова (/game)"
        bot.send_message(message.chat.id, text, parse_mode= "Markdown")
    if(message.text == '/getallrates'):
        resp = requests.get(url)
        root = ET.fromstring(resp.content) # поулчаетм ValCurs
        listRates=''
        for row in root:
            children = list(row) # поулчаем информацию по данной валюты
            listRates += f"*{children[2].text} {children[3].text} ({children[1].text})*: {children[4].text}р\n" #формируем строку для каждой валюты
        bot.send_message(message.chat.id, listRates, parse_mode= "Markdown")
    if(message.text == '/getrate'):
        m = bot.send_message(message.chat.id, text='Введите код валюты:')
        bot.register_next_step_handler(m,getRate) #регистрируем след сообщение в функции getRate
    if(message.text == '/game'):
        userWord[message.from_user.id] = [random.choice(words), '']
        for char in userWord[message.from_user.id][0]:
            userWord[message.from_user.id][1] += '_'
        m = bot.send_message(message.chat.id, text=f'Слово *{userWord[message.from_user.id][1]}*\nВведите букву:', parse_mode= "Markdown")
        bot.register_next_step_handler(m,game)

def game(message):
    char = message.text.lower()
    if len(char) == 1:
        if char in userWord[message.from_user.id][0]:
            for i, ch in enumerate(userWord[message.from_user.id][0]): #проходим по каждому символу в загаданном слове i=index, ch=char
                if(char == ch):
                    userWord[message.from_user.id][1] = userWord[message.from_user.id][1][:i] + ch + userWord[message.from_user.id][1][i+1:] # _ _ _ => _ а _
    if(userWord[message.from_user.id][0] == userWord[message.from_user.id][1]): #проверяем отгдал ли пользователь слово
        bot.send_message(message.chat.id, text=f'Ура, вы отгадали слово "*{userWord[message.from_user.id][1]}"*', parse_mode= "Markdown")
    else:
        m = bot.send_message(message.chat.id, text=f'Слово *{userWord[message.from_user.id][1]}*\nВведите букву:', parse_mode= "Markdown")
        bot.register_next_step_handler(m,game)

def getRate(message):
    resp = requests.get(url) #отправляем гет запрос на данный урл
    root = ET.fromstring(resp.content) #получаем главный тэг
    otvet = ''
    msg = message.text.lower()
    for row in root:
        children = list(row)
        if children[1].text.lower() == msg:
            otvet = f"*{children[2].text} {children[3].text} ({children[1].text})*: {children[4].text}р"
            break
    if(len(otvet)>0):
        bot.send_message(message.chat.id, otvet, parse_mode= "Markdown")
    else:
        bot.send_message(message.chat.id, "Такой валюты нет! Попробуйте еще раз", parse_mode= "Markdown")


bot.polling(none_stop=True, interval=1);
