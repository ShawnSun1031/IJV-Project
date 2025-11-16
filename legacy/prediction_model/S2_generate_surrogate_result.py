import json
import os
import random
import numpy as np
import pandas as pd
import torch
from ANN_models import SurrogateModel
from joblib import Parallel, delayed

#%% load all we need file
with open(os.path.join("OPs_used","mus_spectrum.json"), "r") as f:
    mus_spectrum = json.load(f)
with open(os.path.join("OPs_used","mua_spectrum.json"), "r") as f:
    mua_spectrum = json.load(f)
with open(os.path.join("OPs_used", "bloodConc.json"), "r") as f:
    bloodConc = json.load(f)
    bloodConc = bloodConc['bloodConc']
with open(os.path.join("OPs_used", "wavelength.json"), 'r') as f:
    used_wl = json.load(f)
    used_wl = used_wl['wavelength']
with open(os.path.join("OPs_used", "SO2.json"), 'r') as f:
    SO2 = json.load(f)
    train_SO2 = SO2['train_SO2']
    test_SO2 = SO2['test_SO2']
mus_set = pd.read_csv(os.path.join("OPs_used","mus_set.csv")).to_numpy()
mua_set = pd.read_csv(os.path.join("OPs_used","mua_set.csv")).to_numpy()
skin_mua_set = pd.read_csv(os.path.join("OPs_used", "mua_chromophore", "skin_mua_spectrum.csv")).to_numpy()
fat_mua_set = pd.read_csv(os.path.join("OPs_used", "mua_chromophore", "fat_mua_spectrum.csv")).to_numpy()
muscle_mua_set = pd.read_csv(os.path.join("OPs_used", "mua_chromophore", "muscle_mua_spectrum.csv")).to_numpy()
cca_mua_set = pd.read_csv(os.path.join("OPs_used", "mua_chromophore", "cca_mua_spectrum.csv")).to_numpy()


#%% functions
def preprocess_data(arr, mus_set, mua_set):
    OPs_normalized = torch.from_numpy(arr[:,:10]) 
    max_mus = np.max(mus_set, axis=0)[:5]
    max_mua = np.max(mua_set, axis=0)[:5]
    x_max = torch.from_numpy(np.concatenate((max_mus,max_mua)))
    min_mus = np.min(mus_set, axis=0)[:5]
    min_mua = np.min(mua_set, axis=0)[:5]
    x_min = torch.from_numpy(np.concatenate((min_mus,min_mua)))
    OPs_normalized = (OPs_normalized - x_min) / (x_max - x_min)
    SO2_used = torch.from_numpy(arr[:,10]) # SO2
    bloodConc_used = torch.from_numpy(arr[:,11]) # bloodConc
    
    return OPs_normalized, SO2_used, bloodConc_used

def gen_surrogate_result(blc:int, used_SO2:list, mus:dict, mua:dict, dataset_type:str, rangdom_gen:list, id:int):
    print(f'now processing {dataset_type}{id}...')
    surrogate_concurrent_data = {"wavelength" : [f'{wl} nm' for wl in used_wl],
                        "skin_mus": mus["skin"][rangdom_gen[0]],
                        "fat_mus": mus["fat"][rangdom_gen[1]],
                        "muscle_mus": mus["muscle"][rangdom_gen[2]],
                        "ijv_mus": mus["blood"][rangdom_gen[3]],
                        "cca_mus": mus["blood"][rangdom_gen[3]],
                        "skin_mua": skin_mua_set[rangdom_gen[5]],
                        "fat_mua": fat_mua_set[rangdom_gen[6]]}
    for s in used_SO2:
        surrogate_input = {"wavelength" : [f'{wl} nm' for wl in used_wl],
                        "skin_mus": mus["skin"][rangdom_gen[0]],
                        "fat_mus": mus["fat"][rangdom_gen[1]],
                        "muscle_mus": mus["muscle"][rangdom_gen[2]],
                        "ijv_mus": mus["blood"][rangdom_gen[3]],
                        "cca_mus": mus["blood"][rangdom_gen[3]],
                        "skin_mua": skin_mua_set[rangdom_gen[5]],
                        "fat_mua": fat_mua_set[rangdom_gen[6]],
                        "muscle_mua" : muscle_mua_set[rangdom_gen[7]],
                        "ijv_mua": mua_spectrum[f'ijv_bloodConc_{blc}_bloodSO2_{s}'],
                        "cca_mua": cca_mua_set[rangdom_gen[8]],
                        "answer": s,
                        "bloodConc": blc}
        surrogate_input = pd.DataFrame(surrogate_input)
        
        # get surrogate model output
        arr = surrogate_input.to_numpy()
        arr = arr[:,1:].astype(np.float64) # OPs_used
        OPs_normalized, SO2_used, bloodConc_used = preprocess_data(arr, mus_set, mua_set)
        large_reflectance = large_ijv_model(OPs_normalized.to(torch.float32).cuda())
        large_reflectance = torch.exp(-large_reflectance).detach().cpu().numpy()
        small_reflectance = small_ijv_model(OPs_normalized.to(torch.float32).cuda())
        small_reflectance = torch.exp(-small_reflectance).detach().cpu().numpy()
        
        # save reflectance
        surrogate_input['largeIJV_SDS1'] = large_reflectance[:,0]
        surrogate_input['largeIJV_SDS2'] = large_reflectance[:,1]
        surrogate_input['smallIJV_SDS1'] = small_reflectance[:,0]
        surrogate_input['smallIJV_SDS2'] = small_reflectance[:,1]
        
        # save result
        surrogate_input = surrogate_input.drop(columns=['wavelength', 'skin_mus', 'fat_mus', 'muscle_mus', 'ijv_mus', 
                                'cca_mus', 'skin_mua', 'fat_mua', 'answer', 'bloodConc']) # drop these values for saving memory
        
        surrogate_input.to_csv(os.path.join("dataset", "surrogate_result", subject, dataset_type, f'bloodConc_{blc}', f'SO2_{s}', f'{id}_{dataset_type}.csv'), index=False) 
    surrogate_concurrent_data = pd.DataFrame(surrogate_concurrent_data)
    surrogate_concurrent_data.to_csv(os.path.join("dataset", "surrogate_result", subject, dataset_type, f'{id}_{dataset_type}_concurrent.csv'), index=False)
        
        
