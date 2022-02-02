import random
import telebot
import sqlite3

from telebot.types import ReplyKeyboardRemove

bot = telebot.TeleBot("")

#base
conn = sqlite3.connect("killer.db", check_same_thread=False)
curs = conn.cursor()
curs.execute("CREATE TABLE IF NOT EXISTS pups (id INTEGER, name TEXT)")
curs.execute("CREATE TABLE IF NOT EXISTS queue (num INTEGER)")
conn.commit()
#base

bot_logger = telebot.TeleBot('')
def log(message, text_comment):
    bot_logger.send_message(307518206,f'#Killer2020 получил сообщение!\n user: @{message.from_user.username}\n name: {message.from_user.first_name} {message.from_user.last_name}\n text: {message.text} \n content_type: {message.content_type} \n id: {message.chat.id} \n Comment: {text_comment}', disable_notification=True)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    log(message,'подъезъдъ')
    bot.send_message(message.chat.id,'Привет. Пароль? 🕵️')

@bot.message_handler(regexp=r"(?i:репер френе)")
def truepass(message):
    curs.execute(f'select * from pups where id={message.chat.id}')
    if curs.fetchone():
        
        keyboard=telebot.types.ReplyKeyboardMarkup()
        keyboard.add('да','нет')
        bot.send_message(message.chat.id,'Ты уже записан!! Хочешь поменять имя?', reply_markup=keyboard)
        
        bot.register_next_step_handler(message,want_to_edit)

    else:
        bot.send_message(message.chat.id,'Отлично, теперь отправь мне свое имя. Именно так я представлю тебя твоему убийце 😈')
        bot.register_next_step_handler(message,name_step)


def want_to_edit(message):
    if message.text=='да':
        bot.send_message(message.chat.id,'Ah shit, here we go again. \nВведи свое имя:',reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message,name_step_edit)
    else:
        bot.send_message(message.chat.id,'ok', reply_markup=ReplyKeyboardRemove())
    
def name_step_edit(message):
    name=message.text
    keyboard=telebot.types.ReplyKeyboardMarkup()
    keyboard.add('🤗','👋')
    bot.send_message(message.chat.id,'Любишь обнимашки?', reply_markup=keyboard)
    bot.register_next_step_handler(message, lambda m: huggies_step_edit(m,name))

def huggies_step_edit(message, name):
    if not message.text in ['🤗','👋'] :
        bot.send_message(message.chat.id,'Не пон. Выбери смайл')
        bot.register_next_step_handler(message, lambda m: huggies_step_edit(m,name))
    else:
        log(message, "Переименовался))")
        bot.send_message(message.chat.id,'Принято. Не забывай про /killed.', reply_markup=ReplyKeyboardRemove())
        curs.execute(f'UPDATE pups SET name="{(name+" "+message.text)}" WHERE id={message.chat.id}')
        conn.commit()

        
def name_step(message):
    name=message.text
    keyboard=telebot.types.ReplyKeyboardMarkup()
    keyboard.add('🤗','👋')
    bot.send_message(message.chat.id,'Любишь обнимашки? Те, кто любит, в игре будут обозначаться смайликом 🤗, а те, кто нет - 👋', reply_markup=keyboard)
    bot.register_next_step_handler(message, lambda m: huggies_step(m,name))

def huggies_step(message, name):
    if not message.text in ['🤗','👋'] :
        bot.send_message(message.chat.id,'Не пон. Выбери смайл')
        bot.register_next_step_handler(message, lambda m: huggies_step(m,name))
    else:
        bot.send_message(message.chat.id,'Отлично, я тебя запомнил! Когда придет время, ты узнаешь свою жертву ;)\nP.S.: И да, отправь /killed когда тебя убьют.', reply_markup=ReplyKeyboardRemove())
        curs.execute(f'INSERT INTO pups VALUES({message.chat.id}, "{(name+" "+message.text)}")')
        conn.commit()


@bot.message_handler(commands=['clear_db'])
def start_game(message):
    if message.chat.id == 307518206:
        curs.execute('DELETE FROM queue;')
        curs.execute('DELETE FROM pups;')
        conn.commit()

@bot.message_handler(commands=['send_directly'])
def send_to_somebody(message):
    if message.chat.id == 307518206:
        msg = bot.send_message(message.chat.id,'Send id:')
        bot.register_next_step_handler(msg, id_tosmb_step)

def id_tosmb_step(message):
    msg = bot.send_message(message.chat.id,'Send message:')
    bot.register_next_step_handler(msg, lambda m: send_tosmb_step(m, message.text))

