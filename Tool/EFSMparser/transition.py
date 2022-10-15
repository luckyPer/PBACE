# coding=utf-8
class Transition(object):
    def __init__(self, trans_name, h_state, t_state,
                 inp_event, guard, action, input_params,
                 define_set, use_set, out_event):
        self.trans_name = trans_name  # 变迁名字 string类型
        self.h_state = h_state  # 头状态 string类型
        self.t_state = t_state  # 尾状态 string类型
        self.inp_event = inp_event  # 提取的输入事件文本
        self.out_event = out_event
        self.guard = guard  # 提取的谓词判断条件文本
        self.action = action  # 提取的更新操作文本
        self.input_params = input_params  # 输入事件中的变量名 set
        self.sc = None  # 全局的状态格局
        self.define_set = define_set  # 用于统计def-use pair
        self.use_set = use_set

    def set_sc(self, v):
        self.sc = v

    def get_input_params(self):
        return self.input_params

    def set_oup_event(self, v):
        self.out_event = v

    def get_output_event(self):
        return self.out_event

    def get_define_var(self):
        return self.define_set

    def get_use_var(self):
        return self.use_set

    def get_inp_event(self):
        return self.inp_event

    def get_trans_name(self):
        return self.trans_name

