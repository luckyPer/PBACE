# coding=utf-8
import json
import configparser
import os


def read_json_file(path):
    new_dict = None
    with open(path, "r") as f:
        new_dict = json.load(f)
    return new_dict


def read_conf_by_key(section, option):
    conf = configparser.ConfigParser()
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    conf.read(root_path + '/EFSMparser/config.conf', 'utf8')
    V = conf.get(section, option)
    return V