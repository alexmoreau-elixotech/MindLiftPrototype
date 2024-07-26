import os
import json

def write_dict_to_file(path, content):
    with open(path, "w+") as f:
        json.dump(content, f)

def write_list_to_file(path, content):
    with open(path, "w+") as f:
        json.dump(content, f)

def load_content(path):
    content = {}
    with open(path, "r") as f:
        content = json.load(f)

    return content