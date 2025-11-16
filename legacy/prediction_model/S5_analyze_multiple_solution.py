# %%
import os
import numpy as np
from glob import glob
from tqdm import tqdm
import pandas as pd
from joblib import Parallel, delayed


# %%
def get_similarity(data, spec1_df):
    topK = 10
    spec1 = np.empty((input_size))
    for i in range(input_size):
        spec1[i] = spec1_df[f'data_value_{i}']
    spec1_SO2 = np.round(spec1_df['true'])
    compare_data = data[np.where(np.round(100*data[:,41])!=spec1_SO2)]
    diff_spec = (spec1[:input_size] - compare_data[:, :input_size])/np.abs(compare_data[:, :input_size])*100
    similarity = np.mean(np.abs(diff_spec), axis=1)
    similarity_total_idx = np.argsort(similarity)
    similarity_topK_idx = similarity_total_idx[:topK]

    similarity_topK = similarity[similarity_topK_idx]
    spec_topK = compare_data[similarity_topK_idx]
    similarity_mean = np.mean(similarity)
    similarity_std = np.std(similarity)
    row = {'similarity_mean' : similarity_mean, 'similarity_std': similarity_std}
    # for idx in range(spec1.shape[0]):
    #     row[f'spec1_value_{idx}'] = spec1[idx]
    for idx in range(similarity_topK.shape[0]):
        row[f'similarity_{idx}'] = similarity_topK[idx]
    for i in range(1):
        for j in range(spec_topK.shape[1]):
            row[f'similar_spec{i}_value_{j}'] = spec_topK[i,j]
    
    return row

if __name__ == '__main__':
    subject = 'ctchen'
    result = 'prediction_model_formula3'
    input_size = 800
    os.makedirs(os.path.join('result', subject, result), exist_ok=True)
    
    dataset_fileset = glob(os.path.join("dataset", result, "test", "*.npy"))
    dataset_fileset.sort(key=lambda x : int(x.split("/")[-1].split("_")[0]))
    get_size = np.load(dataset_fileset[0])
    data = np.empty((get_size.shape[0]*len(dataset_fileset), get_size.shape[1]))
    for idx, dataset_file in enumerate(dataset_fileset):
        print(f'now processing {dataset_file}')
        data[idx*get_size.shape[0]:(idx+1)*get_size.shape[0]] = np.load(dataset_file)
   
    data = data[~np.any(data[:,:input_size] == 0, axis=1)] # remove any zero reflectance
    
    analysis_data = pd.read_csv(os.path.join('pic', result, 'RMSE.csv'))
    # res = Parallel(n_jobs=-5)(delayed(get_similarity)(data, analysis_data.iloc[idx]) for idx in tqdm(range(analysis_data.shape[0])))
    res = Parallel(n_jobs=-5)(delayed(get_similarity)(data, analysis_data.iloc[idx]) for idx in tqdm(range(10)))
    res = pd.DataFrame(res)
    analysis_data = pd.concat((analysis_data, res), axis=1)
    analysis_data.to_csv(os.path.join('result', subject, result, "similar_analysis.csv"), index=False)



