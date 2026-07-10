import torch
import warnings
import os

def initialize_device():
    if torch.cuda.is_available():
        return torch.device('cuda')
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device('mps')
    elif os.environ.get('HIP_VISIBLE_DEVICES'):
        return torch.device('cuda')
    elif hasattr(torch, 'hip') and torch.hip.is_available():
        return torch.device('cuda')
    else:
        return torch.device('cpu')
