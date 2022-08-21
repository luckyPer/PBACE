# coding=utf-8
import queue
import copy
import random
from PathGeneration.utility import write_to_csv, blank_line, read_conf_C
from inputGenerationImprove.IPSG import IPS_Generation


class Generation(object):
    def __init__(self, _efsm):
        self.epoch = 10  # 生成test suits 最大个数
        self.max_level = 12  # 宽度遍历的最大层数
        self.model_name = _efsm.model_name
        self.inpParam_in_inpEvent = _efsm.get_inpParam_in_inpEvent()
        self.C = read_conf_C()
        self.ips = IPS_Generation(self.model_name)

    def _update_input_by_ips(self, top_sc, cur_transition_name):
        if cur_transition_name not in self.inpParam_in_inpEvent:
            return True
        if 't' in cur_transition_name and len(cur_transition_name) > 1:
            context_vars = top_sc.get_cur_context()
            _cur_trans_num = int(cur_transition_name[1:])
            _inp_params_val = self.ips.generate(_cur_trans_num, context_vars)
            if _inp_params_val:
                top_sc.set_cur_input_params(_inp_params_val)
                return True
            else:
                return False
        else:
            print("error")
            return False

    def _bfs_traverse(self, efsm, target_coverage):
        threshold = 6
        _path = None
        print("-----------start-------------{}-----".format(self.epoch))
        print("====================coverage================")
        _is_finded = False
        _cur_level = 0
        find_size = 0
        _collection = set()

        sc = efsm.get_cur_sc()
        sc_queue = queue.Queue()
        sc_queue.put(sc)

        while not sc_queue.empty() and _cur_level <= self.max_level and find_size < threshold and not _is_finded:
            que_length = len(sc_queue.queue)
            #  判断测试集是否满足特定的测试准则
            _tmp_sc_queue = copy.deepcopy(sc_queue.queue)
            _tmp_list = []
            _is_finded = False
            if self.C == "all_transition":
                _collection = set()

            while len(_tmp_sc_queue) and not _is_finded:
                _ts = _tmp_sc_queue.pop()
                _tmp_list.append(_ts)
                # judge coverage
                if self.C == "all_state":
                    _collection = _collection.union(_ts.get_cur_state().split())
                    if len(_collection) >= len(target_coverage):
                        _is_finded = self._all_state_coverage(target_coverage, _collection)
                elif self.C == "all_transition":
                    _collection = _collection.union(set(_ts.transition_path))
                    if len(_collection) >= len(target_coverage):
                        _is_finded = self._all_transition_coverage(target_coverage, _collection)
                elif self.C == "random":
                    _collection = _ts.transition_path
                    _is_finded = self._random_coverage(target_coverage, _collection)
                    if _is_finded:
                        while len(_tmp_sc_queue):
                            _ts = _tmp_sc_queue.pop()
                            _tmp_list.append(_ts)

                if _is_finded:
                    find_size += 1
                    print("-----------end--------------{}----".format(self.epoch))
                    self.epoch = self.epoch - 1
                    return _tmp_list

            while que_length > 0 and find_size < threshold and not _is_finded:
                que_length -= 1
                top_sc = sc_queue.get()
                cur_state = top_sc.get_cur_state()
                if cur_state == 's1':
                    efsm.init_sc_val(top_sc)
                _transitionList = efsm.get_next_trans(cur_state, list_flag=True)
                _transitionList = copy.deepcopy(_transitionList)
                if not _transitionList:
                    continue
                _trans_size = len(_transitionList)

                while _trans_size:
                    _trans_size = _trans_size - 1
                    if _is_finded:
                        break
                    _cur_transition = random.choice(_transitionList)
                    _transitionList.remove(_cur_transition)
                    if _cur_transition:
                        # if top_sc.transition_path and _cur_transition.trans_name == top_sc.transition_path[-1]:
                        #     continue

                        _tmpsc = copy.deepcopy(top_sc)
                        update_input_flag = self._update_input_by_ips(_tmpsc, _cur_transition.trans_name)
                        if not efsm.is_feasible(_cur_transition, _tmpsc):
                            continue
                        efsm.execute(_cur_transition, _tmpsc)
                        context_vars = _tmpsc.get_cur_context()
                        inp_params_val = _tmpsc.get_cur_input_params()
                        output_event = efsm.update_transition_output(_cur_transition, context_vars, inp_params_val)
                        _tmpsc.update_sc(_cur_transition.t_state, context_vars, inp_params_val,
                                         _cur_transition.trans_name, output_event)
                        # _cur_transition.set_sc(_tmpsc)
                        sc_queue.put(_tmpsc)
            _cur_level += 1

        print("-----------end--------------{}----".format(self.epoch))
        self.epoch = self.epoch - 1
        return None

    def _all_state_coverage(self, target, current):
        target_state = set(target)
        current_state = set(current)
        if target_state >= current_state:
            return True
        else:
            return False

    def _all_transition_coverage(self, target, current):
        target_path = set(target)
        current_path = set(current)
        if target_path >= current_path:
            return True
        else:
            return False

    def _random_coverage(self, max_len, current):
        if len(current) >= max_len:
            return True
        else:
            return False

    def _traverse(self, efsm_t):
        if self.C == "all_state":
            target_coverage = efsm_t.states_table
        elif self.C == "all_transition":
            target_coverage = efsm_t.trans_list
        elif self.C == "random":
            target_coverage = int(len(efsm_t.trans_list))
        test_suit_list = []

        _efsm_t = copy.deepcopy(efsm_t)
        while self.epoch:
            _sc_pool = self._bfs_traverse(_efsm_t, target_coverage)

            if _sc_pool:
                if len(_sc_pool) > 6:
                    continue
                _test_suit = []
                for sc in _sc_pool:
                    ts = {}
                    _context = sc.context_pool
                    _input = sc.input_pool
                    _state = sc.state_pool
                    _path = sc.transition_path
                    _output = sc.output_pool
                    _trace = []
                    _sc = []
                    for ind in range(len(_state)):
                        _tmp_sc = []
                        _tmp_sc.append(_state[ind])
                        for key, val in _context[ind].items():
                            _tmp_sc.append(val)
                        for key, val in _input[ind].items():
                            _tmp_sc.append(val)
                        _sc.append(tuple(_tmp_sc))

                    for ind in range(len(_path)):
                        _tmp_trace = []
                        for j in range(ind+1):
                            _tmp_trace.append(_path[j])
                        _trace.append(_tmp_trace)
                    _test_suit.append(sc.transition_path)

                    ts.__setitem__('context', _context)
                    ts.__setitem__('input', _input)
                    ts.__setitem__('path', _path)
                    ts.__setitem__('sc', _sc)
                    ts.__setitem__('trace', _trace)
                    ts.__setitem__('output', _output)
                    write_to_csv(ts, target_coverage, self.model_name)
                blank_line(self.model_name)
                test_suit_list.append(_test_suit)
        return test_suit_list

    def run(self, efsm):
        return self._traverse(efsm)
