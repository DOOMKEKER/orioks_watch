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
        f"To {choose} your login and password send message like this:"
        "login:<your_login>"
        "password:<your_password>"
    )
    return CHOOSED

def add_change_login_and_password_choosed(update: Update, context: CallbackContext):
    id =  Update.message.from_user.id
    choose = context.user_data['choice']
    login, password = db_sql.get_user(id)
    db_sql.update_insert_user(id, login, password, cursor, choose)
    update.message.reply_text(f"Successfully {choose}ed", reply_keyboard=menu_markup)
    context.user_data.clear()
    return ConversationHandler.END

def idle(update: Update, context: CallbackContext):
    reply = [['My scores', 'Receive notifications'], ["Change login|password"]]
    update.message.reply_text(
        reply_markup=ReplyKeyboardMarkup(reply, one_time_keyboard=True))
    return CHOOSE

def my_scores(update: Update, context: CallbackContext):
    id = Update.message.from_user.id
    data = db_sql.get_scores(id, conn)#TODO not relevant data
    update.message.reply_text(data.to_markdown(),#TODO how it looks
            reply_keyboard=menu_keyboard)
    return ConversationHandler.END

def receive_notifications(update: Update, context: CallbackContext):
    reply = ['Yes', 'No']
    update.message.reply_text("Do you want to receive notifications about new scores and notifications from ORIOKS?",
        reply_markup=ReplyKeyboardMarkup(reply, one_time_keyboard=True))
    return CHOOSED

def receive_notifications_choose(update: Update, context: CallbackContext):
    choose = update.message.text
    id = update.from_user.id
    db_sql.receive_notifications(id, cursor, choose)
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
        entry_points=[CommandHandler('start', start), MessageHandler(Filters.regex("^Menu"),idle)],
        states={
            CHOOSE: [
                MessageHandler(Filters.regex('^(Add me|Change login\|password)$'), add_change_login_and_password),
                MessageHandler(Filters.regex('^Receive notifications$'), receive_notifications),
                MessageHandler(Filters.regex('^My scores$'), my_scores)
            ],
            CHOOSED: [
                MessageHandler(Filters.regex('(login:[0-9]\{7\}|password:.\{5,\})'), add_change_login_and_password_choosed),
                MessageHandler(Filters.regex('^(Yes|No)$'), receive_notifications_choose),
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('^(To menu)'), idle)],
    )

    updater.dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

    while(True):
        dummy_event.wait(timeout=60*60*2)

    return 0

if __name__ == '__main__':
    main()

