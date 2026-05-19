from py_ap200_simple_interface import AimooeExtDrive, I_ConnectionMethod
import numpy as np
import time
import json
import os

try:
    from .AbsBoneAndTipInfo import AbsBoneAndTipInfo
    from . import utils
except:
    from AbsBoneAndTipInfo import AbsBoneAndTipInfo
    import utils

class Ap200_BoneAndTipInfo(AbsBoneAndTipInfo):
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
            [-0.1376650631427765, 0.9894883036613464, 0.04428544268012047, 292.7553529001813], 
            [0.2815919518470764, 0.08196504414081573, -0.9560270309448242, 345.3551874660921], 
            [-0.9496074318885803, -0.1191411018371582, -0.28991565108299255, 205.73061393043133], 
            [0.0, 0.0, 0.0, 1.0]
        ])

    def acquire(self) -> None:
        tool_info_dict = self.drive.get_specific_tool_info(
            utils.TOOL_DIR, ["BONE-1", "TPS-B4D0-015"])
        
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
    def get_tip_in_bone(self) -> np.ndarray:
        return self.bone_Rto.T @ (self.tip_Tto - self.bone_Tto)

    # 获得 CT 坐标系下的器械尖端坐标
    def get_tip_in_ct(self) -> np.ndarray:
        return (self.bone_to_ct @ np.hstack([self.get_tip_in_bone(), [1]]))[:3]
    
    # 获得骨骼位姿
    def get_bone_pose(self) -> tuple[np.ndarray, ...]:
        return self.bone_Rto, self.bone_Tto
    
    # 获得器械位姿
    def get_tool_pose(self) -> tuple[np.ndarray, ...]:
        return self.tool_Rto, self.tool_Tto

# 录制新数据
def record_main():
    if os.path.isfile(utils.ACTION_JSON):
        inp = input("are you sure to erase the history record? (y/N)").lower().strip()
        if not inp.startswith("y"):
            return

    # 初始化连接
    bone_and_tip_info:AbsBoneAndTipInfo = Ap200_BoneAndTipInfo("192.168.1.10")
    # 记录一个动作序列
    json_data = []
    begin_time = time.time()

    # 录制时长
    MAX_TIME = 10

    print("Recording ...")
    while True:
        bone_and_tip_info.acquire()
        
        # 记录时间
        time_now = time.time() - begin_time
        if time_now > MAX_TIME:
            break

        # 获取数据
        tip_in_ct = bone_and_tip_info.get_tip_in_ct()
        r_bone, t_bone = bone_and_tip_info.get_bone_pose()
        r_tool, t_tool = bone_and_tip_info.get_tool_pose()

        # 记录当前时刻的信息
        json_data.append({
            "time_now": time_now, # 距离系统启动的时间
            "tip_in_ct": tip_in_ct.tolist(),
            "r_bone": r_bone.tolist(),
            "t_bone": t_bone.tolist(),
            "r_tool": r_tool.tolist(),
            "t_tool": t_tool.tolist(),
        })

    # 存档动作序列
    with open(utils.ACTION_JSON, "w") as fpout:
        json.dump(json_data, fpout, indent=4)


if __name__ == "__main__":
    record_main()
