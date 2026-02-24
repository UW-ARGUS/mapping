"""
ARGUS 3D mapping reconstruction.
"""

import cv2
import torch
from vggt.models.vggt import VGGT
from vggt.utils.load_fn import load_and_preprocess_images
from vggt.visual_util import predictions_to_glb 
from vggt.utils.pose_enc import pose_encoding_to_extri_intri
from vggt.utils.geometry import unproject_depth_map_to_point_map
import time

print("===== huh whatL =====")


from modules.image_data import ImageData
from modules.image_receiver.image_receiver_manager import ImageReceiverManager
from utilities.message_queue import MessageQueue


def main(device, model) -> int:
    """
    Main function.
    """
    # TODO: These values should come from a config file
    base_port = 5000
    number_of_connections = 4
    image_to_mapping_queue = MessageQueue[ImageData](maxsize=100)

    image_receiver_manager = ImageReceiverManager(
        base_port=base_port,
        number_of_connections=number_of_connections,
        image_queue=image_to_mapping_queue,
    )

    try:
        image_receiver_manager.start_workers()

        while True:
            print("waiting for images...")
            while image_to_mapping_queue.size() < 4:
                pass

            time.sleep(2)
            filenames = []
            for i in range(4):
                image_data = image_to_mapping_queue.get()
                filenames.append(f"../../gui/src/assets/received_{image_data.device_id}.jpg")
                cv2.imwrite(filenames[i], image_data.image)

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

            print("DONE EXPORT YAYYYYYYYYYYYYY")

            # if image_data is None:
            #     continue
    
            # # timestamp = time.time()
            # filename = f"received_{image_data.device_id}.jpg"
            # cv2.imwrite(filename, image_data.image)
            # print("SUCCESS SAVED PHOTO")
            # # cv2.putText(
            # #     image_data.image,
            # #     f"{image_data.timestamp:.3f}",
            # #     (10, 20),  # Top-left corner
            # #     cv2.FONT_HERSHEY_SIMPLEX,  # Font type
            # #     0.5,  # Font size
            # #     (255, 0, 255),  # Fuschia
            # #     1,  # Line thickness
            # # )

            # # cv2.imshow(f"Image display {image_data.device_id}", image_data.image)

            # # if cv2.waitKey(1) & 0xFF == ord("q"):
            # #     break
    finally:
        image_receiver_manager.stop_workers()

    return 0


if __name__ == "__main__":
    print("==== SETTING UP VGGT MODEL =====")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = VGGT()
    _URL = "https://huggingface.co/facebook/VGGT-1B/resolve/main/model.pt"
    model.load_state_dict(torch.hub.load_state_dict_from_url(_URL))


    model.eval()
    model = model.to(device)
    print("==== FINISH SETTING UP VGGT MODEL =====")


    result_main = main(device, model)
    if result_main < 0:
        print(f"ERROR: Status code: {result_main}")

    print("Done!")
