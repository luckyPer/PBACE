# coding=utf-8
from EFSMparser.load import LoadEFSM
from PathGeneration.traverseEFSMSCN import Generation as G1
from PathGeneration.traverseEFSM_NO_Guard import Generation as G2
from PathGeneration.utility import read_conf_m

if __name__ == "__main__":
    SPEC_FILE = read_conf_m()
    l = LoadEFSM()
    efsm_obj = l.load_efsm(SPEC_FILE)
    #efsm_obj.get_guard_content('t2')

    g = G2(efsm_obj)
    g.run(efsm_obj)
