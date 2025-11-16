import numpy as np
import torch
from torch.utils.data.sampler import SubsetRandomSampler
from torch.utils.data import Dataset, DataLoader

#%% data preprocessing
class dataload(Dataset):
    def __init__(self, root: str, mus_max: np.ndarray, mus_min: np.ndarray, mua_max: np.ndarray, mua_min: np.ndarray):
        # load dataset then split to x and y
        xy = np.load(root)
        self.x = torch.from_numpy(xy[:,:10])
        self.y = torch.from_numpy(xy[:,[10,11]]) # index 10 for SDS1, index 11 for SDS2
        
        # input normalization
        self.x_max = torch.from_numpy(np.concatenate((mus_max, mua_max)))
        self.x_min = torch.from_numpy(np.concatenate((mus_min, mua_min)))
        self.x = (self.x - self.x_min) / (self.x_max - self.x_min)
        
        # output normalization
        self.y = -torch.log(self.y)
        
        self.n_samples = xy.shape[0]

                
    def __getitem__(self, index):
        
        return self.x[index], self.y[index]
        
    def __len__(self):
        
        return self.n_samples

def data_preprocess(dataset, batch_size, test_split, shuffle_dataset, random_seed):
    # create data indice for training and testing splits
    dataset_size = len(dataset)
    indices = list(range(dataset_size))
    # count out split size
    split = int(np.floor(test_split*dataset_size))
    if shuffle_dataset:
        np.random.seed(random_seed)
        np.random.shuffle(indices)
    train_indices, test_indices = indices[split:],indices[:split]

    # creating data samplers and loaders:
    train_sampler = SubsetRandomSampler(train_indices)
    test_sampler = SubsetRandomSampler(test_indices)
    
    train_loader = DataLoader(dataset, batch_size=batch_size, sampler=train_sampler)
    test_loader = DataLoader(dataset, batch_size=batch_size, sampler=test_sampler)
    
    return train_loader, test_loader