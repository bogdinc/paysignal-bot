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

usdt = 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'

period = 5 * 60


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

chats = dict()

sql = "SELECT chat_id, link, lang FROM channels"

for x in db.query_all(sql):
    chats[x['lang']] = {
                        'link': "https://t.me/joinchat/%s" % (x['link']),
                        'id': int(x['chat_id'])
    }


while True:

    settings = db.query_one("SELECT token, wallet, last_check FROM settings WHERE id=1")

    users=dict()

    sql = "SELECT wallet, user_id, lang, status, firstname, balance FROM users"
    for x in db.query_all(sql):
        users[x['wallet']] = {
                                'user_id': x['user_id'],
                                'lang': x['lang'],
                                'status': x['status'],
                                'firstname': x['firstname'],
                                'balance': x['balance']
                            }


    wallets = set(users.keys())

    now = int(time.time())
    logger.info("Checking payments at %s" % (now))
    url = "https://api.trongrid.io/v1/accounts/%s/transactions/trc20?only_to=true&limit=200&min_timestamp=%s&&contract_address=%s" % (settings['wallet'],
                                                                                                                 settings['last_check']*1000, usdt)

    response = requests.request("GET", url)
    result = response.json()['data']
    if result:
        logger.info("%s transactions found" % (len(result)))

    for tx in result:
        if tx["block_timestamp"] == settings['last_check']*1000:
            break
        try:
            token = tx["token_info"]["address"]
        except:
            continue
        if tx["type"] == "Transfer" and int(tx['value'])>0 and tx['from'] in wallets:
            amount = int(tx['value'])/10**6
            user = users[tx['from']]
            logger.info("Found payment %s USDT from %s" % (amount, tx['from']))
            if user['status'] == 1:
                sql = "UPDATE users SET balance=balance+%s WHERE user_id=%s" % (amount,
                                                                                user['user_id'])
                msg = db.query_one("SELECT msg FROM %s WHERE id=16" % (user['lang']))['msg'] % (user['firstname'],
                                                                                                amount)
            else:
                sql = "UPDATE users SET status=1, balance=balance+%s WHERE user_id=%s" % (amount,
                                                                                          user['user_id'])

                if user['balance'] + amount >= 20:
                    msg = db.query_one("SELECT msg FROM %s WHERE id=7" % (user['lang']))['msg'] % (user['firstname'],
                                                                                                   chats[user['lang']]['link']
                                                                                                    )
                    url = "https://api.telegram.org/bot%s/unbanChatMember?only_if_banned=true&chat_id=%s&user_id=%s" % (settings['token'],
                                                                                        chats[user['lang']]['id'],
                                                                                        user['user_id'])
                    r = requests.get(url)
                else:
                    msg = db.query_one("SELECT msg FROM %s WHERE id=16" % (user['lang']))['msg'] % (user['firstname'],
                                                                                                    amount)

            db.query_one(sql)
            url = "https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s" % (settings['token'],
                                                                                     user['user_id'],
                                                                                     msg
                                                                                     )
            r = requests.get(url)

    sql = "UPDATE settings SET last_check=%s WHERE id=1" % (now)
    db.query_one(sql)

    msgs = dict()

    sql = """SELECT payments.user_id, users.lang, users.firstname FROM payments
             INNER JOIN users
             ON payments.user_id = users.user_id
             WHERE payments.created_at<=%s""" % (now - period * 2)
    data = db.query_all(sql)
    for x in data:
        if x['lang'] not in msgs.keys():
            msgs[x['lang']] = db.query_one("SELECT msg FROM %s WHERE id=8" % (x['lang']))['msg']
        url = "https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s" % (settings['token'],
                                                                                 x['user_id'],
                                                                                 msgs[x['lang']] % (x['firstname']))
        r = requests.get(url)

    sql = "DELETE FROM payments WHERE created_at<=%s" % (now-period*2)
    db.query_one(sql)
    logger.info("Sleeping 5 mins")
    time.sleep(period)
