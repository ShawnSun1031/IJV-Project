import os
import json
import pandas as pd
import numpy as np
import sys
from joblib import Parallel, delayed

#%%
with open(os.path.join("OPs_used", "bloodConc.json"), "r") as f:
    bloodConc = json.load(f)
    bloodConc = bloodConc['bloodConc']
with open(os.path.join("OPs_used", "wavelength.json"), 'r') as f:
    wavelength = json.load(f)
    wavelength = wavelength['wavelength']
with open(os.path.join("OPs_used", "SO2.json"), 'r') as f:
    SO2 = json.load(f)
    train_SO2 = SO2['train_SO2']
    test_SO2 = SO2['test_SO2']
#%%
def gen_prediction_input(id : int, blc : int, dataset_type: str, SO2_used : list, outputpath : str):
    # for id in range(num):
    #     print(f'now processing {dataset_type}_{id}...')
    #     for blc in bloodConc:
    print(f'now processing {dataset_type}_{id}...')
    prediction_input = np.zeros((len(SO2_used),2*len(wavelength)*len(wavelength)+5)) # T1_large_SDS1/SDS2 T1_small_SDS1/SDS2 T2_large_SDS1/SDS2 T2_small_SDS1/SDS2 bloodConc ans id
    # prediction_input = np.zeros((len(SO2_used),40+5))
    for i, s in enumerate(SO2_used):
        surrogate_result_T1 = pd.read_csv(os.path.join("dataset", "surrogate_result", subject, dataset_type, 
                                                    f'bloodConc_{blc}', 'SO2_0.7', f'{id}_{dataset_type}.csv'))
        surrogate_result_T2 = pd.read_csv(os.path.join("dataset", "surrogate_result", subject, dataset_type, 
                                                    f'bloodConc_{blc}', f'SO2_{s}', f'{id}_{dataset_type}.csv'))
        
        # filter abnormal 
        T2_SDS1_Rmax_Rmin = (surrogate_result_T2['smallIJV_SDS1'].to_numpy() / surrogate_result_T2['largeIJV_SDS1'].to_numpy()).mean()
        T1_SDS1_Rmax_Rmin = (surrogate_result_T1['smallIJV_SDS1'].to_numpy() / surrogate_result_T1['largeIJV_SDS1'].to_numpy()).mean()
        T2_SDS2_Rmax_Rmin = (surrogate_result_T2['smallIJV_SDS2'].to_numpy() / surrogate_result_T2['largeIJV_SDS2'].to_numpy()).mean()
        T1_SDS2_Rmax_Rmin = (surrogate_result_T1['smallIJV_SDS2'].to_numpy() / surrogate_result_T1['largeIJV_SDS2'].to_numpy()).mean()

        if (T2_SDS1_Rmax_Rmin > 1) & (T1_SDS1_Rmax_Rmin > 1) & (T2_SDS2_Rmax_Rmin > 1) & (T1_SDS2_Rmax_Rmin > 1):
            SDS1_delta_logRmaxRmin = np.log((surrogate_result_T2['smallIJV_SDS1'].to_numpy() / surrogate_result_T2['largeIJV_SDS1'].to_numpy())) - np.log((surrogate_result_T1['smallIJV_SDS1'].to_numpy() / surrogate_result_T1['largeIJV_SDS1'].to_numpy()))
            SDS2_delta_logRmaxRmin = np.log((surrogate_result_T2['smallIJV_SDS2'].to_numpy() / surrogate_result_T2['largeIJV_SDS2'].to_numpy())) - np.log((surrogate_result_T1['smallIJV_SDS2'].to_numpy() / surrogate_result_T1['largeIJV_SDS2'].to_numpy()))
            prediction_input[i][:20] = SDS1_delta_logRmaxRmin
            prediction_input[i][20:40] = SDS2_delta_logRmaxRmin
            for wl_idx in range(len(wavelength)):
                T2_large_SDS2 = surrogate_result_T2['largeIJV_SDS2'].to_numpy()
                T2_large_SDS1 = surrogate_result_T2['largeIJV_SDS1'][wl_idx]
                T1_large_SDS2 = surrogate_result_T1['largeIJV_SDS2'].to_numpy()
                T1_large_SDS1 = surrogate_result_T1['largeIJV_SDS1'][wl_idx]

                T2_small_SDS2 = surrogate_result_T2['smallIJV_SDS2'].to_numpy()
                T2_small_SDS1 = surrogate_result_T2['smallIJV_SDS1'][wl_idx]
                T1_small_SDS2 = surrogate_result_T1['smallIJV_SDS2'].to_numpy()
                T1_small_SDS1 = surrogate_result_T1['smallIJV_SDS1'][wl_idx]
                
                # normalize with spec mean
                T2_large = T2_large_SDS2/T2_large_SDS1
                # T2_large = (T2_large - T2_large.mean()) / (T2_large.max() - T2_large.min())
                T1_large = T1_large_SDS2/T1_large_SDS1
                # T1_large = (T1_large - T1_large.mean()) / (T1_large.max() - T1_large.min())
                R_large = T1_large/T2_large
                R_large = (R_large - R_large.min() + 1e-9) / (R_large.max() - R_large.min() + 1e-9)
                prediction_input[i][wl_idx*20 : wl_idx*20+20] = np.log(R_large)
                
                T2_small = T2_small_SDS2/T2_small_SDS1
                # T2_small = (T2_small - T2_small.mean()) / (T2_small.max() - T2_small.min())
                T1_small = T1_small_SDS2/T1_small_SDS1
                # T1_small = (T1_small - T1_small.mean()) / (T1_small.max() - T1_small.min())
                R_small = T1_small/T2_small
                R_small = (R_small - R_small.min() + 1e-9) / (R_small.max() - R_small.min() + 1e-9)
                prediction_input[i][400+wl_idx*20 : 400+wl_idx*20+20] = np.log(R_small)
            
                
            prediction_input[i][800] = blc
            prediction_input[i][801] = s - 0.7 # answer
            prediction_input[i][802] = id # for analyzing used
            prediction_input[i][803] = -1 # mua_rank
            prediction_input[i][804] = -1 # muscle_SO2

    # filter abnormal
    non_zero_ridx = np.where(prediction_input==0, 0, 1).sum(axis=1)
    non_zero_ridx = np.where(non_zero_ridx==0)[0]
    prediction_input = np.delete(prediction_input, non_zero_ridx, axis=0)
    if prediction_input.size == 0:
        pass
    else:
        np.save(os.path.join("dataset", outputpath, subject, dataset_type, f"{id}_blc_{blc}.npy"), prediction_input)


if __name__ == "__main__":
    train_num = 10
    val_num = 2
    test_num = 2
    outputpath = 'prediction_model_formula24_chromophore_rand_ab'
    subject = 'ctchen'
    #%%
    os.makedirs(os.path.join("dataset", outputpath, subject, "train"), exist_ok=True)
    os.makedirs(os.path.join("dataset", outputpath, subject, "val"), exist_ok=True)
    os.makedirs(os.path.join("dataset", outputpath, subject, "test"), exist_ok=True)
    
    products = []
    for id in range(train_num):
        for blc in bloodConc:
            products.append((id,blc))
            
    Parallel(n_jobs=1)(delayed(gen_prediction_input)(id,blc,'train',train_SO2,outputpath) for id, blc in products)
    
    products = []
    for id in range(val_num):
        for blc in bloodConc:
            products.append((id,blc))
            
    Parallel(n_jobs=1)(delayed(gen_prediction_input)(id,blc,'val',test_SO2,outputpath) for id, blc in products)
    
    products = []
    for id in range(test_num):
        for blc in bloodConc:
            products.append((id,blc))
    Parallel(n_jobs=1)(delayed(gen_prediction_input)(id,blc,'test',test_SO2,outputpath) for id, blc in products)
    