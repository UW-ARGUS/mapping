import cv2
import torch
from vggt.models.vggt import VGGT
from vggt.utils.load_fn import load_and_preprocess_images
from vggt.visual_util import predictions_to_glb 
from vggt.utils.pose_enc import pose_encoding_to_extri_intri
from vggt.utils.geometry import unproject_depth_map_to_point_map

from pathlib import Path


device = "cuda" if torch.cuda.is_available() else "cpu"
model = VGGT()
_URL = "https://huggingface.co/facebook/VGGT-1B/resolve/main/model.pt"
model.load_state_dict(torch.hub.load_state_dict_from_url(_URL))


model.eval()
model = model.to(device)

while True:
    print("starting..")
    # Find all .jpg files in the current directory and get their names
    filenames = [file.name for file in Path('.').glob('*.jpg')]
    
    images = load_and_preprocess_images(filenames).to(device)
    with torch.no_grad():
        predictions = model(images)

    # Convert pose encoding to extrinsic and intrinsic matrices
    print("Converting pose encoding to extrinsic and intrinsic matrices...")
    extrinsic, intrinsic = pose_encoding_to_extri_intri(predictions["pose_enc"], images.shape[-2:])
    predictions["extrinsic"] = extrinsic
    predictions["intrinsic"] = intrinsic

    # Convert tensors to numpy
    for key in predictions.keys():
        if isinstance(predictions[key], torch.Tensor):
            predictions[key] = predictions[key].cpu().numpy().squeeze(0)  # remove batch dimension
    predictions['pose_enc_list'] = None # remove pose_enc_list

    # Generate world points from depth map
    print("Computing world points from depth map...")
    depth_map = predictions["depth"]  # (S, H, W, 1)
    world_points = unproject_depth_map_to_point_map(depth_map, predictions["extrinsic"], predictions["intrinsic"])
    predictions["world_points_from_depth"] = world_points

    # Clean up
    torch.cuda.empty_cache()

    glbscene = predictions_to_glb(
        predictions,
        conf_thres=0.10,
        filter_by_frames="all",
        mask_black_bg=False,
        mask_white_bg=False,
        show_cam=False,
        mask_sky=False,
        target_dir=None,
        prediction_mode="Predicted Pointmap",
    )
    glbscene.export(file_obj='../../gui/src/assets/mymy_room.glb')
    print("finished!!")