import os

subject = "Julie"

#%% make directory for training folder and testing folder of subject
os.makedirs(os.path.join("dataset", subject, 'train', 'ijv_large'), exist_ok=True)
os.makedirs(os.path.join("dataset", subject, 'train', 'ijv_small'), exist_ok=True)
os.makedirs(os.path.join("dataset", subject, 'test', 'ijv_large'), exist_ok=True)
os.makedirs(os.path.join("dataset", subject, 'test', 'ijv_small'), exist_ok=True)

