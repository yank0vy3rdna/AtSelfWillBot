import telebot
import os
from latex.build import build_pdf
from telebot import apihelper
import settings

apihelper.proxy = {'https': settings.credentials['proxy']}
bot = telebot.TeleBot(settings.credentials['api-key'])
user_dict = {}
texTemplate = open('atselfwill.tex').read()


class User:
    def __init__(self, name):
        self.name = name
        self.group = None


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    msg = bot.reply_to(message, """\
ПСЖ бот by yank0vy3rdna
Привет,
сейчас я помогу тебе числануться
Для начала назови свое имя(ФИО в родительном падеже)?
""")
    bot.register_next_step_handler(msg, process_name_step)


def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = User(name)
        user_dict[chat_id] = user
        msg = bot.reply_to(message, 'Напиши ка теперь свою группу')
        bot.register_next_step_handler(msg, process_age_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_age_step(message):
    try:
        chat_id = message.chat.id
        age = message.text
        user = user_dict[chat_id]
        user.group = age
        fio = user.name.split(' ')
        f = fio[0]
        i = fio[1]
        o = fio[2]
        fio = f + ' ' + i + ' ' + o
        fio = fio.title()
        bot.send_message(chat_id, 'Обработка начата, и обратного пути нет..')
        try:
            current_dir = os.path.abspath(os.path.dirname(__file__))
            pdf = build_pdf(texTemplate.replace('@GROUP@', user.group).replace('@FIO@', fio),
                            texinputs=[current_dir, ''])
            pdf.save_to('ПСЖ.pdf')
            bot.send_message(chat_id, 'Поздравляю, ' + user.name.split(' ')[1] +
                             ', ваш бланк ПСЖ заполнен и скоро будет доставлен')
            doc = open('ПСЖ.pdf', 'rb')
            bot.send_document(chat_id, doc)
            print(user_dict)
        except Exception as e:
            # print(e)
            bot.send_message(chat_id, 'Поздравляю, ' + user.name.split(' ')[1] + ', ваш бланк ПСЖ послал тебя нахуй')
    except Exception as e:
        bot.reply_to(message, 'oooops')
        print(e)


bot.enable_save_next_step_handlers(delay=2)

bot.load_next_step_handlers()

bot.polling()