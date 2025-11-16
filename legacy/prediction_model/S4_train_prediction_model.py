import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from ANN_models import PredictionModel, PredictionModel2, PredictionModel3, PredictionModel4, PredictionModel_single_SDS, PredictionModel5
from myDataset import myDataset
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

#%% train model
def train(model, optimizer, criterion, train_loader, epoch, batch_size, lr):
    trlog = {}
    trlog['epoch'] = epoch
    trlog['batch_size'] = batch_size
    trlog['learning_rate'] = lr
    trlog['train_loss'] = []
    trlog['val_loss'] = []
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
        min_loss = test(trlog,ep,min_loss)
        val(trlog,ep)
        
    return trlog

def val(trlog,ep):
    model.eval()
    ts_loss = 0
    for batch_idx, (data,target,_,_,_) in enumerate(val_loader):
        data,target = data.to(torch.float32).cuda(), target.to(torch.float32).cuda()
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output,target)
        ts_loss += loss.item()
        
    print(f"[val] batch:{batch_idx}/{len(val_loader)}({100*batch_idx/len(val_loader):.2f}%) loss={ts_loss/len(val_loader)}")
    trlog['val_loss'].append(ts_loss/len(val_loader))
    

def test(trlog,ep,min_loss):
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
        trlog['best_model'] = os.path.join("model_save",result_folder, subject, f"ep_{ep}_loss_{min_loss}.pth")
        torch.save(model.state_dict(), os.path.join("model_save",result_folder, subject, f"ep_{ep}_loss_{min_loss}.pth"))
            
    return min_loss


if __name__ == "__main__":
    result_folder = "prediction_model_formula24_chromophore_rand_ab"
    subject = 'ctchen'
    #%%
    EPOCH = 3
    BATCH_SIZE = 128
    lr=0.00003
    os.makedirs(os.path.join("model_save", result_folder, subject), exist_ok=True)
    
    train_folder = os.path.join("dataset", result_folder, subject, "train")
    train_dataset = myDataset(train_folder)
    print(f'train dataset size : {len(train_dataset)}')
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

    val_folder = os.path.join("dataset", result_folder, subject, "val")
    val_dataset = myDataset(val_folder)
    print(f'val dataset size : {len(val_dataset)}')
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
    # torch.save(val_loader, os.path.join("model_save", result_folder, 'val_loader.pth'))
    
    test_folder = os.path.join("dataset", result_folder, subject, "test")
    test_dataset = myDataset(test_folder)
    print(f'test dataset size : {len(test_dataset)}')
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)
    # torch.save(test_loader, os.path.join("model_save", result_folder, 'test_loader.pth'))

    # train model
    start_time = time.time()
    model = PredictionModel5(neuronsize=5).cuda()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()
    trlog = train(model, optimizer, criterion, train_loader, EPOCH, BATCH_SIZE, lr)
    end_time = time.time()
    print(f'elapsed time : {end_time-start_time:.3f} sec')
    trlog['elapsed_time'] = end_time-start_time
    trlog['train_size'] = len(train_dataset)
    trlog['val_size'] = len(val_dataset)
    trlog['test_size'] = len(test_dataset)

    # save result
    with open(os.path.join("model_save", result_folder, subject, "trlog.json"), 'w') as f:
        json.dump(trlog, f, indent=4)  
    torch.save(test_loader, os.path.join("model_save", result_folder, subject, 'test_loader.pth'))     
            
            
        
        