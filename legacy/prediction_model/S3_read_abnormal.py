import os
import numpy as np
import pandas as pd

train_SO2 = [
        0.4,
        0.45,
        0.5,
        0.55,
        0.6,
        0.65,
        0.7,
        0.75,
        0.8,
        0.85,
        0.9
    ]

bloodConc = [
        166,
        156,
        160,
        164,
        149,
        162,
        155,
        172,
        145,
        153,
        174,
        147,
        138,
        170,
        143,
        168,
        151,
        141,
        139,
        158
    ]

log = {'blc' : [],
       'SO2' : [],
       'ID' : []}
result_folder = "surrogate_result"
for blc in bloodConc:
    print(f'Now processing {blc}!')
    for SO2 in train_SO2:
        for ID in range(10000):
            data = pd.read_csv(os.path.join('dataset', result_folder, 'train', f'bloodConc_{blc}', f'SO2_{SO2}', f'{ID}_train.csv')).to_numpy()
            if np.where(data<=0,1,0).any():
                print(f'ABNORMAL!! blc:{blc}, SO2:{SO2}, ID:{ID} !!')
                log['blc'].append(blc)
                log['SO2'].append(SO2)
                log['ID'].append(ID)


# id 4958 blc 151
# id 1804 blc 162,155,170,151
# a = np.load(os.path.join('dataset', result_folder, 'train', f"1804_blc_{162}.npy"))
# b = a[[0,1,2,3,4,5,7,8,9,10],:]
# x = b[:800]
# print(np.where(x==0))
# print(x[5,:])



