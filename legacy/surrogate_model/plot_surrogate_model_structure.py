# %%
import torch
import numpy as np
from surrogate_model import ANN
import random
import os
os.makedirs(os.path.join('pic'), exist_ok=True)

# %%
model = ANN().cuda()
device = "cuda" if torch.cuda.is_available() else "cpu"

# Model visualization
input_names = ['optical parameter']
output_names = ['reflectance']
tensor_input = np.array([random.random() for i in range(10)])
tensor_input = torch.tensor(tensor_input)
tensor_input = tensor_input.to(torch.float32).to(device)
torch.onnx.export(model, tensor_input, os.path.join('pic', 'surrogate_model_structure.onnx'), input_names=input_names, output_names=output_names)