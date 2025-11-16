# %%
import matplotlib.pyplot as plt
from ANN_models import PredictionModel, PredictionModel2, PredictionModel3, PredictionModel4, PredictionModel_single_SDS, PredictionModel5
import os 
import json
import torch
import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib as mpl
import sys
os.chdir(sys.path[0])
# Default settings
mpl.rcParams.update(mpl.rcParamsDefault)
plt.style.use("seaborn-darkgrid")
# %%
result_folder = "prediction_model_formula24_chromophore_rand_ab"
subject = 'ctchen'
# %%
os.makedirs(os.path.join("pic", result_folder, subject), exist_ok=True)
with open(os.path.join("OPs_used", "SO2.json"), 'r') as f:
    SO2 = json.load(f)
    test_SO2 = SO2['test_SO2']
with open(os.path.join("model_save", result_folder, subject, 'trlog.json'), 'r') as f:
    config = json.load(f)
test_loader = torch.load(os.path.join("model_save", result_folder, subject, 'test_loader.pth'))
model = PredictionModel5(neuronsize=5).cuda()
# model = PredictionModel_single_SDS().cuda()
# model = PredictionModel2().cuda()
model.load_state_dict(torch.load(config['best_model']))
model.eval()

def cal_R_square(y_true, y_pred):
    y_bar = np.mean(y_true)
    numerator = np.sum(np.square(y_true-y_pred))
    denominator = np.sum(np.square(y_true-y_bar))
    R_square = 1 - numerator/denominator
    
    return R_square
# df = {'predic' : [], 'true' : [] , 'error' : [], 'abs_error' : []}
# for i in range(800):
#     df[f'data_value_{i}'] = []
    
# for batch_idx, (data,target, _, _, _) in tqdm(enumerate(test_loader)):
#     data,target = data.to(torch.float32).cuda(), target.to(torch.float32).cuda()
#     output = model(data)
#     output = output.detach().cpu().numpy()
#     target = target.detach().cpu().numpy()
#     for idx in range(output.shape[0]):
#         df['predic'].append(output[idx][0]*100)
#         df['true'].append(target[idx][0]*100)
#         df['error'].append(100*(output[idx][0] - target[idx][0]))
#         df['abs_error'].append(np.abs(100*(output[idx][0] - target[idx][0])))
        
#     for row_idx, one_row in enumerate(data):
#         for idx in range(one_row.shape[0]):
#             df[f'data_value_{idx}'] += [one_row[idx].item()]

# df = pd.DataFrame(df)
# df = df.sort_values('abs_error', ascending=False)
# df.to_csv(os.path.join("pic", result_folder, subject, "RMSE.csv"), index=False)
        
    

#%%
plt.figure()
for batch_idx, (data,target, _,_,_) in enumerate(test_loader):
    data,target = data.to(torch.float32).cuda(), target.to(torch.float32).cuda()
    output = model(data)
    output = output.detach().cpu().numpy()
    target = target.detach().cpu().numpy()
    if batch_idx == 0:
        error = 100*(output - target)
        accumulate_RMSE = 100*(output - target)
        accumulate_output = output
        accumulate_target = target
    else:
        error = np.concatenate((error, 100*(output - target)))
        accumulate_RMSE = np.concatenate((accumulate_RMSE, 100*(output - target)))
        accumulate_output = np.concatenate((accumulate_output, output))
        accumulate_target = np.concatenate((accumulate_target, target))
    if batch_idx == 0:
        plt.plot(target*100,output*100, 'r.', markersize=5, label= 'predict')
        plt.plot(target*100,target*100,'b', label = 'optimal')
    else:
        plt.plot(target*100,output*100, 'r.', markersize=5)
        plt.plot(target*100,target*100,'b')

RMSE = np.sqrt(np.mean(np.square(accumulate_RMSE)))
R_square = cal_R_square(y_true=accumulate_target, y_pred=accumulate_output)
plt.title(f"based on SO2=70% \n RMSE:{RMSE:.2f}% $R^{2}$:{R_square:.3f}")
plt.xlabel("truth $\u0394$SO2(%)")
plt.ylabel("predict $\u0394$SO2(%)")
# plt.legend(loc='center left', bbox_to_anchor=(1.05, 0.5),
#           fancybox=True, shadow=True)
plt.legend()
plt.savefig(os.path.join("pic", result_folder, subject, "RMSE.png"), dpi=300, format='png', bbox_inches='tight')
plt.close()
# plt.show()

# %%
for batch_idx, (data,target, _,_,_) in enumerate(test_loader):
    data,target = data.to(torch.float32).cuda(), target.to(torch.float32).cuda()
    output = model(data)
    output = output.detach().cpu().numpy()
    target = target.detach().cpu().numpy()
    if batch_idx == 0:
        error = 100*(output - target)
        RMSE = 100*(output - target)
    else:
        error = np.concatenate((error, 100*(output - target)))
        RMSE = np.concatenate((RMSE, 100*(output - target)))

mean = np.mean(error)
std = np.std(error)
plt.figure()
n,bin, pack = plt.hist(error, bins=50)
plt.vlines([mean+2*std, mean-2*std], 0, max(n), 'r', label='$\mu$$\pm$2*$\sigma$')
plt.text(mean+2*std, max(n)+20, f'{mean+2*std:.2f}%')
plt.text(mean-2*std, max(n)+20, f'{mean-2*std:.2f}%')
plt.xlabel('error(prediction-true)')
plt.ylabel('count')
plt.title('error histogram')
plt.legend()
plt.savefig(os.path.join("pic", result_folder, subject, "hist.png"), dpi=300, format='png', bbox_inches='tight')
plt.close()
# plt.show()

plt.figure()
epoch = config['epoch']
epoch = [i for i in range(epoch)]
train_loss = config['train_loss']
test_loss = config['test_loss']
plt.plot(epoch, train_loss, label='train loss')
plt.plot(epoch, test_loss, label='test loss')
plt.xlabel('epoch #')
plt.ylabel('RMSE loss')
plt.legend()
plt.savefig(os.path.join("pic", result_folder, subject, "loss.png"), dpi=300, format='png', bbox_inches='tight')
plt.close()

