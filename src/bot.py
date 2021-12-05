from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters

from requests import Session
from bs4 import BeautifulSoup as bs
import json

from config import token

updater = Updater(token=token, use_context=True)

