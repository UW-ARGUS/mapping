import cv2
import torch
from vggt.models.vggt import VGGT
from vggt.utils.load_fn import load_and_preprocess_images
from vggt.visual_util import predictions_to_glb 
from vggt.utils.pose_enc import pose_encoding_to_extri_intri
from vggt.utils.geometry import unproject_depth_map_to_point_map

from pathlib import Path
import os
import fcntl
import glob
import time

device = "cuda" if torch.cuda.is_available() else "cpu"
model = VGGT()
_URL = "https://huggingface.co/facebook/VGGT-1B/resolve/main/model.pt"
model.load_state_dict(torch.hub.load_state_dict_from_url(_URL))


model.eval()
model = model.to(device)


SHARED_DIR = '../../gui/src/assets'
LOCK_FILE = os.path.join(SHARED_DIR, "batch.lock")

def wait_for_four_images(directory_path):
    """
    Blocks execution until exactly 4 .jpg files are found in the directory.
    Returns a sorted list of the file paths.
    """
    print(f"⏳ Waiting for exactly 4 .jpg files in '{directory_path}'...")
    
    while True:
        # 1. Grab all .jpg files in the folder
        search_pattern = os.path.join(directory_path, "*.jpg")
        jpg_files = glob.glob(search_pattern)
        
        # 2. Check the count
        current_count = len(jpg_files)
        
        if current_count == 4:
            print("\n✅ Exactly 4 images found! Unlocking pipeline...")
            return sorted(jpg_files)
            
        elif current_count > 4:
            # Helpful warning if Script 1 is dumping too many files
            print(f"\r⚠️ Found {current_count} images. Waiting for exactly 4...", end="")
        else:
            # Keep the terminal clean while waiting
            print(f"\r⏳ Currently see {current_count}/4 images. Waiting...", end="")
            
        # 3. CRITICAL: Sleep to prevent 100% CPU usage
        time.sleep(0.1)

def get_absolute_jpg_paths():
    # 3. Build your search pattern using the absolute directory
    search_pattern = os.path.join(SHARED_DIR, "*.jpg")
    
    # 4. Glob will now automatically return the FULL paths for every file
    jpg_files = glob.glob(search_pattern)
    
    return sorted(jpg_files)

final_glb_path = '../../gui/src/assets/mymy_room.glb'
temp_glb_path = '../../gui/src/assets/mymy_room_temp.glb'

while True:
    print("starting..")
    # Find all .jpg files in the current directory and get their names

    ready_images = wait_for_four_images(SHARED_DIR)

    with open(LOCK_FILE, 'r+') as lock_file:
            fcntl.flock(lock_file, fcntl.LOCK_EX)
            try:
                print("🔒 Lock acquired. Obtaining the images...")
                filenames = get_absolute_jpg_paths()
                images = load_and_preprocess_images(filenames).to(device)
            finally:
                fcntl.flock(lock_file, fcntl.LOCK_UN)
                print("🔓 Images acquired. Lock released.")

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
    glbscene.export(file_obj=temp_glb_path)

    os.replace(temp_glb_path, final_glb_path)
    print("finished!!")