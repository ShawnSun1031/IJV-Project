import os
from myDataset import myDataset
import numpy as np

result_folder = "prediction_model_formula8"
# load train dataset
train_folder = os.path.join("dataset", result_folder, "train")
train_ds = myDataset(train_folder)
print(f'train dataset size : {len(train_ds)}')

# load test dataset
test_folder = os.path.join("dataset", result_folder, "test")
test_ds = myDataset(test_folder)
print(f'test dataset size : {len(test_ds)}')

find_abnormal = []
for idx in range(len(train_ds)):
    # print(f'now processing_train_{idx}...')
    x, y, id, mua_rank, _ = train_ds[idx]
    x, y = x.numpy(), y.numpy()
    if y == 0:
        if np.sum(x) != 0:
            print(f'train_{id}_0_SO2_abnormal!!')
            find_abnormal.append(id)
    elif y != 0:
        if np.where(x==0,1,0).any():
            print(f'train_{id}_abnormal!!')
            find_abnormal.append(id)

test_find_abnormal = []
for idx in range(len(test_folder)):
    # print(f'now processing_test_{idx}...')
    x, y, id, mua_rank, _ = train_ds[idx]
    x, y = x.numpy(), y.numpy()
    if y == 0:
        if np.sum(x) != 0:
            print(f'test_{id}_0_SO2_abnormal!!')
            test_find_abnormal.append(id)
    elif y != 0:
        if np.where(x==0,1,0).any():
            print(f'test_{id}_abnormal!!')
            test_find_abnormal.append(id)