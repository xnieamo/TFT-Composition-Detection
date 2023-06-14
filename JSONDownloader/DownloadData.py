import requests
import json
import os


def has_update():

    url = "https://raw.communitydragon.org/latest/content-metadata.json"
    response = requests.get(url)
    if response.status_code == 200:
        versions = json.loads(response.text)
        latest_version = versions["version"]
        return latest_version != get_current_version()
    else:
        return True

def get_current_version():

    script_dir = os.path.dirname(os.path.abspath(__file__))
    rel_path = "../Data/content-metadata.json"
    abs_file_path = os.path.join(script_dir, rel_path)

    with open(abs_file_path, "r") as f:
        data = json.load(f)
        return data["version"]

def update_data():
    if has_update():
        print("New data available")
        url = "https://raw.communitydragon.org/latest/cdragon/tft/en_us.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            rel_path = "../Data/en_us.json"
            abs_file_path = os.path.join(script_dir, rel_path)
            with open(abs_file_path, "w") as f:
                json.dump(data, f, indent=4)
            print("Data updated")

