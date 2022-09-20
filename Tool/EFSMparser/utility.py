# coding=utf-8
import json


def read_json_file(path):
    new_dict = None
    with open(path, "r") as f:
        new_dict = json.load(f)
    return new_dict

