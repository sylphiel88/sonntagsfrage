import sqlite3, sys, os


def create_database():
    connection = sqlite3.connect("sonntagsfrage.db")
    cursor = connection.cursor()
    sql = "CREATE TABLE sonntagsfrage(institut VARCHAR(64) PRIMARY KEY, datum DATE,cdu VARCHAR(64),spd VARCHAR(64)," \
          "gru VARCHAR(64),fdp VARCHAR(64),lin VARCHAR(64),afd VARCHAR(64),son VARCHAR(64)) "
    cursor.execute(sql)
    return cursor, connection


def get_database():
    connection = sqlite3.connect("sonntagsfrage.db")
    cursor = connection.cursor()
    return cursor, connection


class DataBase:
    def __init__(self):
        if os.path.exists("sonntagsfrage.db"):
            self.db, self.con = get_database()
        else:
            self.db, self.con = create_database()
