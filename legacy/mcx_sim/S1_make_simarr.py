import json
import os
import numpy as np
import pandas as pd
import argparse
#%%
TISSUES = ['skin', 'fat', 'muscle', 'ijv', 'cca']

def Get_OPs_set(bound: dict, split_num: list, OP_type: str, savepath: str):    
    """
    _summary_ : getting the optical parameter(OP) set we want to simulate,
    split to training set and testing set for the purpose of training surrogate model.
    For testing set, we only get 10% datasize compare to training set.

    Args:
        bound (dict): {key : [upperbound, lowerbound]}
        split_num (list): [skin_OP_gen_num, fat_OP_gen_num, ...]
        OP_type (str): ['mus' | 'mua']
        savepath (str): saving directory

    Returns:
        OPs_set_train (pd.DataFrame),  OPs_set_test (pd.DataFrame) : each row correspond to one configuration.
    """
    
    assert len(bound) != len(split_num), 'tissues and split size not match'
    if OP_type == 'mus':
        assert split_num[-1] == split_num[-2], 'ijv mus should be same as cca mus'
    
    OPs_table_train = {}
    OPs_table_test = {}
    train_conditions = 1
    test_conditions = 1
    for i, tissue in enumerate(TISSUES):
        if OP_type == 'mus' and tissue == 'cca':
            break
        if OP_type =='mus' and tissue == 'ijv':    
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
            OPs_table_train[tissue] = list(np.linspace(bound[tissue][0]-15, bound[tissue][1], 2*split_num[i]))[::2]  # simulate low scattering region
            OPs_table_test[tissue] = list(np.linspace(bound[tissue][0]-15, bound[tissue][1], 2*split_num[i]))[1::2]  # simulate low scattering region
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
        else:
            OPs_table_train[tissue] = list(np.linspace(bound[tissue][0], bound[tissue][1], 2*split_num[i]))[::2]
            OPs_table_test[tissue] = list(np.linspace(bound[tissue][0], bound[tissue][1], 2*split_num[i]))[1::2]
        train_conditions *= len(OPs_table_train[tissue])
        test_conditions *= len(OPs_table_test[tissue])

    # get train set
    OPs_set_train = np.zeros((train_conditions,len(TISSUES)))
    idx = 0
    for skin_OP in OPs_table_train['skin']:
        for subcuit_OP in OPs_table_train['fat']:
            for muscle_OP in OPs_table_train['muscle']:
                for ijv_OP in OPs_table_train['ijv']:
                    if OP_type == 'mus': # cca mus = ijv mus
                        OPs_set_train[idx][0] = skin_OP
                        OPs_set_train[idx][1] = subcuit_OP
                        OPs_set_train[idx][2] = muscle_OP
                        OPs_set_train[idx][3] = ijv_OP
                        OPs_set_train[idx][4] = OPs_set_train[idx][3]
                        idx += 1
                    elif OP_type == 'mua':
                        for cca_OP in OPs_table_train['cca']:
                            OPs_set_train[idx][0] = skin_OP
                            OPs_set_train[idx][1] = subcuit_OP
                            OPs_set_train[idx][2] = muscle_OP
                            OPs_set_train[idx][3] = ijv_OP
                            OPs_set_train[idx][4] = cca_OP
                            idx += 1
    np.save(os.path.join(savepath, f'{OP_type}_set_train.npy'), OPs_set_train)
    OPs_set_train = pd.DataFrame(OPs_set_train, columns=TISSUES)
    OPs_set_train.to_csv(os.path.join(savepath, f'{OP_type}_set_train.csv'), index=False)
    
    # get test set
    OPs_set_test = np.zeros((test_conditions,len(TISSUES)))
    idx = 0
    for skin_OP in OPs_table_test['skin']:
        for subcuit_OP in OPs_table_test['fat']:
            for muscle_OP in OPs_table_test['muscle']:
                for ijv_OP in OPs_table_test['ijv']:
                    if OP_type == 'mus': # cca mus = ijv mus
                        OPs_set_test[idx][0] = skin_OP
                        OPs_set_test[idx][1] = subcuit_OP
                        OPs_set_test[idx][2] = muscle_OP
                        OPs_set_test[idx][3] = ijv_OP
                        OPs_set_test[idx][4] = OPs_set_test[idx][3]
                        idx += 1
                    elif OP_type == 'mua':
                        for cca_OP in OPs_table_test['cca']:
                            OPs_set_test[idx][0] = skin_OP
                            OPs_set_test[idx][1] = subcuit_OP
                            OPs_set_test[idx][2] = muscle_OP
                            OPs_set_test[idx][3] = ijv_OP
                            OPs_set_test[idx][4] = cca_OP
                            idx += 1
    # randomly choose 10% datasize 
    if OP_type == 'mus':
        np.random.shuffle(OPs_set_test)
        OPs_set_test = OPs_set_test[:int(OPs_set_test.shape[0]*0.1)]
        
    np.save(os.path.join(savepath, f'{OP_type}_set_test.npy'), OPs_set_test)
    OPs_set_test = pd.DataFrame(OPs_set_test, columns=TISSUES)
    OPs_set_test.to_csv(os.path.join(savepath, f'{OP_type}_set_test.csv'), index=False)
    
    
    return OPs_set_train,  OPs_set_test
#%%
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # mus
    parser.add_argument("--num_skin_mus", type=int, help="Split n points from skin_mus upper bound to lower bound")
    parser.add_argument("--num_fat_mus", type=int, help="Split n points from fat_mus upper bound to lower bound")
    parser.add_argument("--num_muscle_mus", type=int, help="Split n points from muscle_mus upper bound to lower bound")
    parser.add_argument("--num_blood_mus", type=int, help="Split n points from blood_mus upper bound to lower bound")
    # mua
    parser.add_argument("--num_skin_mua", type=int, help="Split n points from skin_mua upper bound to lower bound")
    parser.add_argument("--num_fat_mua", type=int, help="Split n points from fat_mua upper bound to lower bound")
    parser.add_argument("--num_muscle_mua", type=int, help="Split n points from muscle_mua upper bound to lower bound")
    parser.add_argument("--num_ijv_mua", type=int, help="Split n points from ijv_mua upper bound to lower bound")
    parser.add_argument("--num_cca_mua", type=int, help="Split n points from cca_mua upper bound to lower bound")
    args = parser.parse_args()
    
    # Get Mus set
    with open(os.path.join("OPs_used", "mus_bound.json"), "r") as f:
        mus_bound = json.load(f)
    mus_tissues = ['skin', 'fat', 'muscle', 'ijv', 'cca']
    split_num = [args.num_skin_mus, args.num_fat_mus, args.num_muscle_mus, args.num_blood_mus, args.num_blood_mus]
    savepath = 'OPs_used'
    mus_set = Get_OPs_set(bound = mus_bound, 
                          split_num = split_num, 
                          OP_type = 'mus', 
                          savepath = savepath)

    # Get Mua set
    with open(os.path.join("OPs_used", "mua_bound.json"), "r") as f:
        mua_bound = json.load(f)
    mua_tissues = ['skin', 'fat', 'muscle', 'ijv', 'cca']
    split_num = [args.num_skin_mua, args.num_fat_mua, args.num_muscle_mua, args.num_ijv_mua, args.num_cca_mua]
    savepath = 'OPs_used'
    mua_set = Get_OPs_set(bound = mua_bound, 
                          split_num = split_num, 
                          OP_type = 'mua', 
                          savepath = savepath)


