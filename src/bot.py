from re import sub
from typing import Text
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
from telegram import Bot, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, conversationhandler
from telegram.utils.request import Request

import threading
from requests import Session
from bs4 import BeautifulSoup as bs
import json

import db_sql
import connect
import helper_funcs as funcs

#create token.py and input there token = "<your TOKEN>"
from config import token

START, CHOOSED, IDLE, CHOOSE = range(4)

conn, cursor = None, None

reply_keyboard = [
    ['Add me', 'Change login|password'],
    ['My scores', 'Receive notifications'],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

menu_keyboard = [["Menu"]]
menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True)

def start(update: Update, context: CallbackContext):

    update.message.reply_text(
        'It is bot for ORIOKS\n'
        'If you want to see your scores or receive notifications from ORIOKS press "Add Me"',
        reply_markup=markup,
    )
    return CHOOSE

def add_change_login_and_password(update: Update, context: CallbackContext):
    choose = "add" if update.message.text == "Add me" else "change"
    context.user_data['choice'] = choose
    update.message.reply_text(
        f"To {choose} your login and password please enter login:"
    )
    return CHOOSED

def add_change_log_pass_choosed(update: Update, context: CallbackContext):
    if "login" not in context.user_data:
        context.user_data["login"] = update.message.text
        update.message.reply_text("Now enter password:", reply_markup=menu_markup)
        return CHOOSED
    id =  update.message.from_user.id
    choose = context.user_data['choice']
    password =  update.message.text
    login = context.user_data["login"]
    if connect.check_login(login, password):
        db_sql.update_insert_user(id, login, password, cursor, choose, conn)
        update.message.reply_text(f"Successfully {choose}ed", reply_markup=menu_markup)
    else:
        update.message.reply_text("invalid login or password", reply_markup=menu_markup)
    context.user_data.clear()
    return ConversationHandler.END

def idle(update: Update, context: CallbackContext):
    reply = [['My scores', 'Receive notifications'], ["Change login|password"]]
    update.message.reply_text("What you want?",
        reply_markup=ReplyKeyboardMarkup(reply, one_time_keyboard=True))
    return CHOOSE

def my_scores(update: Update, context: CallbackContext):
    id = update.message.from_user.id
    login,password = db_sql.get_user(id, conn)
    if not login or not password:
        update.message.reply_text("You not in base, change or add login, password",
            reply_markup=menu_markup)
        return ConversationHandler.END
    scores = connect.request_scores(login,password)
    text = ""
    for subject in scores:
        sum = 0
        for cm in scores[subject]:
            sum += scores[subject][cm]
        text = subject + " : " + str(sum)
    update.message.reply_text(text,
            reply_markup=menu_markup)
    return ConversationHandler.END

def receive_notifications(update: Update, context: CallbackContext):
    reply = [['Yes'], ['No']]
    update.message.reply_text("Do you want to receive notifications about new scores and notifications from ORIOKS?",
        reply_markup=ReplyKeyboardMarkup(reply, one_time_keyboard=True))
    return CHOOSED

def receive_notifications_choose(update: Update, context: CallbackContext):
    choose = update.message.text
    id = update.message.from_user.id
    db_sql.receive_notifications(id, cursor, choose, conn)
    if choose == "Yes":
        text = "Notifications enabled"
    else: 
        text = "Notifications disabled"
    update.message.reply_text(text, reply_keyboard=menu_keyboard)
    context.user_data.clear()
    return ConversationHandler.END

def main():

    request = Request(con_pool_size=8)
    bot = Bot(token=token,request=request)
    updater = Updater(bot=bot)
    dummy_event = threading.Event()

    global conn
    global cursor
    conn, cursor = db_sql.sql_connect()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSE: [
                MessageHandler(Filters.regex('^(Add me|Change login\|password)$'), add_change_login_and_password),
                MessageHandler(Filters.regex('^Receive notifications$'), receive_notifications),
                MessageHandler(Filters.regex('^My scores$'), my_scores)
            ],
            CHOOSED: [
                # MessageHandler(Filters.regex('[0-9].{6,8}'), add_change_log_pass_choosed),
                MessageHandler(Filters.regex('.{3,50}'), add_change_log_pass_choosed),
                MessageHandler(Filters.regex('^(Yes|No)$'), receive_notifications_choose)
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('^(Menu)'), idle)],
    )

    updater.dispatcher.add_handler(conv_handler)
    updater.start_polling()
    # updater.idle()

    while(True):
        dummy_event.wait(timeout=60*60*2) # wait 2 hours #TODO do not send messages in night

        users = db_sql.get_all_users(conn)
        for user in users.tel_id:
            print(user)
            iscores,uscores = funcs.new_scores(user, conn)
            scores = {}
            for x in (iscores,uscores):
                scores.update(x)
            if scores != {}:#dammm...
                if iscores != {}:
                    db_sql.insert_data(user, iscores, cursor, conn)
                elif uscores != {}:
                    print(uscores)
                    db_sql.update_data(user, uscores, cursor, conn)
                bot.send_message(user, "You have some new e-balls!")
                for sub in scores:
                    text = ""
                    text += sub + "\n"
                    for cm in scores[sub]:
                        new_cm = cm if cm != "-" else "Экзамем"
                        text += new_cm + " : " + str(scores[sub][cm]) + "\n"
                    bot.send_message(user, text)

            login, password = db_sql.get_user(user, conn)
            try:
                notis = connect.check_notifications(login, password)
            except:
                continue
            if notis != []:
                    bot.send_message(user, "You have new notifications in ORIOKS!")
                    bot.send_message(user, notis)

if __name__ == '__main__':
    main()

