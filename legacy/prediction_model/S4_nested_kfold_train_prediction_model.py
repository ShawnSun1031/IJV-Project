import torch
import torch.nn as nn
from torch.utils.data import DataLoader, SubsetRandomSampler
from ANN_models import PredictionModel, PredictionModel2, PredictionModel3, PredictionModel4, PredictionModel5
from myDataset import myDataset
from sklearn.model_selection import KFold
import pandas as pd
import numpy as np
import time
import json
import os

with open(os.path.join("OPs_used", "bloodConc.json"), "r") as f:
    bloodConc = json.load(f)
    bloodConc = bloodConc['bloodConc']
with open(os.path.join("OPs_used", "SO2.json"), 'r') as f:
    SO2 = json.load(f)
    train_SO2 = SO2['train_SO2']
    test_SO2 = SO2['test_SO2']

#%% line notify
import requests

def lineNotifyMessage(msg):
    headers = {
        "Authorization": "Bearer " + "cfmFeEIO0W5qO2IHlbKaXdjVKoZ3TLAJiALq7chfIwq", 
        "Content-Type" : "application/x-www-form-urlencoded"
    }

    payload = {'message': msg }
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    return r.status_code


#%% set random seeds fix result
def setup_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    # random.seed(seed)
    # torch.backends.cudnn.deterministic = True
    

#%% train model
def train(model, optimizer, criterion, train_loader, test_loader, epoch, batch_size, lr, save_folder):
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
        for batch_idx, (data,target,_,_,_) in enumerate(train_loader):
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
        min_loss = test(trlog, test_loader, ep, min_loss, save_folder)
        
    return trlog

def test(trlog, test_loader, ep, min_loss, save_folder):
    model.eval()
    ts_loss = 0
    for batch_idx, (data,target,_,_,_) in enumerate(test_loader):
        data,target = data.to(torch.float32).cuda(), target.to(torch.float32).cuda()
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output,target)
        ts_loss += loss.item()
        
    print(f"[test] batch:{batch_idx}/{len(test_loader)}({100*batch_idx/len(test_loader):.2f}%) loss={ts_loss/len(test_loader)}")
    trlog['test_loss'].append(ts_loss/len(test_loader))
    
    if min_loss > ts_loss/len(test_loader):
        min_loss = ts_loss/len(test_loader)
        trlog['best_model'] = os.path.join("model_save", result_folder, save_folder,f"ep_{ep}_loss_{min_loss}.pth")
        torch.save(model.state_dict(), os.path.join("model_save", result_folder, save_folder,f"ep_{ep}_loss_{min_loss}.pth"))
            
    return min_loss


