# coding=utf-8
import configparser
import os

from EFSMparser.load import LoadEFSM


def read_conf_m():
    conf = configparser.ConfigParser()
    dir_name = os.path.dirname(__file__)
    conf.read(dir_name + '/config.conf', 'utf8')
    m = conf.get('model_name', 'm')
    return m


if __name__ == "__main__":
    SPEC_FILE = read_conf_m()
    l = LoadEFSM()
    efsm_obj = l.load_efsm(SPEC_FILE)
    print(efsm_obj)
