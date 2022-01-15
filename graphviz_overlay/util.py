import json


def load_json_file(file):
    if file:
        return json.load(file)
    return {}
