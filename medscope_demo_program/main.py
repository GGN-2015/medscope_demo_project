import medscope
from read_nii_to_numpy import nii_file_to_numpy
from remote_auto_fetch import remote_auto_fetch
import numpy as np
import pickle

import sys
import os

try:
    from .ap200_interface import BoneAndTipInfo
except:
    from ap200_interface import BoneAndTipInfo

DIRNOW = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(DIRNOW, "data")
CT_FILE = os.path.join(DATA_DIR, "CT.nii")
CT_PICKLE = os.path.join(DATA_DIR, "CT.pickle")
BONE_STL = os.path.join(DATA_DIR, "BONE-1.new.stl")
TOOL_STL = os.path.join(DATA_DIR, "TPS-B4D0-015.stl")

# download from github
remote_auto_fetch(
    "https://github.com/GGN-2015/medscope_demo_project/releases/download/binary_file/CT.nii",
    CT_FILE, md5_hash="58C6F98ED7C3E9DB4B5CD265CADD5882")

def main():
    # Fill in your ip addr
    print("Connecting ap200 device ...")
    bone_and_tip_info = BoneAndTipInfo("192.168.1.10")

    # Load CT file
    if not os.path.isfile(CT_PICKLE):
        print("Generating CT.pickle ...")
        arr = nii_file_to_numpy(CT_FILE, 1.0, 1.0, 1.0)
        arr[arr <= 3] = 3
        arr[arr >= 160] = 160
        arr_norm = (arr - np.min(arr)) / (np.max(arr) - np.min(arr) + 1e-8)
        arr_uint8 = (arr_norm * 255).astype(np.uint8)
        with open(CT_PICKLE, "wb") as fp: # Create pickle
            pickle.dump(arr_uint8, fp)  
    
    else:
        print("Loading CT.pickle ...")
        with open(CT_PICKLE, "rb") as fp: # Read pickle
            arr_uint8 = pickle.load(fp)

    print("CT.shape:", arr_uint8.shape)

    # Initialize app and window
    app = medscope.MedScopeSystem(sys.argv)
    window = medscope.MedScopeWindow()

    # Load Ct file
    window.set_volume(arr_uint8)

    # Add a 3D model
    window.add_model_from_file(
        "bone_model",
        BONE_STL,
        (1.0, 1.0, 1.0))  # white, random if not given
    
    # Add a 3D model
    window.add_model_from_file(
        "tool_model",
        TOOL_STL,
        (0.75, 0.75, 0.75))  # gray, random if not given

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

        # 获得手术器械模型位姿
        r, t = bone_and_tip_info.get_tool_pose()
        window.set_model_pose("tool_model", t, r)

    window.add_timer("move_model", 1, move_model)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
