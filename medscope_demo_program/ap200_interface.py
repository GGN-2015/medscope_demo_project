from py_ap200_simple_interface import AimooeExtDrive, I_ConnectionMethod
import numpy as np

import os
DIRNOW = os.path.dirname(os.path.abspath(__file__))
TOOL_DIR = os.path.join(DIRNOW, "AimooeTools")

class BoneAndTipInfo:
    def __init__(self, ip_addr:str) -> None:
        # Initialize AimooeExtDrive
        self.drive = AimooeExtDrive()
        self.drive.connect(I_ConnectionMethod.I_ETHERNET, ip_addr)

        self.zero_element = np.zeros((1, 1))
        self.bone_Tto: np.ndarray = self.zero_element
        self.bone_Rto: np.ndarray = self.zero_element
        self.tip_Tto : np.ndarray = self.zero_element

        # Until 3 Coord all found
        while (
            self.bone_Tto.shape == (1, 1) or
            self.bone_Rto.shape == (1, 1) or
            self. tip_Tto.shape == (1, 1)):
            self.acquire()

        assert isinstance(self.bone_Tto, np.ndarray)
        assert isinstance(self.bone_Rto, np.ndarray)
        assert isinstance(self.tip_Tto , np.ndarray)

        self.bone_to_ct_1 = np.array([
            [0.095946956448921, 0.995254615220118, 0.016199766394794, 154.051369602559532],
            [-0.254370872044368, 0.008781525205108, 0.967066876834516, -123.825411877426021],
            [0.962335513739139, -0.096907872219593, 0.254006344996134, 201.426643071232320],
            [0.000000000000000, 0.000000000000000, 0.000000000000000, 1.000000000000000],
        ])

        self.ct_1_to_ct2 = np.array([
            [0.213626280343952, -0.429429591858853, -0.877470249058253, 257.547242739984711],
            [-0.094269114370527,  0.884951707049311, -0.456041456740843, 279.130800297615963],
            [0.972356491428018, 0.180140783351391, 0.148566994151943, 195.259821718083003],
            [0.000000000000000, 0.000000000000000, 0.000000000000000, 1.000000000000000]
        ])

    def acquire(self) -> None:
        tool_info_dict = self.drive.get_specific_tool_info(
            TOOL_DIR, ["BONE-1", "TPS-B4D0-015"])
        
        bone_info = tool_info_dict.get("BONE-1")
        if bone_info is not None:
            self.bone_Tto = np.array(bone_info["Origin"])
            self.bone_Rto = np.array(bone_info["rMatrix"])
        
        tip_info = tool_info_dict.get("TPS-B4D0-015")
        if tip_info is not None:
            self.tip_Tto = np.array(tip_info["Tooltip"])
    
    # 获得骨骼模型坐标系下的器械尖端坐标
    def get_tip_in_bone(self):
        return self.bone_Rto.T @ (self.tip_Tto - self.bone_Tto)

    # 获得 CT 坐标系下的器械尖端坐标
    def get_tip_in_ct(self):
        return self.ct_1_to_ct2 @ self.bone_to_ct_1 @ np.hstack([self.get_tip_in_bone(), [1]])
    
    # 获得骨骼位姿
    def get_bone_pose(self):
        return self.bone_Rto, self.bone_Tto

if __name__ == "__main__":
    bone_and_tip_info = BoneAndTipInfo("192.168.1.10")
    while True:
        bone_and_tip_info.acquire()
        print(bone_and_tip_info.get_tip_in_ct())
