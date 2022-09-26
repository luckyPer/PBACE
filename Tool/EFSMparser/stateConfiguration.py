# coding=utf-8
import copy


class SC(object):
    def __init__(self, state=None, context_vars=None, input_params=None, transition_path=[]):
        self.cur_state = state  # 当前的状态
        self.context_vars = context_vars  # 当前的上下文变量表
        self.input_params = input_params  # 当前的输入变量
        self.transition_path = transition_path
        self.context_pool = []  # 存储上下文变量的历史记录
        self.input_pool = []  # 存储输入变量的历史记录
        self.state_pool = []  # 存储状态变量的历史记录
        self.output_pool = []  # 存储输出事件的历史记录
        self.input_event_pool = []  # 存储输入事件的历史记录

    def get_cur_state(self):  # 得到当前状态格局
        return self.cur_state

    def set_cur_state(self, v):
        self.cur_state = copy.deepcopy(v)

    def get_cur_context(self):
        return self.context_vars

    def set_cur_context(self, v):
        self.context_vars = copy.deepcopy(v)

    def get_cur_input_params(self):
        return self.input_params

    def set_cur_input_params(self, v):
        self.input_params = copy.deepcopy(v)

    def update_sc_input_params(self, input_params):
        self.input_params = input_params

    def update_sc(self, state, context, input_params, path_name, output=None, input_event=None):
        self.set_cur_state(state)
        self.set_cur_context(context)
        self.set_cur_input_params(input_params)
        self.transition_path.append(path_name)
        self.context_pool.append(context)
        self.input_pool.append(input_params)
        self.state_pool.append(state)
        self.output_pool.append(output)
        self.input_event_pool.append(input_event)

    def get_sc(self):
        return {
            'state': self.cur_state,
            'context_vars': self.context_vars,
            'input_params': self.input_params,
            'input_pool': self.input_pool,
            'context_pool': self.context_pool,
            'state_pool': self.state_pool,
            'output_pool': self.output_pool,
            'input_event': self.input_event_pool
        }
