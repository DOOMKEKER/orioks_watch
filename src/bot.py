from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
from telegram import Bot, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler
from telegram.utils.request import Request

import threading
from requests import Session
from bs4 import BeautifulSoup as bs
import json

import db_sql

#create token.py and input there token = "<your TOKEN>"
from config import token

START, CHOOSED, IDLE, CHOOSE = range(4)

conn, cursor = None

reply_keyboard = [
    ['Add me', 'Change login|password'],
    ['My scores', 'Receive notifications'],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

def start(update: Update, context: CallbackContext):

    update.message.reply_text(
        'It is bot for ORIOKS\n'
        'If you want to see your scores or receive notifications from ORIOKS press "Add Me"',
        reply_markup=markup,
    )
    return CHOOSE

def add_login_and_password(update: Update, context: CallbackContext):
    update.message.reply_text(
        "To add your login and password send message like this:"
        "login:<your_login>"
        "password:<your_password>"
    )
    return CHOOSED

def change_login_and_password(update: Update, context: CallbackContext):
    update.message.reply_text(
        "To change your login and password send message like this:"
        "login:<your_login>"
        "password:<your_password>"
    )
    print(update.message.text)
    return CHOOSED

def idle(update: Update, context: CallbackContext):
    reply_keyboard = [['My scores', 'Receive notifications'], ["Change login|password"]]
    update.message.reply_text(
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return CHOOSE

def my_score(update: Update, context: CallbackContext):
    id =  Update.message.from_user.id
    data = db_sql.get_scores(id, conn)
    update.message.reply_text(data.to_markdown())
    return IDLE

def receive_notifications(update: Update, context: CallbackContext):
    reply_keyboard = ['Yes', 'No']
    update.message.reply_text("Do you want to receive notifications about new scores and notifications from ORIOKS?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return CHOOSED

def receive_notifications_choose(update: Update, context: CallbackContext):
    choose = update.message.text
    id = update.from_user.id
    db_sql.receive_notifications(id, cursor, choose)
    return IDLE

def insert_update_data(update: Update, context: CallbackContext):
    pass

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
                MessageHandler(Filters.regex('^Add me$'), add_login_and_password),
                MessageHandler(Filters.regex('^Change login|password$'), change_login_and_password),
                MessageHandler(Filters.regex('^Receive notifications$'), change_login_and_password),
                MessageHandler(Filters.regex('^My scores$'), change_login_and_password)
            ],
            IDLE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Add me$')), idle
                )
            ],
            CHOOSED: [
                MessageHandler(Filters.regex('^login:$'), change_login_and_password),
                MessageHandler(Filters.regex('^(Yes|No)$'), receive_notifications_choose),
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('^(Add me)'), idle)],
    )

    updater.dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

    while(True):
        dummy_event.wait(timeout=60*60*2)

    return 0

if __name__ == '__main__':
    main()

