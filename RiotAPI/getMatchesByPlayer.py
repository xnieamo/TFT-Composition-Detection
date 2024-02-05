import requests
import json
from time import sleep

headers = {
    "X-Riot-Token": "***REMOVED***"
}

# load the challenger players from json
with open("challengerPlayers.json", "r") as f:
    data = json.load(f)

# For each player, if they have a puuid, get their match history
for i in range(len(data["entries"])):
    if "puuid" in data["entries"][i]:
        puuid = data["entries"][i]["puuid"]
        matchCount = data["entries"][i]["wins"] + data["entries"][i]["losses"]
        URL = "https://americas.api.riotgames.com/tft/match/v1/matches/by-puuid/" + puuid + "/ids?count=" + str(matchCount)
        response = requests.get(URL, headers=headers)
        if response.status_code == 200:
            matchData = response.json()
            data["entries"][i]["matches"] = matchData
            print(i + 1, "/", len(data["entries"]))
        else:
            print("Error: ", response.status_code)

        # For API rate limits
        sleep(1.5)

# Save the data to a file
with open("challengerPlayersWithMatches.json", "w") as f:
    json.dump(data, f, indent=4)