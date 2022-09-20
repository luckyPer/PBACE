# coding=utf-8
import numpy
import pyauparser
import os

from .transition import Transition
from .stateConfiguration import SC
from . import EFSMParser

dir_name = os.path.dirname(__file__)


class EFSM(object):
    def __init__(self):
        self.model_name = ""
        self.cur_sc = None  # 当前状态格局
        self.context_vars = None  # 上下文变量表
        self.inp_params = None  # 统计出的所有输入变量
        self.adjacency_matrix = [[]]  # 邻接矩阵
        self.adjacency_list = []  # 邻接表
        self.states_table = []  # 状态-下标 映射表
        self.trans_list = []  # 总变迁列表
        self.trans_name_map = {}  # 变迁名 - 变迁信息 映射
        self.trans_guard_list = []  # guards里有输入变量的变迁合集
        self.guard_content = {}  # 按guard 左中右 分解后的内容

    def set_model_name(self, v):
        self.model_name = v

    def get_cur_sc(self):
        return self.cur_sc

    def set_cur_sc(self, cur_sc):
        self.cur_sc = cur_sc

    def get_context_vars(self):
        return self.context_vars

    def set_context_vars(self, context_vars):
        self.context_vars = context_vars

    def get_inp_params(self):
        return self.inp_params

    def set_inp_params(self, inp_params):
        for key, value in inp_params.items():
            if value['type'] == int:
                value['value'] = 0
            elif value['type'] == bool:
                value['value'] = False
        self.inp_params = inp_params

    def add_states(self, state):
        self.states_table.append(state)

    def get_states_table(self):
        return self.states_table

    def init_adjacency_matrix(self):
        length = len(self.states_table)
        if length:
            self.adjacency_matrix = [[[] for _ in range(length)] for _ in range(length)]
            self.adjacency_list = [[] for _ in range(length)]

    def init_sc(self, state, context, input_params=None, transition_path=[]):
        self.context_vars = context
        _context_vars = {}
        _input_params = {}
        for key, value in context.items():
            _context_vars.__setitem__(key, value['value'])
        for key, value in input_params.items():
            _input_params.__setitem__(key, value['value'])

        self.cur_sc = SC(state, _context_vars, _input_params, transition_path)

    def init_sc_val(self, sc):
        input_params = sc.get_cur_input_params()
        for key, value in input_params.items():
            input_params[key] = self.inp_params[key]['value']

    def is_feasible(self, cur_transition, sc=None):
        # state = sc.get_cur_state()
        context = sc.get_cur_context()
        input_param = sc.get_cur_input_params()
        guard = cur_transition.guard
        if guard == '':
            return True
        if not cur_transition:
            return False
        flag = None
        efsmp = EFSMParser(os.path.join(dir_name, "grammar/EFSMParserGuardIPSG.egt"))
        grammar = efsmp.get_grammar()
        try:
            tree = pyauparser.parse_string_to_tree(grammar, guard)
            flag = efsmp.judge_ipsg(tree, context, input_param)
            if type(flag) is bool or type(flag) is numpy.bool_:
                return flag
            else:
                if False in flag:
                    return False
                else:
                    return True
        except pyauparser.ParseError as e:
            return False

    def execute(self, cur_transition, sc):
        if not cur_transition:
            return
        # state = sc.get_cur_state()
        context = sc.get_cur_context()
        input_param = sc.get_cur_input_params()
        action = cur_transition.action
        if len(action) == 0:
            return
        flag = None
        efsmp = EFSMParser(os.path.join(dir_name, "grammar/EFSMparserPlus.egt"))
        grammar = efsmp.get_grammar()
        try:
            tree = pyauparser.parse_string_to_tree(grammar, action)
            flag = efsmp.evaluate(tree, context, input_param)
            return flag
        except pyauparser.ParseError as e:
            return False

    def update_transition_output(self, cur_transition, contexts, input_params):
        result_event = ''
        output_event = cur_transition.get_output_event()
        if output_event == '':
            return ''
        result_event = output_event
        for key, val in contexts.items():
            if key in result_event:
                result_event = result_event.replace(key, str(val))
        for key, val in input_params.items():
            if key in result_event:
                result_event = result_event.replace(key, str(val))
        return result_event

    def add_transition(self, transition):
        trans = Transition(
            trans_name=transition["trans_name"],
            h_state=transition["h_state"],
            t_state=transition["t_state"],
            inp_event=transition["input_event"],
            out_event=transition["output_event"],
            guard=transition["guard"],
            action=transition["action"],
            input_params=transition["input_params"],
            define_set=transition["define_set"],
            use_set=transition["use_set"]
        )
        head = self.states_table.index(transition["h_state"])
        tail = self.states_table.index(transition["t_state"])
        self.adjacency_matrix[head][tail].append(trans)
        self.adjacency_list[head].append(trans)
        self.trans_list.append(transition["trans_name"])
        self.trans_name_map.__setitem__(transition["trans_name"], trans)

    def get_next_trans(self, cur_state, list_flag=False):
        _transition = None
        _state_idx = self.states_table.index(cur_state)
        if list_flag:
            return self.adjacency_list[_state_idx]
        return self.adjacency_matrix[_state_idx]

    def get_inp_name_list(self):
        _list = list()
        for key, value in self.inp_params.items():
            _list.append(key)
        return _list

    def get_inp_params_by_trans_name(self, trans_name):
        transition = self.trans_name_map[trans_name]
        input_params = transition.get_input_params()
        return input_params

    def update_tran_guard_set(self):
        for tran_name, tran in self.trans_name_map.items():
            guard = tran.guard
            for inp_param in self.inp_params.keys():
                if inp_param in guard:
                    self.trans_guard_list.append(tran.trans_name)
                    break

    def get_inpParam_in_inpEvent(self):  # 找出输入变量在输入事件中的变迁
        inpParam_in_inpEvent = set()
        for tran_name, tran in self.trans_name_map.items():
            inp_event = tran.inp_event
            if inp_event == "":
                continue
            for inp_param in self.inp_params.keys():
                if inp_param in inp_event:
                    inpParam_in_inpEvent.add(tran.trans_name)
                    break
        return inpParam_in_inpEvent

    #  code for ipsg : deal with guard
    def get_guard_content(self, trans_name):
        if trans_name in self.guard_content:
            return self.guard_content.get(trans_name)
        content = {}
        transition = self.trans_name_map[trans_name]
        if transition:
            guard = transition.guard
            if guard and guard != '':
                efsmp = EFSMParser(os.path.join(dir_name, "grammar/EFSMparserSymbol.egt"))
                grammar = efsmp.get_grammar()
                try:
                    tree = pyauparser.parse_string_to_tree(grammar, guard)
                    logic_op = []
                    compare_op = []
                    express_content = []
                    efsmp.analysis_guard_content(tree, express_content, compare_op, logic_op)
                    atomicGuards = []
                    atomicOP = []
                    if express_content and compare_op:
                        while logic_op:
                            logic_idx = express_content.index(logic_op[0])
                            atomicOP.append(logic_op[0])
                            logic_op.pop(0)
                            express_content_l = express_content[:logic_idx]
                            l = self._get_expression_symbol(express_content_l, compare_op)
                            atomicGuards.append(l)
                            express_content = express_content[logic_idx + 1:]
                        l = self._get_expression_symbol(express_content, compare_op)
                        atomicGuards.append(l)
                    content = {
                        'atomicGuards': atomicGuards,
                        'atomicOP': atomicOP
                    }
                except pyauparser.ParseError as e:
                    return False
        return content

    def _get_expression_symbol(self, express_content, compare_op):
        idx = express_content.index(compare_op[0])
        l = express_content[:idx]
        l.insert(0, '+')
        r = express_content[idx + 1:]
        r.insert(0, '+')
        left = self._get_expression_symbol_detail(l)
        right = self._get_expression_symbol_detail(r)
        content = {
            'left': left,
            'op': compare_op[0],
            'right': right
        }
        compare_op.pop(0)
        return content

    def _get_expression_symbol_detail(self, express_list):
        result_list = []
        express_list.reverse()
        while express_list:
            exp = [express_list.pop() for _ in range(2)]
            sign = exp[0]
            name = exp[1]
            type = ''
            if name in self.context_vars:
                type = 'context'
            elif name in self.inp_params:
                type = 'input'
            else:
                type = 'constant'
            content = {
                'name': name,
                'sign': sign,
                'type': type,
            }
            result_list.append(content)
        return result_list

    # define-user begin
    def get_define_var(self, trans_name):
        trans_name = str(trans_name)
        tran = self.trans_name_map[trans_name]
        define_var = tran.get_define_var()
        return define_var

    def get_use_var(self, trans_name):
        trans_name = str(trans_name)
        tran = self.trans_name_map[trans_name]
        use_var = tran.get_use_var()
        return use_var

    def get_defUse_Pair(self, test_path):
        defUsePair = set()
        len_tp = len(test_path)
        for i in range(len_tp):
            define_var = self.get_define_var(test_path[i])
            if not define_var:
                continue
            for j in range(i, len_tp):
                use_var = self.get_use_var(test_path[j])
                if not use_var:
                    continue
                intersection_set = define_var & use_var
                if intersection_set:
                    defUsePair = defUsePair | intersection_set

        return defUsePair
