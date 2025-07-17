import torch
from vggt.models.vggt import VGGT

print("==== DOWNLOADING VGGT MODEL =====")
model = VGGT()
_URL = "https://huggingface.co/facebook/VGGT-1B/resolve/main/model.pt"
model.load_state_dict(torch.hub.load_state_dict_from_url(_URL))
print("==== FINISHED DOWNLOADING VGGT MODEL =====")