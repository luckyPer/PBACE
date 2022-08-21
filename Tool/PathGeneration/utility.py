# coding=utf-8
import pandas as pd
import configparser
import os


def write_to_csv(ts, target_trans, model_name):
    target_path = []
    path = []
    c_val = []
    i_val = []
    sc_val = []
    trace_val = []
    output_val = []
    if ts:
        for ind in range(len(ts['path'])):
            path.append(ts['path'][ind])
            c_val.append(ts['context'][ind])
            target_path.append(target_trans)
            i_val.append(ts['input'][ind])
            sc_val.append(ts['sc'][ind])
            trace_val.append(ts['trace'][ind])
            output_val.append(ts['output'][ind])
        # 字典
        dict = {'target': target_path, 'path': path, 'context_values': c_val, 'input_params': i_val}

        dict_sc = {'target': target_path, 'trace': trace_val, 'sc': sc_val, 'output_event': output_val}
        df = pd.DataFrame(dict_sc)
        coverage_config = read_conf_C()
        file_name = 'transition_{0}_{1}.csv'.format(model_name, coverage_config)
        # 保存 dataframe
        df.to_csv(file_name, mode='a', header=False, index=True)
        pass


def blank_line(model_name):
    dict1 = {'target': [''], 'path': [''], 'context_values': [''], 'input_params': ['']}
    dict_sc = {'target': [''], 'trace': [''], 'sc': [''], 'output_event': ['']}
    df = pd.DataFrame(dict_sc)
    coverage_config = read_conf_C()
    file_name = 'transition_{0}_{1}.csv'.format(model_name, coverage_config)
    # 保存 dataframe
    df.to_csv(file_name, mode='a', header=False, index=False)


def read_conf_C():
    conf = configparser.ConfigParser()
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    conf.read(root_path + '/PathGeneration/config.conf', 'utf8')
    C = conf.get('coverage_criterion', 'C')
    return C


def read_conf_m():
    conf = configparser.ConfigParser()
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    conf.read(root_path + '/PathGeneration/config.conf', 'utf8')
    m = conf.get('model_name', 'm')
    return m

if __name__ == "__main__":
    print(read_conf_m())