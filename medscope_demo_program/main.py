import medscope
from read_nii_to_numpy import nii_file_to_numpy
from remote_auto_fetch import remote_auto_fetch
import numpy as np
import pickle

import sys
import os

try:
    from .Ap200_BoneAndTipInfo import Ap200_BoneAndTipInfo, AbsBoneAndTipInfo
    from .FakeBoneAndTipInfo import FakeBoneAndTipInfo
    from . import utils
except:
    from Ap200_BoneAndTipInfo import Ap200_BoneAndTipInfo, AbsBoneAndTipInfo
    from FakeBoneAndTipInfo import FakeBoneAndTipInfo
    import utils

# download from github
remote_auto_fetch(
    "https://github.com/GGN-2015/medscope_demo_project/releases/download/binary_file/CT.nii",
    utils.CT_FILE, md5_hash="58C6F98ED7C3E9DB4B5CD265CADD5882")

remote_auto_fetch(
    "https://github.com/GGN-2015/medscope_demo_project/releases/download/SegmentationCT/SegmentationCT.nii",
    utils.SEG_CT_FILE, md5_hash="4d9cb97bd42241b45cd0f4a75769ca04")

def make_and_load_pickle(nii_filepath:str, min_val:float, max_val:float) -> np.ndarray:
    assert nii_filepath.endswith(".nii")
    # Load CT file
    pickle_path = nii_filepath[:-4] + ".pickle"

    if not os.path.isfile(pickle_path):
        print(f"Generating {pickle_path} ...")
        arr = nii_file_to_numpy(nii_filepath, 1.0, 1.0, 1.0)
        arr[arr <= min_val] = min_val
        arr[arr >= max_val] = max_val
        arr_norm = (arr - np.min(arr)) / (np.max(arr) - np.min(arr) + 1e-8)
        arr_uint8 = (arr_norm * 255).astype(np.uint8)
        with open(pickle_path, "wb") as fp: # Create pickle
            pickle.dump(arr_uint8, fp)  
    else:
        print(f"Loading {pickle_path} ...")
        with open(pickle_path, "rb") as fp: # Read pickle
            arr_uint8 = pickle.load(fp)
    return arr_uint8

def main(device_ip_addr:str="192.168.1.10", use_fake_device:bool=False, mask_alpha:float=0.7):

    # 构建 RGB 通道
    ct_arr_uint8 = make_and_load_pickle(utils.CT_FILE, 3, 160)
    print("CT.shape:", ct_arr_uint8.shape)
    ct_arr_uint8 = np.repeat(ct_arr_uint8[np.newaxis, ...], 3, axis=0)

    # 掩码
    seg_arr_uint8 = make_and_load_pickle(utils.SEG_CT_FILE, 0, 1)
    print("SegmentationCT.shape:", seg_arr_uint8.shape)

    # seg_arr_uint8 的尺寸必须和 ct_arr_uint8 在一个通道上相同
    assert seg_arr_uint8.shape == ct_arr_uint8.shape[1:]

    # 把掩码打到红色通道
    ct_arr_uint8 = ct_arr_uint8.astype(np.float64)
    ct_arr_uint8[0, :, :, :] = np.maximum(ct_arr_uint8[0, :, :], (seg_arr_uint8 >= 0.5) * 255)
    ct_arr_uint8[1, :, :, :] [seg_arr_uint8 >= 0.5] *= mask_alpha
    ct_arr_uint8[2, :, :, :] [seg_arr_uint8 >= 0.5] *= mask_alpha
    ct_arr_uint8 = ct_arr_uint8.astype(np.uint8)

    # Fill in your ip addr
    if not use_fake_device:
        print("Connecting ap200 device ...")
        bone_and_tip_info:AbsBoneAndTipInfo = Ap200_BoneAndTipInfo(device_ip_addr)
    else:
        bone_and_tip_info:AbsBoneAndTipInfo = FakeBoneAndTipInfo(ct_arr_uint8.shape[1], ct_arr_uint8.shape[2], ct_arr_uint8.shape[3])

    # Initialize app and window
    app = medscope.MedScopeSystem(sys.argv)
    window = medscope.MedScopeWindow(
        im_wrap_xy=medscope.ImageWrap(x_rev=True, y_rev=True, transpose=True),
        im_wrap_xz=medscope.ImageWrap(x_rev=True, y_rev=True, transpose=True),
        im_wrap_yz=medscope.ImageWrap(x_rev=True, y_rev=True)
    )

    # Load Ct file
    window.set_volume(ct_arr_uint8)

    # Add a 3D model
    window.add_model_from_file(
        "bone_model",
        utils.BONE_STL,
        (1.0, 1.0, 1.0))  # white, random if not given
    
    # Add a 3D model
    window.add_model_from_file(
        "plane_with_bone-1",
        utils.PLANE_WITH_BONE_1,
        (1.0, 1.0, 0.1))  # yellow, random if not given
    
    # Add a 3D model
    window.add_model_from_file(
        "tool_model",
        utils.TOOL_STL,
        (0.1, 0.1, 0.1))  # gray, random if not given
    
        # Add a 3D model
    window.add_model_from_file(
        "tool_model_tip",
        utils.TOOL_TIP_STL,
        (1.0, 0.0, 0.0))  # red, random if not given

    # up at (0, -1, 0)
    window.set_camera_pose(
        (0, 0, 0),
        (0, 0, 500),
        (0, -1, 0)
    )

    # Call move_model every 1ms (as quickly as the processor can)
    def move_model():
        bone_and_tip_info.acquire()

        # 设置器械位置
        tip_pos = bone_and_tip_info.get_tip_in_ct()
        window.set_slice_positions(tip_pos[0], tip_pos[1], tip_pos[2])

        # 获得骨头模型位姿
        r, t = bone_and_tip_info.get_bone_pose()
        window.set_model_pose("bone_model", t, r)
        window.set_model_pose("plane_with_bone-1", t, r)

        # 获得手术器械模型位姿
        r, t = bone_and_tip_info.get_tool_pose()
        window.set_model_pose("tool_model", t, r)
        window.set_model_pose("tool_model_tip", t, r)

    window.add_timer("move_model", 1, move_model)
    sys.exit(app.exec_())

if __name__ == "__main__":
    import sys
    if "--fake" in sys.argv:
        use_fake_device = True
    else:
        y_or_n = input("Would you like to use fake device (y/N): ").lower()
        use_fake_device = (y_or_n.startswith("y"))
    main(use_fake_device=use_fake_device)