if __name__ == "__main__":
    result_folder = "prediction_model_formula8"
    os.makedirs(os.path.join("model_save", result_folder), exist_ok=True)
    #%%
    # set up random seed
    setup_seed(19981031)
    EPOCH = 20
    
    # get testing grid hyper parameters
    hyper_set_pd = {
        'hp_idx' : [],
        'batch_size' : [],
        'learning_rate' : [],
        'neuron' : [],
    }
    hyper_set = []
    batch_size_set = [512,256,128]
    learning_rate_set = [0.0001, 0.00005, 0.00003] 
    neuron_set = [5,3,1] # neuron should be integer
    count = 0
    for batch_size in batch_size_set:
        for learning_rate in learning_rate_set:
            for neuron in neuron_set:
                hyper_set.append((neuron, learning_rate, batch_size))
                hyper_set_pd['hp_idx'] += [count]
                hyper_set_pd['batch_size'] += [batch_size]
                hyper_set_pd['learning_rate'] += [learning_rate]
                hyper_set_pd['neuron'] += [neuron]
                count += 1
    hyper_set_pd = pd.DataFrame(hyper_set_pd)
    hyper_set_pd.to_csv(os.path.join("model_save", result_folder,'hyper_set.csv'), index=False)
    
    # k-fold cross validation
    kfold = KFold(n_splits=5) # 10-fold cross validation
    fold_losses = []
    
    # load train dataset
    train_folder = os.path.join("dataset", result_folder, "train")
    train_ds = myDataset(train_folder)
    
    # load test dataset
    test_folder = os.path.join("dataset", result_folder, "test")
    test_ds = myDataset(test_folder)
    
    # nested k-fold cross validation
    record_all_set = {
        'out_fold_idx' : [],
        'in_fold_idx' : [],
        'hp_idx' : [],
        'neuron' : [],
        'learning_rate' : [],
        'batch_size' : [],
        'test_loss' : []
    }
    for out_fold_idx, (out_train_ids, out_val_ids) in enumerate(kfold.split(train_ds)): 
        msg = f'outer folder #{out_fold_idx}  train size: {len(out_train_ids)}, val size: {len(out_val_ids)}'
        lineNotifyMessage(msg)
        print(f'outer folder #{out_fold_idx}  train size: {len(out_train_ids)}, val size: {len(out_val_ids)}')
        inner_best_set = {'in_fold_idx' : [],
                          'hp_idx' : [],
                          'neuron' : [],
                          'learning_rate' : [],
                          'batch_size' : [],
                          'test_loss' : []}
        for in_fold_idx, (in_train_ids, in_val_ids) in enumerate(kfold.split(out_train_ids)): 
            print(f'inner folder #{in_fold_idx}  train size: {len(in_train_ids)}, val size: {len(in_val_ids)}')
            # gridsearch hyperparameter
            for hp_idx, (neuron, learning_rate, batch_size) in enumerate(hyper_set):
                # set model from beginning 
                model = PredictionModel5(neuronsize=neuron).cuda()
                criterion = nn.MSELoss()
                optimizer = torch.optim.Adam(params=model.parameters(), lr=learning_rate)

                # load data
                train_sampler = SubsetRandomSampler(out_train_ids[in_train_ids]) # mapping to train_ds index
                val_sampler = SubsetRandomSampler(out_train_ids[in_val_ids]) # mapping to train_ds index
                train_loader = DataLoader(dataset=train_ds, batch_size=batch_size, sampler=train_sampler)
                val_loader = DataLoader(dataset=train_ds, batch_size=batch_size, sampler=val_sampler)
                
                # train on train-loader, validate on val-loader
                save_folder=f'outidx_{out_fold_idx}_inidx_{in_fold_idx}_hpidx_{hp_idx}'
                os.makedirs(os.path.join("model_save", result_folder, save_folder), exist_ok=True)
                trlog = train(model=model, 
                              optimizer=optimizer, 
                              criterion=criterion, 
                              train_loader=train_loader,
                              test_loader=val_loader,
                              epoch=EPOCH, 
                              batch_size=batch_size, 
                              lr=learning_rate,
                              save_folder=save_folder)
                
                # save log
                trlog['train_size'] = len(in_train_ids)
                trlog['test_size'] = len(in_val_ids)
                trlog['neuron'] = neuron
                with open(os.path.join("model_save", result_folder, save_folder, "trlog.json"), 'w') as f:
                    json.dump(trlog, f, indent=4)
                    
                # save inner result
                inner_best_set['in_fold_idx'] += [in_fold_idx]
                inner_best_set['hp_idx'] += [hp_idx]
                inner_best_set['neuron'] += [neuron]
                inner_best_set['batch_size'] += [batch_size]
                inner_best_set['learning_rate'] += [learning_rate]
                inner_best_set['test_loss'] += [min(trlog['test_loss'])]
                
                # record_all result
                record_all_set['out_fold_idx'] += [out_fold_idx]
                record_all_set['in_fold_idx'] += [in_fold_idx]
                record_all_set['hp_idx'] += [hp_idx]
                record_all_set['neuron'] += [neuron]
                record_all_set['batch_size'] += [batch_size]
                record_all_set['learning_rate'] += [learning_rate]
                record_all_set['test_loss'] += [min(trlog['test_loss'])]
                
        # get best inner setting
        inner_best_set = pd.DataFrame(inner_best_set)
        inner_best_set = inner_best_set.sort_values(by='test_loss').iloc[0]
        inner_best_neuron = int(inner_best_set['neuron'])
        inner_best_batch_size = int(inner_best_set['batch_size'])
        inner_best_learning_rate = inner_best_set['learning_rate']
        
        # set model from beginning 
        model = PredictionModel5(neuronsize=inner_best_neuron).cuda()
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(params=model.parameters(), lr=inner_best_learning_rate)
        
        # load data
        train_sampler = SubsetRandomSampler(out_train_ids)
        val_sampler = SubsetRandomSampler(out_val_ids) 
        train_loader = DataLoader(dataset=train_ds, batch_size=inner_best_batch_size, sampler=train_sampler)
        val_loader = DataLoader(dataset=train_ds, batch_size=inner_best_batch_size, sampler=val_sampler)
                        
        # train on train-loader, validate on val-loader
        save_folder=f'outidx_{out_fold_idx}'
        os.makedirs(os.path.join("model_save", result_folder, save_folder), exist_ok=True)
        trlog = train(model=model, 
                        optimizer=optimizer, 
                        criterion=criterion, 
                        train_loader=train_loader,
                        test_loader=val_loader,
                        epoch=EPOCH, 
                        batch_size=inner_best_batch_size, 
                        lr=inner_best_learning_rate,
                        save_folder=save_folder)
        
        # save log
        trlog['train_size'] = len(train_loader)*inner_best_batch_size
        trlog['test_size'] = len(val_loader)*inner_best_batch_size
        trlog['neuron'] = neuron
        with open(os.path.join("model_save", result_folder, save_folder, "trlog.json"), 'w') as f:
            json.dump(trlog, f, indent=4)
            
        # record_all result
        record_all_set['out_fold_idx'] += [out_fold_idx]
        record_all_set['in_fold_idx'] += [in_fold_idx]
        record_all_set['hp_idx'] += [hp_idx]
        record_all_set['neuron'] += [neuron]
        record_all_set['batch_size'] += [batch_size]
        record_all_set['learning_rate'] += [learning_rate]
        record_all_set['test_loss'] += [min(trlog['test_loss'])]  
        
        # send progress message
        msg = f'outer fold : {out_fold_idx}, best neuron : {inner_best_neuron}, best batch_size : {inner_best_batch_size}, best lr : {inner_best_learning_rate}'
        lineNotifyMessage(msg)
    
    record_all_set = pd.DataFrame(record_all_set)  
    record_all_set.to_csv(os.path.join("model_save", result_folder, f'all_result.csv'), index=False)    

    #%% test the best setting on testing set using all training data 
    EPOCH = 50
    # get best setting
    best_set = record_all_set.sort_values(by='test_loss').iloc[0]
    best_neuron = int(best_set['neuron'])
    best_batch_size = int(best_set['batch_size'])
    best_learning_rate = best_set['learning_rate']
       
    # set model from beginning 
    model = PredictionModel5(neuronsize=best_neuron).cuda()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(params=model.parameters(), lr=best_learning_rate)
    
    # load data
    train_loader = DataLoader(dataset=train_ds, batch_size=best_batch_size)
    test_loader = DataLoader(dataset=test_ds, batch_size=best_batch_size)
    
    # train on train-loader, validate on test-loader
    save_folder=f'all_train_data_on_test_set'
    os.makedirs(os.path.join("model_save", result_folder, save_folder), exist_ok=True)
    trlog = train(model=model, 
                    optimizer=optimizer, 
                    criterion=criterion, 
                    train_loader=train_loader,
                    test_loader=test_loader,
                    epoch=EPOCH, 
                    batch_size=best_batch_size, 
                    lr=best_learning_rate,
                    save_folder=save_folder)
    
    # save log
    trlog['train_size'] = len(train_ds)
    trlog['test_size'] = len(test_ds)
    trlog['neuron'] = neuron
    with open(os.path.join("model_save", result_folder, save_folder, "trlog.json"), 'w') as f:
        json.dump(trlog, f, indent=4)