#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import pymysql.cursors
import time
import logging
import json
import requests


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

period = 60 * 60


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


with open('config.json', encoding='utf-8') as json_file:
    data = json.load(json_file)

db = Db(data['DBSERVER'], data['DBUSER'], data['DBPASSWD'], data['DATABASE'])

settings = db.query_one("SELECT token, amount, inactivity FROM settings WHERE id=1")

msgs = dict()

chats = dict()

sql = "SELECT chat_id, lang FROM channels WHERE status=1"
for x in db.query_all(sql):
    chats[x['lang']] = x['chat_id']

while True:
    now = int(time.time())

    users = db.query_all("SELECT user_id, balance, lang FROM users WHERE status=1 AND %s - last_active > %s" % (now, settings['inactivity']))

    logger.info("%s inactive users found" % (len(users)))

    for u in users:
        if u['balance'] >= settings['amount']:
            sql = "UPDATE users SET balance=balance-%s WHERE user_id=%s" % (settings['amount'], u['user_id'])
            db.query_one(sql)
            logger.info("User %s balance reduced" % (u['user_id']))
            if u['balance'] - settings['amount'] < settings['amount']:
                if u['lang'] not in msgs.keys():
                    msgs[u['lang']] = db.query_one("SELECT msg FROM %s WHERE id=15" % (u['lang']))['msg']
                url = "https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s" % (settings['token'],
                                                                                         u['user_id'],
                                                                                         msgs[u['lang']] % (settings['amount']))
                r = requests.get(url)

        else:
            url = "https://api.telegram.org/bot%s/kickChatMember?revoke_messages=false&chat_id=%s&user_id=%s" % (settings['token'],
                                                                                                                 chats[u['lang']],
                                                                                                                 u['user_id'])
            r = requests.get(url)
            sql = "UPDATE users SET status=0 WHERE user_id=%s" % (u['user_id'])
            db.query_one(sql)
            logger.info("User %s kicked from chat" % (u['user_id']))

    logger.info("Sleeping %s minutes" % (int(period/60)))
    time.sleep(period)