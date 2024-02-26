import sqlite3
import os
import pandas as pd

# Set the working directory
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, '../../Data/Raw/TFT.db')


# Static variables about version
PATCH_VERSION = "Version 14.2.556.3141"
SET = 10

# Open TFT database
db = sqlite3.connect(filename)
cur = db.cursor()

# The goal here is to extract all the match and player ids from the matchplayers table. This will be used to populate an intermediate file with champion, level, and item count. We also include placement data to run a regression model later.
cur.execute('''
    SELECT matchunits.puuid,
           matchUnits.characterId, 
           matchUnits.characterName, 
           matchUnits.tier,     
           matchUnits.itemCount,
           matchPlayers.placement
    FROM matches
    INNER JOIN matchPlayers
        ON matchplayers.matchid = matches.id and matchplayers.puuid = matchunits.puuid
    INNER JOIN matchUnits
        ON matchUnits.matchId = matches.id
    WHERE matches.gameVersion LIKE ? AND matches.tftSetNumber = ?
''',(PATCH_VERSION+'%', SET))



# Fetch the data
match_data = cur.fetchall()

# Print the data
# print(match_data)

# Create a dataframe from the data
df = pd.DataFrame(match_data, columns=["puuid","characterId", "characterName", "tier", "itemCount", "placement"])

# Print the dataframe
# print(df)

# Save the dataframe to a csv file
df.to_csv(os.path.join(dirname,'../../Data/Intermediate/matchUnits.csv'),       index=False)    

# Close the database
db.close()