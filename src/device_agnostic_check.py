import torch

if torch.cuda.is_available():
    print("GPU available")
else:
    print("GPU not available")