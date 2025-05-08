# Bad Bunnies
# SoftDev
# P05:
# 2025-06-XX
# Time Spent: not enough hours

import sqlite3
import csv
from datetime import datetime

DB_FILE = "stock.db"

def setup():
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = db.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL);")
    c.execute("CREATE TABLE IF NOT EXISTS uploads (image_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, training BOOLEAN, image_path TEXT NOT NULL, datetime TEXT NOT NULL);")
    # c.execute("CREATE TABLE IF NOT EXISTS history (game_ID INTEGER PRIMARY KEY, winner TEXT, loser TEXT);")

    db.commit()
    db.close()

# User Initialization and Manipulation --------------------------------
def addUser(username, password):
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = db.cursor()
    # datetime formatting for sqlite text
    # created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # omits userID as an input as it autoincrements
    c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password))
    db.commit()
    db.close()

# searches the users DB for the userID associated to the username parameter
def checkUser(username):
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = db.cursor()
    c.execute("SELECT user_id FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    db.close()
    # check in case there is an error in fetching data
    if result:
        return result[0]
    else:
        return -1

#Updates a value in a table with a new value
def setTableData(table, updateValueType, newValue, valueType, value):
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = db.cursor()
    c.execute(f"UPDATE {table} SET {updateValueType} = '{newValue}' WHERE {valueType} = ?", (value,))
    db.commit()
    db.close()

# Getting information from tables ------------------------------------------
#Selecting specific argument-based data
def getTableData(table, valueType, value):
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = db.cursor()
    # make sure that this all exists
    c.execute("SELECT * FROM " + table + " WHERE " + valueType + " = ?", (value,))
    result = c.fetchone()
    db.close()
    # check in case there is an error in fetching data
    if result:
        return result
    else:
        return -1

#Selecting specific argument-based data -- same as getTableData except gets all rows instead of only one
def getAllTableData(table, valueType, value):
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = db.cursor()
    # make sure that this all exists
    c.execute("SELECT * FROM " + table + " WHERE " + valueType + " = ?", (value,))
    result = c.fetchall()
    db.close()
    # check in case there is an error in fetching data
    if result:
        return result
    else:
        return -1

#Resetting any table
def resetTable(tableName):
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = db.cursor()
    c.execute("DELETE FROM " + tableName)
    db.commit()
    db.close()