def send_tosmb_step(message,id):
    bot.send_message(id,message.text)

@bot.message_handler(commands=['send'])
def send_for_all(message):
    if message.chat.id == 307518206:
        bot.register_next_step_handler(message,send_step)
def send_step(message):
    send_text_to_all(message.text)

def send_text_to_all(text):
    curs.execute('SELECT id FROM pups')
    ids = curs.fetchall()
    for id in ids:
        bot.send_message(id[0],text, parse_mode="Markdown")


@bot.message_handler(commands=['start_game'])
def start_game(message):
    if message.chat.id == 307518206:
        curs.execute('DELETE FROM queue;')
        curs.execute('SELECT COUNT(*) FROM pups')
        queuelen = curs.fetchone()[0]
        queue = list(range(1, queuelen+1))
        print(queue)
        random.shuffle(queue)
        print(queue)
        for i in range(queuelen):
            curs.execute(f'INSERT INTO queue VALUES({queue[i]})')
            conn.commit()
            curs.execute(f'SELECT id FROM pups WHERE rowid={queue[i]}')
            id = curs.fetchone()[0]
            curs.execute(f'SELECT (name) FROM pups WHERE rowid={queue[(i+1)%queuelen]}')
            name = curs.fetchone()[0]
            bot.send_message(id,'Твоя первая цель: '+name)

def getnextinqueue(num):
    curs.execute(f'SELECT num FROM queue WHERE rowid>(select rowid from queue where num={num}) ORDER BY rowid ASC LIMIT 1')
    nex = curs.fetchone()
    if not nex:
        curs.execute(f'SELECT num FROM queue ORDER BY rowid ASC LIMIT 1')
        nex = curs.fetchone()
    return nex[0]

def getpreviousinqueue(num):
    curs.execute(f'SELECT num FROM queue WHERE rowid<(select rowid from queue where num={num}) ORDER BY rowid DESC LIMIT 1')
    prev = curs.fetchone()
    if not prev:
        curs.execute(f'SELECT num FROM queue ORDER BY rowid DESC LIMIT 1')
        prev=curs.fetchone()
    return prev[0]
    



@bot.message_handler(commands=['killed'])
def start_game(message):
    curs.execute(f'select rowid from pups WHERE id={message.chat.id}')
    numkilled=curs.fetchone()
    if numkilled:
        numkilled=numkilled[0]
    else:
        bot.send_message(message.chat.id, 'анн нет!')
        return
    
    curs.execute(f'select * from queue where num = {numkilled}')
    isintab=curs.fetchone()
    if not isintab:
        bot.send_message(message.chat.id, 'Врёш')
        return 0

    killernum=getpreviousinqueue(numkilled)
    vicntimnum=getnextinqueue(numkilled)
    log(message, f'vicnum: {vicntimnum}; numkilled: {numkilled}; killernum: {killernum}')
    curs.execute(f'DELETE FROM queue WHERE num={numkilled}')
    conn.commit()

    curs.execute(f'select Count(*) from queue')
    if curs.fetchone()[0]==2:
        curs.execute(f'select num from queue')
        num1=curs.fetchone()[0]
        num2=curs.fetchone()[0]
        curs.execute(f'select name from pups where rowid = {num1}')
        name1=curs.fetchone()[0][:-2]
        curs.execute(f'select name from pups where rowid = {num2}')
        name2=curs.fetchone()[0][:-2]
        send_text_to_all(f"Точно мистер и миссис Смит, совсем как Бонни и Клайд, подобно Ким Пять-с-плюсом и Рону Так-Себе, они, *{name1}* и *{name2}*, они победили! Поздравим их!")
        return 0

    curs.execute(f'SELECT (name) FROM pups WHERE rowid={vicntimnum}')
    name = curs.fetchone()[0]
    print(killernum)
    curs.execute(f'SELECT id from pups where rowid=?',[killernum])
    killerid=curs.fetchone()[0]
     
    if killernum==vicntimnum:
        bot.send_message(killerid, 'Убийца, мать твою! Ты победил!!')
    else:
        bot.send_message(killerid,'Congratulations! Твоя следующая цель: '+name)

    bot.send_message(message.chat.id, 'Царствие небесное!')

@bot.message_handler(func=lambda message:True)
def handle_message(message):
    log(message,'hmm')

try:
    bot.polling()
except Exception as e:
    bot_logger.send_message(307518206,f'#Killer2020 Капец, ошибка! \n{str(e)}', disable_notification=True)
    
