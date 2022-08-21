# coding=utf-8
import queue
import copy
import random
from itertools import combinations
from inputGenerationImprove.IPSG import IPS_Generation
from PathGeneration.utility import write_to_csv, blank_line


class TraverseEFSM(object):
    def __init__(self, model_name):
        self.epoch = 20  # 生成test suits 最大个数
        self.max_level = 15  # 宽度遍历的最大层数
        self.model_name = model_name

    def _combination_trans(self, trans_list, size):
        comb = combinations(trans_list, size)
        return list(comb)

    def _update_input_by_ips(self, top_sc, cur_transition_name):
        if 't' in cur_transition_name and len(cur_transition_name) > 1:
            context_vars = top_sc.get_cur_context()
            inp_params_val = top_sc.get_cur_input_params()
            _cur_trans_num = int(cur_transition_name[1:])
            _counter = context_vars.get('counter')
            _input = int(context_vars.get('input'))
            _number = context_vars.get('number')
            ips = IPS_Generation(self.model_name)
            _inp_val_list = ips.generate(_cur_trans_num, [_counter, _input, _number])  # optional ,_NUM ,_block
            inp_params_val['optional'] = _inp_val_list[0]
            inp_params_val['NUM'] = _inp_val_list[1]
            inp_params_val['block'] = _inp_val_list[2]
        else:
            print("error")

    def _bfs_traverse(self, efsm, target_trans):
        threshold = 5
        _path = None
        print("-----------start------------------")
        print("====================coverage================")
        _is_finded = False
        _cur_level = 0
        find_size = 0
        _sc_pool = list()

        sc = efsm.get_cur_sc()
        sc_queue = queue.Queue()
        sc_queue.put(sc)

        while not sc_queue.empty() and _cur_level <= self.max_level and find_size < threshold and not _is_finded:
            que_length = len(sc_queue.queue)
            #  判断测试集是否满足特定的测试准则
            _tmp_sc_queue = copy.deepcopy(sc_queue.queue)
            _path = set()
            _tmp_list = []
            while len(_tmp_sc_queue):
                _ts = _tmp_sc_queue.pop()
                _path = _path.union(set(_ts.transition_path))
                _tmp_list.append(_ts)
                # judge coverage
                if len(_path) >= len(target_trans):
                    _is_finded = self._transition_coverage_criterion(target_trans, _path)
                    if _is_finded:
                        find_size += 1
                        return _tmp_list
            while que_length > 0 and find_size < threshold and not _is_finded:
                que_length -= 1
                top_sc = sc_queue.get()
                cur_state = top_sc.get_cur_state()
                _transitionList = efsm.get_next_trans(cur_state, list_flag=True)
                _transitionList = copy.deepcopy(_transitionList)
                if not _transitionList:
                    continue
                _trans_size = len(_transitionList)
                ### hard code for input scn model
                #top_sc.input_params['qos'] = random.randint(1, 2)

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
                        _sc_pool.append(_tmpsc)
                        self._update_input_by_ips(_tmpsc, _cur_transition.trans_name)
                        if not efsm.is_feasible(_cur_transition, _tmpsc):
                            continue
                        efsm.execute(_cur_transition, _tmpsc)
                        context_vars = _tmpsc.get_cur_context()
                        inp_params_val = _tmpsc.get_cur_input_params()
                        _tmpsc.update_sc(_cur_transition.t_state, context_vars, inp_params_val,
                                         _cur_transition.trans_name)
                        # _cur_transition.set_sc(_tmpsc)
                        # 对于单条测试用例的判断
                        # _path = _tmpsc.transition_path
                        # # judge coverage
                        # if len(set(_path)) >= len(target_trans):
                        #     _is_finded = self._transition_coverage_criterion(target_trans, _path)
                        #     if _is_finded:
                        #         print(_path)
                        #         print(_tmpsc._context_pool)
                        #         find_size += 1
                        #         return _sc_pool, _path
                        sc_queue.put(_tmpsc)
            _cur_level += 1

        print("-----------end------------------")
        return None

    def _all_transition_coverage(self, efsm, current_path):
        target_path = set(efsm.trans_list)
        current_path = set(current_path)
        if target_path >= current_path:
            return True
        else:
            return False

    def _transition_coverage(self, efsm):
        target_trans = efsm.trans_list
        len1 = self.epoch
        test_suit_list = []
        while len1:
            len1 = len1 - 1
            _sc_pool = self._bfs_traverse(efsm, target_trans)

            if _sc_pool:
                _test_suit = []
                for sc in _sc_pool:
                    ts = {}
                    ts.__setitem__('context', sc.context_pool)
                    ts.__setitem__('input', sc.input_pool)
                    ts.__setitem__('path', sc.transition_path)
                    _test_suit.append(sc.transition_path)
                    write_to_csv(ts, target_trans)
                blank_line()
                test_suit_list.append(_test_suit)
        return test_suit_list

    def _transition_coverage_criterion(self, target, current):
        target_path = set(target)
        current_path = set(current)
        if target_path >= current_path:
            return True
        else:
            return False

    def run(self, efsm):
        return self._transition_coverage(efsm)
