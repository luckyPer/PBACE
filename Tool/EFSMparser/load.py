# coding=utf-8
import pyauparser
import os
from .efsm import EFSM
from EFSMparser import EFSMParser
from EFSMparser.utility import read_json_file, read_conf_by_key


dir_name = os.path.dirname(__file__)
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class LoadEFSM(object):
    def __init__(self):
        self.efsm = EFSM()

    def read_transition(self, t):
        _tmp_trans = {}
        h_state = t.get('h_state')
        t_state = t.get('t_state')
        if h_state not in self.efsm.states_table:
            self.efsm.add_states(h_state)
        if t_state not in self.efsm.states_table:
            self.efsm.add_states(t_state)

    def construct_efsm(self, t_list):
        for t in t_list:
            self.read_transition(t)
        self.efsm.init_adjacency_matrix()
        for t in t_list:
            self.efsm.add_transition(t)

    def load_efsm(self, specification_name):
        json_name = 'Specification/{0}.json'.format(specification_name)
        file_name = os.path.join(root_path, json_name)
        t_list = read_json_file(file_name)
        input_params = {}
        context_vars = {}
        try:
            for t in t_list:
                str = t.get('action') + t.get('input_event') + t.get('guard')
                efsmp = EFSMParser(os.path.join(dir_name, "grammar/EFSMparserPlus.egt"))
                grammar = efsmp.get_grammar()
                if str:
                    tree = pyauparser.parse_string_to_tree(grammar, str)
                    efsmp.analysis(tree, context_vars, input_params)
                t['input_params'] = set([_key for _key in efsmp.get_input_params().keys()])
                t['define_set'] = set()
                t['use_set'] = set()
                for _key, _v in efsmp.get_input_params().items():
                    if _key not in input_params:
                        input_params.__setitem__(_key, _v)
                    if input_params[_key]['value'] is None:
                        input_params.__setitem__(_key, _v)
                define_set = set()
                define_var_str = t.get('input_event') + t.get('action')
                if define_var_str:
                    define_var_tree = pyauparser.parse_string_to_tree(grammar, define_var_str)
                    efsmp.analysis_define(define_var_tree, define_set)
                t['define_set'] = define_set
                use_set = set()
                use_var_str = t.get('output_event') + t.get('action') + t.get('guard')
                if use_var_str:
                    use_var_tree = pyauparser.parse_string_to_tree(grammar, use_var_str)
                    efsmp.analysis_use(use_var_tree, use_set)
                t['use_set'] = use_set

            self.construct_efsm(t_list)
            self.efsm.set_context_vars(context_vars)
            self.efsm.set_inp_params(input_params)

            _str_init_state = read_conf_by_key('init_state', 's')
            self.efsm.init_sc(_str_init_state, context_vars, input_params)
            self.efsm.update_tran_guard_set()
            self.efsm.set_model_name(specification_name)
            self.efsm.get_defUse_Pair(self.efsm.trans_list)
            return self.efsm

        except pyauparser.ParseError as e:
            print(e)
            return None
