#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove,KeyboardButton, ParseMode, Bot, Chat, MessageEntity, Message,
                      InputMediaPhoto, Update, InputMediaDocument, LabeledPrice)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler, PicklePersistence, CallbackContext, PreCheckoutQueryHandler)
from telegram.utils import helpers
from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError)
from telegram.ext.dispatcher import run_async
import telegram.bot
from telegram.ext import messagequeue as mq
from telegram.utils.request import Request
import logging
import random
import pymysql.cursors
import sys
import json
import base64
import time
import re
from threading import Thread

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# преобразование словаря настроек в класс с аттрибутами
class Config(object):
    def __init__(self, initial_data):
        for key in initial_data:
            setattr(self, key, initial_data[key])

# Класс для работы с БД mysql
class Db(object):
    def __init__(self, dbserver, dbuser, dbpasswd, database):
        self.dbserver = dbserver
        self.dbuser = dbuser
        self.dbpasswd = dbpasswd
        self.database = database

    # чтение одной записи БД
    def query_one(self, sql):
        connection = pymysql.connect(host=self.dbserver, user=self.dbuser,
                                     password=self.dbpasswd, db=self.database, autocommit=True,
                                     charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                if "insert" in sql.lower():
                    reply = cursor.lastrowid
                else:
                    reply = cursor.fetchone()
        finally:
            connection.close()
        return reply

    # чтение нескольких записей БД
    def query_all(self, sql):
        connection = pymysql.connect(host=self.dbserver, user=self.dbuser,
                                     password=self.dbpasswd, db=self.database, autocommit=True,
                                     charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                reply = cursor.fetchall()
        finally:
            connection.close()
        return reply

    # проверка существования пользователя
    def user_exists(self, user_id):
        sql = f"SELECT user_id FROM users WHERE user_id={user_id}"
        data = self.query_one(sql)
        if data:
            return True
        else:
            return False

    # получение настроек бота
    def get_settings(self):
        sql = "SELECT * FROM settings WHERE id=1"
        data = self.query_one(sql)
        return data

    # получение настроек пользователя
    def get_user_data(self, user_id):
        sql = f"SELECT * FROM users WHERE user_id={user_id}"
        data = self.query_one(sql)
        return data


    def get_languages(self):
        sql = "SELECT lang, icon, title FROM channels ORDER BY id ASC"
        data = self.query_all(sql)
        return data


    # получение текстов на двух языках из БД
    def get_messages(self):
        result = dict()
        for lang in self.get_languages():
            try:
                sql = "SELECT msg FROM %s ORDER BY id ASC" % (lang['lang'])
                data = self.query_all(sql)
                result[lang['lang']] = [x['msg'] for x in self.query_all(sql)]
            except:
                pass
        return result

    def get_chats(self):
        sql = "SELECT chat_id FROM channels ORDER BY id ASC"
        data = [int(x['chat_id']) for x in self.query_all(sql)]
        return data


    # получение клавитур на двух языках из БД
    def get_keyboards(self):
        sql = """SELECT kbd_id, text, lang FROM (
                 SELECT * FROM keyboards ORDER BY kbd_id ASC) AS nested
                 ORDER BY id ASC"""
        data = self.query_all(sql)
        result = dict()
        for lang in self.get_languages():
            result[lang['lang']] = list()
            new_data = [x for x in data if x['lang'] == lang['lang']]
            ids = list(set([x['kbd_id'] for x in new_data]))
            for item in ids:
                result[lang['lang']].append([x['text'] for x in new_data if x['kbd_id']==item])
        for x in list(result.keys()):
            if not result[x]:
                del result[x]
        return result


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())


# выводится по команде /start или при смене языка в настройках
def start(update: Update, context: CallbackContext):
    if update.message.chat.id != update.message.from_user.id:
        return
    user_id = update.message.from_user.id
    if db.user_exists(user_id):
        context.user_data[user_id] = db.get_user_data(user_id)
        reply_keyboard = [[
                            config.keyboards[context.user_data[user_id]['lang']][4][0],
                            config.keyboards[context.user_data[user_id]['lang']][4][1]
                         ]]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
        msg = config.texts[context.user_data[user_id]['lang']][0] % (update.message.from_user.first_name)
        context.bot.send_message(chat_id=user_id, text=msg,
                                 reply_markup=reply_markup)
        return ConversationHandler.END
    else:
        context.user_data[user_id] = dict()
        keyboard = list()
        for x in db.get_languages():
            if x['lang'] in config.texts.keys():
                keyboard.append([InlineKeyboardButton("%s %s" % (x['icon'], x['title']), callback_data=x['lang'])])
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=user_id, text="Select a language:", reply_markup=reply_markup)
        return LANG


