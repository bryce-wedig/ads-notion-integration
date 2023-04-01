import datetime
import json


def write_last_successful_runtime():
    file = open('last_successful_runtime.txt', 'w')
    file.write(str(datetime.datetime.now().isoformat()))
    file.close()


def read_last_successful_runtime():
    file = open('last_successful_runtime.txt', 'r')
    contents = file.read()
    file.close()

    return datetime.datetime.fromisoformat(contents)


def read_json(filepath):
    with open(filepath) as json_file:
        return json.load(json_file)
