import sqlite3
import requests
import json
from time import sleep


# Load the data from the json file
with open("challengerPlayersWithMatches.json", "r") as f:
    data = json.load(f)

# Open TFT database
db = sqlite3.connect('TFT.db')
print(sqlite3.version)

# Create match data table in database if it does not exist. This table holds metadata about the matches.
cursor = db.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS matches(
        id TEXT PRIMARY KEY,
        gameDatetime TIMESTAMP,
        gameLength FLOAT,
        gameVaration TEXT,
        gameVersion TEXT,
        queueId INTEGER,
        tftSetNumber INTEGER
    )
''')

# Create match players table in database if it does not exist. This table holds metadata about the players in the matches.
cursor.execute('''
    CREATE TABLE IF NOT EXISTS matchPlayers(
        matchId TEXT,
        puuid TEXT,
        goldLeft INTEGER,
        lastRound INTEGER, 
        level INTEGER,
        placement INTEGER,
        playersEliminated INTEGER,
        timeEliminated FLOAT,
        totalDamageToPlayers INTEGER,
        PRIMARY KEY(matchId, puuid),
        FOREIGN KEY(matchId) REFERENCES matches(id),
        FOREIGN KEY(puuid) REFERENCES players(puuid)
    )
''')
# Enforce the unique constraint on the matchPlayers table
cursor.execute('''
    CREATE UNIQUE INDEX IF NOT EXISTS matchPlayerIndex ON matchPlayers(matchId, puuid)
''')

# Create a units table for each match/player combination.
cursor.execute('''
    CREATE TABLE IF NOT EXISTS matchUnits(
        matchId TEXT,
        puuid TEXT,
        characterId INTEGER,
        characterName TEXT,
        tier INTEGER,
        itemCount INTEGER,
        item1 TEXT,
        item2 TEXT,
        item3 TEXT,
        PRIMARY KEY(matchId, puuid, characterId),
        FOREIGN KEY(matchId) REFERENCES matches(id),
        FOREIGN KEY(puuid) REFERENCES players(puuid)
    )
''')

# Create a traits table for each match/player combination.
cursor.execute('''
    CREATE TABLE IF NOT EXISTS matchTraits(
        matchId TEXT,
        puuid TEXT,
        traitName TEXT,
        numUnits INTEGER,
        activeTier INTEGER,
        totalTier INTEGER,
        PRIMARY KEY(matchId, puuid, traitName),
        FOREIGN KEY(matchId) REFERENCES matches(id),
        FOREIGN KEY(puuid) REFERENCES players(puuid)
    )
''')

db.commit()


### Adding the data to the database

# Riot API Key
headers = {
    "X-Riot-Token": "***REMOVED***"
}

# Loop over each player and load match data. Then pull match JSON from RIOT API
for i in range(len(data["entries"])):
    if i < 97:
        continue

    if "puuid" in data["entries"][i]:
        matches = data["entries"][i]["matches"]
        puuid = data["entries"][i]["puuid"]
        for match in matches:
            # Check if match is in database
            res = cursor.execute('''
                SELECT * FROM matches WHERE id = ?
            ''', (match,))
            if res.fetchone() is None:
                # If the match is not in the database, pull the match JSON from the RIOT API
                print("Match not in database. Pulling from RIOT API")

                # Pull match JSON from RIOT API
                URL = "https://americas.api.riotgames.com/tft/match/v1/matches/" + match
                response = requests.get(URL, headers=headers)
                if response.status_code == 200:
                    matchData = response.json()
                    sleep(1.25)
                    # print(matchData)
                else:
                    print("Error: ", response.status_code)
                
                # Add match to the database
                cursor.execute('''
                    INSERT INTO matches(id, gameDatetime, gameLength, gameVersion, queueId, tftSetNumber)
                    VALUES(?,?,?,?,?,?)
                ''', (match, matchData["info"]["game_datetime"], matchData["info"]["game_length"], matchData["info"]["game_version"], matchData["info"]["queue_id"], matchData["info"]["tft_set_number"]))
                
                # Add match players to the database
                for player in matchData["info"]["participants"]:

                    # Check if player is in the database
                    res = cursor.execute('''
                        SELECT * FROM players WHERE puuid = ?
                    ''', (player["puuid"],))
                    if res.fetchone() is None:
                        # Pull player JSON from RIOT API
                        URL = "https://na1.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/" + player["puuid"]
                        response = requests.get(URL, headers=headers)

                        if response.status_code == 200:
                            playerData = response.json()
                            sleep(1.25)
                            # Add player to the database. If player is in database, update values.
                            cursor.execute('''
                                INSERT INTO players(puuid, name)
                                VALUES(?,?) ON CONFLICT(name) DO UPDATE SET puuid = ?
                            ''', (player["puuid"], playerData["name"], player["puuid"]))
                            

                            # print(playerData)
                        else:
                            print("Error: ", response.status_code)
                            print(URL)

                    # Add match players to the database
                    cursor.execute('''
                        INSERT INTO matchPlayers(matchId, puuid, goldLeft, lastRound, level, placement, playersEliminated, timeEliminated, totalDamageToPlayers)
                        VALUES(?,?,?,?,?,?,?,?,?)
                    ''', (match, player["puuid"], player["gold_left"], player["last_round"], player["level"], player["placement"], player["players_eliminated"], player["time_eliminated"], player["total_damage_to_players"]))
                    
                    # Add match units to the database
                    for u in range(len(player["units"])):
                        items = [None, None, None]
                        # print(player["units"][u]["itemNames"])
                        for i in range(min(len(player["units"][u]["itemNames"]),3)):
                            items[i] = player["units"][u]["itemNames"][i]

                        cursor.execute('''
                            INSERT INTO matchUnits(matchId, puuid, characterId, characterName, tier, itemCount, item1, item2, item3)
                            VALUES(?,?,?,?,?,?,?,?,?)
                        ''', (match, player["puuid"], u, player["units"][u]["character_id"], player["units"][u]["tier"], len(player["units"][u]["itemNames"]), items[0], items[1], items[2]))
                    
                    # Add match traits to the database
                    for t in player["traits"]:
                        cursor.execute('''
                            INSERT INTO matchTraits(matchId, puuid, traitName, numUnits, activeTier, totalTier)
                            VALUES(?,?,?,?,?,?)
                        ''', (match, player["puuid"], t["name"], t["num_units"], t["tier_current"], t["tier_total"]))

            # Commit changes for this match to the database
            db.commit() 
            print(match)





# Close database
db.close()