from datetime import datetime
import sqlite3
import time
import os

def setup():
    global conn
    path = "./data/Tentro.db"
    conn = sqlite3.connect(path)

    with open(path, "rb") as file:
        filename = datetime.now().strftime("%y-%m-%d %H%M")
        if not os.path.exists(os.path.join("data", "db_backups")):
            os.makedirs(os.path.join("data", "db_backups"))
        with open(f"./data/db_backups/{filename}.db", "wb+") as newfile:
            newfile.writelines(file.readlines())

    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS guilds (
                        guild_id integer NOT NULL,
                        notice string NOT NULL,
                        prefix string NOT NULL,
                        language string NOT NULL,
                        name string NOT NULL
                    );""")

    c.execute("""CREATE TABLE IF NOT EXISTS users (
                        user_id integer NOT NULL
                    );""")

    c.execute("""CREATE TABLE IF NOT EXISTS notices (
                        date integer NOT NULL,
                        title string NOT NULL,
                        message string NOT NULL
                    );""")

    c.execute("""CREATE TABLE IF NOT EXISTS rolejoin (
                        guild_id string NOT NULL,
                        role_id string NOT NULL
                    );""")

    c.execute("""CREATE TABLE IF NOT EXISTS leavecmd (
                        guild_id integer NOT NULL,
                        msg string NOT NULL,
                        channel_id integer NOT NULL
                    );""")

    c.execute("""CREATE TABLE IF NOT EXISTS joincmd (
                        guild_id integer NOT NULL,
                        msg string NOT NULL,
                        channel_id integer NOT NULL
                    );""")

    conn.commit()

def checkguilds(guilds):
    c = conn.cursor()
    guild_ids = dict()
    for guild in guilds:
        guild_ids[guild.id] = guild

    for guild_id in guild_ids:
        t = (guild_id,)
        c.execute("SELECT * FROM guilds where guild_id=?;", t)
        if not c.fetchone():
            addguild(guild_id)

    count = [0, 0]
    c.execute("SELECT guild_id FROM guilds;")
    for guild_id in c.fetchall():
        if not (guild_id[0] in guild_ids):
            count[0] += 1
            c.execute("DELETE FROM guilds WHERE guild_id=?;", guild_id)
        else:
            channel_ids = [channel.id for channel in guild_ids[guild_id[0]].channels]
            c.execute("SELECT channel_id FROM channels WHERE guild_id=?;", guild_id)
            channels = c.fetchall()
            for channel_id in channels:
                if not (channel_id[0] in channel_ids):
                    count[1] += 1
                    c.execute("DELETE FROM channels WHERE channel_id=?;", channel_id)
    print("Removed", count[0], "guilds from 'guilds'")
    print("Removed", count[1], "channels from 'channels'")

    count = 0
    c.execute("SELECT guild_id FROM channels;")
    for guild_id in c.fetchall():
        if not (guild_id[0] in guild_ids):
            count += 1
            c.execute("DELETE FROM channels WHERE guild_id=?;", guild_id)
    print("Removed", count, "guild channels from 'channels'")

    count = 0
    c.execute("SELECT guild_id FROM counting;")
    for guild_id in c.fetchall():
        if not (guild_id[0] in guild_ids):
            count += 1
            c.execute("DELETE FROM counting WHERE guild_id=?;", guild_id)
    print("Removed", count, "guilds from 'counting'\n")

    conn.commit()

# General

def addguild(guild_id):
    c = conn.cursor()
    t = (guild_id, time.time())
    c.execute("""INSERT INTO guilds (
                        guild_id, notice,
                        prefix, language,
                        name
                    )
                    VALUES (
                        ?, ?,
                        't!', 'english',
                        '',
                    );""", t)
    t = (guild_id,)
    conn.commit()

def removeguild(guild_id):
    c = conn.cursor()
    t = (guild_id,)
    c.execute("DELETE FROM guilds WHERE guild_id=?;", t)
    conn.commit()

# Config

def getlang(guild_id):
    c = conn.cursor()
    t = (guild_id,)
    c.execute("SELECT language FROM guilds WHERE guild_id=?;", t)
    return c.fetchone()[0]

# Notices

def addnotice(date, title, message):
    c = conn.cursor()
    t = (date, title, message)
    c.execute("""INSERT INTO notices (
                    date, title, message
                )
                VALUES (
                    ?, ?, ?
                );""", t)
    conn.commit()

def editnotice(title, message):
    c = conn.cursor()
    t = (title, message, getlastnotice()[0])
    c.execute(f"UPDATE notices SET title=?, message=? WHERE date=?;", t)
    return c.fetchone()

def getlastnotice():
    c = conn.cursor()
    c.execute(f"SELECT * FROM notices ORDER BY date DESC LIMIT 1;")
    return c.fetchone()

def getservernotice(guild_id):
    c = conn.cursor()
    t = (guild_id,)
    c.execute(f"SELECT notice FROM guilds WHERE guild_id=?;", t)
    return c.fetchone()[0]

def updateservernotice(guild_id):
    c = conn.cursor()
    t = (time.time(), guild_id)
    c.execute(f"UPDATE guilds SET notice=? WHERE guild_id=?;", t)
    conn.commit()

# Users

def register(user_id):
    c = conn.cursor()
    t = (user_id,)
    c.execute("SELECT user_id FROM users WHERE user_id=?;", t)
    if c.fetchone() is None:
        c.execute(f"""INSERT INTO users (
                        user_id
                    )
                    VALUES (
                        ?
                    );""", t)
        conn.commit()

# Prefix

def changeprefix(guild_id, prefix):
    c = conn.cursor()
    t = (prefix, guild_id)
    c.execute("UPDATE guilds SET prefix=? WHERE guild_id=?;", t)
    conn.commit()

def getprefix(guild_id):
    c = conn.cursor()
    t = (guild_id,)
    c.execute("SELECT prefix FROM guilds WHERE guild_id=?;", t)
    return c.fetchone()[0]