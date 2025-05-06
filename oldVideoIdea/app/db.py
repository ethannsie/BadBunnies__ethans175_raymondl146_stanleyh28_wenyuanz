import sqlite3
import csv
from datetime import datetime

DB_FILE = "stock.db"

def setup():
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = db.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, privacy TEXT, created_at TEXT, last_login TEXT);")
    c.execute("CREATE TABLE IF NOT EXISTS portfolio (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, stock_name TEXT);")
    # c.execute("CREATE TABLE IF NOT EXISTS gameChallenge (challenge_ID INTEGER PRIMARY KEY AUTOINCREMENT, challenger TEXT, challenged TEXT, accepted_status TEXT);")
    # c.execute("CREATE TABLE IF NOT EXISTS gameHistory (game_ID INTEGER PRIMARY KEY, winner TEXT, loser TEXT);")
    # c.execute("CREATE TABLE IF NOT EXISTS gameTracker (game_ID INTEGER, player1 TEXT, player2 TEXT, move1 TEXT, move2 TEXT, turn INTEGER);")
    # c.execute("CREATE TABLE IF NOT EXISTS battlelog (game_ID INTEGER, action TEXT);")

    db.commit()
    db.close()

# User Initialization and Manipulation --------------------------------
def addUser(username, password):
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = db.cursor()
    # datetime formatting for sqlite text
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # omits userID as an input as it autoincrements
    c.execute("INSERT INTO users (username, password, privacy, created_at, last_login) VALUES (?, ?, ?, ?, ?)", (username, password, "Public", created_at, created_at))
    db.commit()
    db.close()

def addStock(username, stock):
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = db.cursor()
    c.execute("INSERT INTO portfolio (username, stock_name) VALUES (?, ?)", (username, stock))
    db.commit()
    db.close()

def removeStock(username, stock):
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = db.cursor()
    c.execute("DELETE FROM portfolio WHERE username = ? AND stock_name = ?", (username, stock))
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

def updateLoginTime(username):
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = db.cursor()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("UPDATE users SET last_login = ? WHERE username = ?", (current_time, username))
    db.commit()
    db.close()

# Table Updating and Manipulation of Data --------------------------------
def updateGameHistory(game_number, winner, loser):
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = db.cursor()
    c.execute("INSERT INTO gameHistory (game_ID, winner, loser) VALUES (?, ?, ?)", (game_number, winner, loser))
    db.commit()
    db.close()

def updateChallengeInitial(user1, user2):
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = db.cursor()
    c.execute("INSERT INTO gameChallenge (accepted_status, challenger, challenged) VALUES (?,?, ?)", ("None",user1,user2))
    db.commit()
    db.close()

def updateChallengeFinal(accepted_status, challenger, challenged):
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = db.cursor()
    c.execute("UPDATE gameChallenge SET accepted_status = ? WHERE challenger = ? AND challenged = ?", (accepted_status, challenger, challenged))
    db.commit()
    db.close()

def updateBattleLog(game_id, action):
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = db.cursor()
    c.execute("INSERT INTO battlelog (game_ID, action) VALUES (?, ?)", (game_id, action))
    db.commit()
    db.close()

def initializeGameTracker(game_id):
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = db.cursor()
    c.execute("INSERT INTO gameTracker (game_id, turn) VALUES (?,?)", (game_id, 0))
    db.commit()
    db.close()

def updateGameTracker(game_id, player, move, oneOrTwo, turn):
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = db.cursor()
    c.execute("UPDATE gameTracker SET move" + str(oneOrTwo) + " = ? WHERE game_ID = ? AND player" + str(oneOrTwo) +  " = ? AND turn = ?", (move, game_id, player, turn))
    db.commit()
    db.close()

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

def getChallengeData(accepted_status, challenger, challenged):
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = db.cursor()
    c.execute("SELECT * FROM gameChallenge WHERE accepted_status = ? AND challenger = ? AND challenged = ?", (accepted_status, challenger, challenged))
    result = c.fetchall()
    db.close()
    if result:
        return result
    else:
        return -1

def getChallengeHistory(username):
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = db.cursor()
    c.execute("SELECT * FROM gameChallenge WHERE challenger = ? OR challenged = ?", (username, username))
    result = c.fetchall()
    print(result)
    db.close()
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
