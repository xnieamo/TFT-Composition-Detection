import sqlite3
import json

# Load the data from the json file
with open("challengerPlayersWithMatches.json", "r") as f:
    data = json.load(f)

# Open TFT database
db = sqlite3.connect('TFT.db')
print(sqlite3.version)

# Create tables in database. Start with players.
cursor = db.cursor()

# Create the players table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS players(
        name TEXT PRIMARY KEY,
        id TEXT,
        puuid TEXT,
        wins INTEGER,
        losses INTEGER,
        lp INTEGER
    )
''')

# Load player data into the table. Check if the player has puuid
for i in range(len(data["entries"])):
    if "puuid" in data["entries"][i]:
        #print(data["entries"][i]["summonerName"])
        name = data["entries"][i]["summonerName"]
        id = data["entries"][i]["summonerId"]
        puuid = data["entries"][i]["puuid"]
        wins = data["entries"][i]["wins"]
        losses = data["entries"][i]["losses"]
        lp = data["entries"][i]["leaguePoints"]
        cursor.execute('''
            INSERT INTO players(name, id, puuid, wins, losses, lp)
            VALUES(?,?,?,?,?,?)
        ''', (name, id, puuid, wins, losses, lp))
        db.commit()


# Close database
db.close()