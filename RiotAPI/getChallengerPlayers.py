from time import sleep
import requests
import json

URL = "https://na1.api.riotgames.com/tft/league/v1/challenger?queue=RANKED_TFT";


headers = {
    "X-Riot-Token": "***REMOVED***"
}

response = requests.get(URL,headers=headers)

if response.status_code == 200:
    data = response.json()
    # print(data)

    # For each player, we need to also aquire their PUUID
    for i in range(len(data["entries"])):
        summonerName = data["entries"][i]["summonerName"]
        URL = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonerName
        response = requests.get(URL, headers=headers)
        if response.status_code == 200:
            summonerData = response.json()
            data["entries"][i]["puuid"] = summonerData["puuid"]
            print(i + 1, "/", len(data["entries"]))
        else:
            print("Error: ", response.status_code)

        # For API rate limits
        sleep(1.5)

    # Save the data to a file
    with open("challengerPlayers.json", "w") as f:
        json.dump(data, f, indent=4)
else:
    print("Error: ", response.status_code)