if __name__ == "__main__":
    train_num = 10
    val_num = 2
    test_num = 2
    subject = 'ctchen'
    
    # load surrogate model
    large_ijv_model = SurrogateModel().cuda()
    large_ijv_model.load_state_dict(torch.load(os.path.join("surrogate_model",subject, "large_ANN_model.pth")))
    small_ijv_model = SurrogateModel().cuda()
    small_ijv_model.load_state_dict(torch.load(os.path.join("surrogate_model",subject, "small_ANN_model.pth")))
    
    #%train spectrum number
    total_num = 10

    # get mus spectrum 
    mus = {}
    tissue = ['skin', 'fat', 'muscle', 'blood']
    for t in tissue:
        mus[t] = pd.DataFrame(mus_spectrum[t]).to_numpy()

    # get mua spectrum 
    mua = {}
    tissue = ["skin", "fat", "cca", "muscle"]
    for t in tissue:
        mua[t] = pd.DataFrame(mua_spectrum[t]).to_numpy()
    
    # generate trainset
    for blc in bloodConc:
        for s in train_SO2:
            os.makedirs(os.path.join("dataset", "surrogate_result", subject, 'train', f'bloodConc_{blc}', f'SO2_{s}'), exist_ok=True)
    products = []
    for id in range(train_num):
        # print(f'now processing train_{id}...')
        rangdom_gen = [3*random.randint(0, total_num-1),3*random.randint(0, total_num-1),3*random.randint(0, total_num-1),
                       3*random.randint(0, total_num-1),3*random.randint(0, total_num-1),3*random.randint(0, total_num-1),
                       3*random.randint(0, total_num-1),3*random.randint(0, total_num-1),3*random.randint(0, total_num-1)] # 0, 3, 6, 9, ... for training spectrum
        for blc in bloodConc:
            products.append((id,rangdom_gen, blc))
    Parallel(n_jobs=-5)(delayed(gen_surrogate_result)(blc, train_SO2, mus, mua, "train", rangdom_gen, id) for id, rangdom_gen, blc in products)
    
    # # generate valset
    for blc in bloodConc:
        for s in test_SO2:
            os.makedirs(os.path.join("dataset", "surrogate_result", subject, 'val', f'bloodConc_{blc}', f'SO2_{s}'), exist_ok=True)
    products = []
    for id in range(val_num):
        # print(f'now processing test_{id}...')
        rangdom_gen = [3*random.randint(0, total_num-1)+1,3*random.randint(0, total_num-1)+1,3*random.randint(0, total_num-1)+1,
                       3*random.randint(0, total_num-1)+1,3*random.randint(0, total_num-1)+1,3*random.randint(0, total_num-1)+1,
                       3*random.randint(0, total_num-1)+1,3*random.randint(0, total_num-1)+1,3*random.randint(0, total_num-1)+1] # 1, 4, 7, 10, ... for validation spectrum
        for blc in bloodConc:
            products.append((id,rangdom_gen, blc))
    Parallel(n_jobs=-5)(delayed(gen_surrogate_result)(blc, test_SO2, mus, mua, "val", rangdom_gen, id) for id, rangdom_gen, blc in products)
    
    
    # # generate testset
    for blc in bloodConc:
        for s in test_SO2:
            os.makedirs(os.path.join("dataset", "surrogate_result", subject, 'test', f'bloodConc_{blc}', f'SO2_{s}'), exist_ok=True)
    products = []
    for id in range(test_num):
        # print(f'now processing test_{id}...')
        rangdom_gen = [3*random.randint(0, total_num-1)+2,3*random.randint(0, total_num-1)+2,3*random.randint(0, total_num-1)+2,
                       3*random.randint(0, total_num-1)+2,3*random.randint(0, total_num-1)+2,3*random.randint(0, total_num-1)+2,
                       3*random.randint(0, total_num-1)+2,3*random.randint(0, total_num-1)+2,3*random.randint(0, total_num-1)+2] # 2, 5, 8, 11, ... for testing spectrum
        for blc in bloodConc:
            products.append((id,rangdom_gen, blc))
    Parallel(n_jobs=-5)(delayed(gen_surrogate_result)(blc, test_SO2, mus, mua, "test", rangdom_gen, id) for id, rangdom_gen, blc in products)
    
