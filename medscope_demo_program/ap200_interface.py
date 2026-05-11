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
        self.tool_Tto: np.ndarray = self.zero_element
        self.tool_Rto: np.ndarray = self.zero_element
        self.tip_Tto : np.ndarray = self.zero_element

        # Until Coords all found
        print("Please show tool and bone model to device camera ...")
        while (
            self.bone_Tto.shape == (1, 1) or
            self.bone_Rto.shape == (1, 1) or
            self.tool_Tto.shape == (1, 1) or
            self.tool_Rto.shape == (1, 1) or
            self. tip_Tto.shape == (1, 1)):
            self.acquire()

        assert isinstance(self.bone_Tto, np.ndarray)
        assert isinstance(self.bone_Rto, np.ndarray)
        assert isinstance(self.tip_Tto , np.ndarray)

        self.bone_to_ct:np.ndarray = np.array([
            [0.1217055469751358, 0.9852456450462341, 0.12032786756753922, 146.5273892979832],
            [0.28159239888191223, 0.08197470754384995, -0.9560260772705078, 328.03341629784484], 
            [-0.9517843723297119, 0.1502370834350586, -0.2674608826637268, 202.91085813852902], 
            [0.0, 0.0, 0.0, 1.0]
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
            self.tip_Tto  = np.array(tip_info["Tooltip"])
            self.tool_Tto = np.array(tip_info["Origin"])
            self.tool_Rto = np.array(tip_info["rMatrix"])
    
    # 获得骨骼模型坐标系下的器械尖端坐标
    def get_tip_in_bone(self):
        return self.bone_Rto.T @ (self.tip_Tto - self.bone_Tto)

    # 获得 CT 坐标系下的器械尖端坐标
    def get_tip_in_ct(self):
        return self.bone_to_ct @ np.hstack([self.get_tip_in_bone(), [1]])
    
    # 获得骨骼位姿
    def get_bone_pose(self):
        return self.bone_Rto, self.bone_Tto
    
    # 获得器械位姿
    def get_tool_pose(self):
        return self.tool_Rto, self.tool_Tto

if __name__ == "__main__":
    bone_and_tip_info = BoneAndTipInfo("192.168.1.10")
    while True:
        bone_and_tip_info.acquire()
        print(bone_and_tip_info.get_tip_in_ct())