# выбор языка при начальной регистрации или валюты при смене в настройках
def set_lang(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    context.user_data[user_id]['lang'] = query.data
    context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    keyboard = [[InlineKeyboardButton(config.keyboards[context.user_data[user_id]['lang']][0][0],
                                      callback_data='start')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = config.texts[context.user_data[user_id]['lang']][0] % (query.from_user.first_name)
    context.bot.send_message(chat_id=user_id, text=msg,
                             reply_markup=reply_markup)
    return START


def show_terms(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    msg = config.texts[context.user_data[user_id]['lang']][1] % (query.from_user.first_name, config.terms)
    keyboard = [[InlineKeyboardButton(config.keyboards[context.user_data[user_id]['lang']][1][0],
                                      callback_data='accept')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=user_id, text=msg, reply_markup=reply_markup)
    return TERMS


def accept_terms(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    keyboard = [[InlineKeyboardButton(config.keyboards[context.user_data[user_id]['lang']][2][0],
                                      callback_data='continue'),
                 InlineKeyboardButton(config.keyboards[context.user_data[user_id]['lang']][2][1],
                                      callback_data='terms'),
                ]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=user_id, text=config.texts[context.user_data[user_id]['lang']][2],
                             reply_markup=reply_markup)
    return CONTINUE


def set_wallet(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    msg = config.texts[context.user_data[user_id]['lang']][3] % (query.from_user.first_name)
    context.bot.send_message(chat_id=user_id, text=msg, disable_web_page_preview=True)
    return WALLET


def register(update: Update, context: CallbackContext):
    if update.message.chat.id != update.message.from_user.id:
        return
    user_id = update.message.from_user.id
    pattern = re.compile('^T[a-zA-Z0-9]{33}$')
    if not re.match(pattern, update.message.text):
        context.bot.send_message(chat_id=user_id, text=config.texts[context.user_data[user_id]['lang']][9])
        return WALLET

    sql = """INSERT INTO users (user_id, username, wallet, lang, firstname)
             VALUES (%s, '%s','%s','%s','%s')""" % (user_id,
                                               update.message.from_user.username,
                                               update.message.text,
                                               context.user_data[user_id]['lang'],
                                               update.message.from_user.first_name
                                               )
    db.query_one(sql)
    keyboard = [[InlineKeyboardButton(config.keyboards[context.user_data[user_id]['lang']][3][0],
                                      callback_data='deposit')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=user_id, text=config.texts[context.user_data[user_id]['lang']][4],
                             reply_markup=reply_markup)
    return ConversationHandler.END


def deposit(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    context.bot.send_message(chat_id=user_id, text=config.texts[context.user_data[user_id]['lang']][5])

    reply_keyboard = [[
                      config.keyboards[context.user_data[user_id]['lang']][4][0],
                      config.keyboards[context.user_data[user_id]['lang']][4][1]
                     ]]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
    context.bot.send_message(chat_id=user_id, text="<b>%s</b>" % (config.wallet) ,parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    sql = "INSERT INTO payments (user_id, created_at) VALUES (%s, %s)" % (user_id, int(time.time()))
    db.query_one(sql)


def balance(update: Update, context: CallbackContext):
    if update.message.chat.id != update.message.from_user.id:
        return
    user_id = update.message.from_user.id
    context.user_data[user_id] = db.get_user_data(user_id)
    msg = config.texts[context.user_data[user_id]['lang']][8] % (context.user_data[user_id]['balance'])
    keyboard = [[InlineKeyboardButton(config.keyboards[context.user_data[user_id]['lang']][3][0],
                                      callback_data='deposit')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=user_id, text=msg, reply_markup=reply_markup)


def info(update: Update, context: CallbackContext):
    if update.message.chat.id != update.message.from_user.id:
        return
    user_id = update.message.from_user.id
    context.user_data[user_id] = db.get_user_data(user_id)
    keyboard = [[
                    InlineKeyboardButton(config.keyboards[context.user_data[user_id]['lang']][5][0],
                                            url=config.terms),
                    InlineKeyboardButton(config.keyboards[context.user_data[user_id]['lang']][5][1],
                                            url='https://t.me/%s' % (config.support)),
                ]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=user_id, text=config.texts[context.user_data[user_id]['lang']][10], reply_markup=reply_markup)


def chat_mode(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    context.user_data[user_id] = db.get_user_data(user_id)
    if update.message.from_user.username not in config.ADMINS:
        return
    if chat_id not in config.chats:
        return

    if update.message.text == "/on":
        sql = "UPDATE channels SET status=1 WHERE chat_id='%s'" % (str(chat_id))
        msg = config.texts[context.user_data[user_id]['lang']][11]
    elif update.message.text == "/off":
        sql = "UPDATE channels SET status=0 WHERE chat_id='%s'" % (str(chat_id))
        msg = config.texts[context.user_data[user_id]['lang']][12]
    db.query_one(sql)
    context.bot.send_message(chat_id=user_id, text=msg)


def user_post(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    if chat_id not in config.chats:
        return
    if update.message.from_user.username in config.ADMINS:
        return
    user_id = update.message.from_user.id
    msg_id = update.message.message_id
    context.user_data[user_id] = db.get_user_data(user_id)
    if context.user_data[user_id]['balance'] < config.amount:
        context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        context.bot.send_message(chat_id=user_id, text=config.texts[context.user_data[user_id]['lang']][13])
    else:
        now = int(time.time())
        sql = "UPDATE users SET last_active = %s WHERE user_id=%s" % (now,user_id)
        db.query_one(sql)


def admin_reply(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    if chat_id not in config.chats:
        return
    if update.message.from_user.username not in config.ADMINS:
        context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        return
    user_id = update.message.reply_to_message.from_user.id
    context.user_data[user_id] = db.get_user_data(user_id)
    if context.user_data[user_id]['balance'] < config.amount:
        context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        return
    sql = "UPDATE users SET balance=balance-%s WHERE user_id=%s" % (config.amount, user_id)
    db.query_one(sql)
    if context.user_data[user_id]['balance'] - config.amount < config.amount:
        context.bot.send_message(chat_id=user_id, text=config.texts[context.user_data[user_id]['lang']][14] % (config.amount))


def added_member(update: Update, context: CallbackContext):
    now = int(time.time())
    new_members = update.message.new_chat_members
    for member in new_members:
        user_id = member.id
        sql = "UPDATE users SET last_active = %s WHERE user_id = %s" % (now, user_id)
        db.query_one(sql)


if __name__ == '__main__':

    LANG, START, TERMS, CONTINUE, WALLET  = range(5)

    with open('config.json', encoding='utf-8') as json_file:
        data = json.load(json_file)

    db = Db(data['DBSERVER'], data['DBUSER'], data['DBPASSWD'], data['DATABASE'])
    bot_settings = db.get_settings()
    for k in bot_settings.keys():
        data[k] = bot_settings[k]
    data['texts'] = db.get_messages()
    data['keyboards'] = db.get_keyboards()
    data['chats'] = db.get_chats()
    config = Config(data)



    lang_pattern = "^(" + '|'.join(list(config.texts.keys())) + ")$"

    updater = Updater(token=config.token, use_context=True)

    start_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states= {
            LANG: [CallbackQueryHandler(set_lang, pattern=lang_pattern)],
            START: [CallbackQueryHandler(show_terms, pattern="start")],
            TERMS: [CallbackQueryHandler(accept_terms, pattern="accept")],
            CONTINUE: [CallbackQueryHandler(show_terms, pattern="terms"),
                       CallbackQueryHandler(set_wallet, pattern="continue")],
            WALLET: [MessageHandler(Filters.text, register)]
        },

        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    balance_pattern = "^(" + '|'.join([config.keyboards[x][4][0] for x in config.keyboards.keys()]) + ")$"
    info_pattern = "^(" + '|'.join([config.keyboards[x][4][1] for x in config.keyboards.keys()]) + ")$"

    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(CallbackQueryHandler(deposit, pattern="deposit"))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(balance_pattern), balance))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(info_pattern), info))
    updater.dispatcher.add_handler(CommandHandler('on', chat_mode))
    updater.dispatcher.add_handler(CommandHandler('off', chat_mode))
    updater.dispatcher.add_handler(MessageHandler(Filters.reply, admin_reply))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, user_post))
    updater.dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, added_member))
    updater.start_polling()
    updater.idle()