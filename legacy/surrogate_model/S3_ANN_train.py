import numpy as np
from torch.utils.data import Dataset, DataLoader
import torch
import torch.nn as nn
import os
import json
from Preprocessing import dataload, data_preprocess
from surrogate_model import ANN

#%% setting seed to make the result have reproducibility
def set_seed(seed):
    np.random.seed(seed)  
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed) 
   
#%% train model
def train(model, optimizer, criterion, train_loader, epoch, batch_size, lr):
    trlog = {}
    trlog['epoch'] = epoch
    trlog['batch_size'] = batch_size
    trlog['learning_rate'] = lr
    trlog['train_loss'] = []
    trlog['test_loss'] = []
    min_loss = 100000
    for ep in range(epoch):
        model.train()
        tr_loss = 0
        for batch_idx, (data,target) in enumerate(train_loader):
            data,target = data.to(torch.float32).cuda(), target.to(torch.float32).cuda()
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output,target)
            tr_loss += loss.item()
            loss.backward()
            optimizer.step()
            if batch_idx % int(0.1*len(train_loader)) == 0:
                print(f"[train] ep:{ep}/{epoch}({100*ep/epoch:.2f}%) batch:{batch_idx}/{len(train_loader)}({100*batch_idx/len(train_loader):.2f}%)\
                      loss={tr_loss/(batch_idx+1)}")
        trlog['train_loss'].append(tr_loss/len(train_loader))
        min_loss = test(trlog,ep,min_loss)
        
    
    return trlog

def test(trlog,ep,min_loss):
    model.eval()
    ts_loss = 0
    for batch_idx, (data,target) in enumerate(test_loader):
        data,target = data.to(torch.float32).cuda(), target.to(torch.float32).cuda()
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output,target)
        ts_loss += loss.item()
        
    print(f"[test] batch:{batch_idx}/{len(test_loader)}({100*batch_idx/len(test_loader):.2f}%) loss={ts_loss/len(test_loader)}")
    trlog['test_loss'].append(ts_loss/len(test_loader))
    
    if min_loss > ts_loss/len(test_loader):
        min_loss = ts_loss/len(test_loader)
        trlog['best_model'] = os.path.join("model_save", outputfolder, f"ep_{ep}_loss_{min_loss}.pth")
        torch.save(model.state_dict(), os.path.join("model_save",outputfolder, f"ep_{ep}_loss_{min_loss}.pth"))
            
    return min_loss
    
#%%   
if __name__ == "__main__":
    # ====================== Modify your setting here ====================== #
    subject = "Julie"
    epoch = 10
    batch_size = 128
    lr = 0.00003
    seed = 19981031
    # ====================================================================== #
    
    # setting seed to make the result have reproducibility
    set_seed(seed) 
    
    # get mua, mus boundary for normalization
    parent_folder = os.path.abspath(os.path.join(os.getcwd(),".."))
    with open(os.path.join(parent_folder, "mcx_sim", "OPs_used", "mus_bound.json"), "r") as f:
        mus_bound_dict = json.load(f)
        mus_max = np.array([mus_bound_dict['skin'][0], mus_bound_dict['fat'][0], mus_bound_dict['muscle'][0],
                            mus_bound_dict['ijv'][0], mus_bound_dict['cca'][0]])
        mus_min = np.array([mus_bound_dict['skin'][1], mus_bound_dict['fat'][1], mus_bound_dict['muscle'][1],
                            mus_bound_dict['ijv'][1], mus_bound_dict['cca'][1]])
    with open(os.path.join(parent_folder, "mcx_sim", "OPs_used", "mua_bound.json"), "r") as f:
        mua_bound_dict = json.load(f)
        mua_max = np.array([mua_bound_dict['skin'][0], mua_bound_dict['fat'][0], mua_bound_dict['muscle'][0],
                            mua_bound_dict['ijv'][0], mua_bound_dict['cca'][0]])
        mua_min = np.array([mua_bound_dict['skin'][1], mua_bound_dict['fat'][1], mua_bound_dict['muscle'][1],
                            mua_bound_dict['ijv'][1], mua_bound_dict['cca'][1]])
    
    # debugging
    assert np.where((mus_max>mus_min), 1, 0).all(), "[DEBUG] mus_max should greater than mus_min !!!"
    assert np.where((mua_max>mua_min), 1, 0).all(), "[DEBUG] mua_max should greater than mua_min !!!"
    
    #%% Run training 
    ijv_type_set = ["ijv_large", "ijv_small"]
    for ijv_type in ijv_type_set:
        # get dataset
        trainset = dataload(root=os.path.join("dataset", subject, f"{ijv_type}_train.npy"),
                        mus_max=mus_max,
                        mus_min=mus_min,
                        mua_max=mua_max,
                        mua_min=mua_min)
        testset = dataload(root=os.path.join("dataset", subject, f"{ijv_type}_test.npy"),
                        mus_max=mus_max,
                        mus_min=mus_min,
                        mua_max=mua_max,
                        mua_min=mua_min)
        
        # get training loader and testing loader 
        train_loader = DataLoader(trainset, batch_size=batch_size, shuffle=True)
        test_loader = DataLoader(testset, batch_size=batch_size, shuffle=False)
        
        # make output folder
        outputfolder = os.path.join(subject, f'{subject}_{ijv_type}_surrogate_model')
        os.makedirs(os.path.join("model_save", outputfolder), exist_ok=True)

        # train model
        model = ANN().cuda()
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        criterion = nn.MSELoss()
        trlog = train(model, optimizer, criterion, train_loader, epoch, batch_size, lr)
        
        # save result
        with open(os.path.join("model_save", outputfolder, "trlog.json"), 'w') as f:
            json.dump(trlog, f, indent=4)
        torch.save(train_loader, os.path.join("model_save", outputfolder, "train_loader.pth"))
        torch.save(test_loader, os.path.join("model_save", outputfolder, "test_loader.pth"))