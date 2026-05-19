import numpy as np
import time
import json
import math

try:
    from .AbsBoneAndTipInfo import AbsBoneAndTipInfo
    from . import utils
except:
    from AbsBoneAndTipInfo import AbsBoneAndTipInfo
    import utils

class FakeBoneAndTipInfo(AbsBoneAndTipInfo):
    def __init__(self, x_range:int, y_range:int, z_range:int) -> None:
        self.x_range = x_range
        self.y_range = y_range
        self.z_range = z_range
        self.begin_time = time.time()
        
        # 模拟的器械尖端
        with open(utils.ACTION_JSON, "r") as fpin:
            self.json_data = json.load(fpin)
        
        # 总时长
        self.total_time = self.json_data[-1]["time_now"]
        self.index_now = 0
    
    @classmethod
    def _mod(cls, v1:float, v2:float) -> float:
        if v2 == 0:
            return 0
        return v1 - math.floor(v1 / v2) * v2

    def acquire(self) -> None:
        timestamp_now = time.time() - self.begin_time

        if timestamp_now > self.total_time:
            self.begin_time = time.time()
            timestamp_now = time.time() - self.begin_time
            self.index_now = 0

        assert timestamp_now <= self.total_time

        # 找到第一个大于等于 timestamp_now 的时间戳
        while (
            self.index_now <= len(self.json_data) - 1 and 
            self.json_data[self.index_now]["time_now"] < timestamp_now):
            self.index_now += 1

    def get_tip_in_ct(self) -> np.ndarray:
        return np.array(self.json_data[self.index_now]["tip_in_ct"])

    def get_bone_pose(self) -> tuple[np.ndarray, ...]:
        return np.array(self.json_data[self.index_now]["r_bone"]), np.array(self.json_data[self.index_now]["t_bone"])
    
    def get_tool_pose(self) -> tuple[np.ndarray, ...]:
        return np.array(self.json_data[self.index_now]["r_tool"]), np.array(self.json_data[self.index_now]["t_tool"])

if __name__ == "__main__":
    fk_bone_and_tip_info = FakeBoneAndTipInfo(100, 200, 300)

    fk_bone_and_tip_info.acquire()
    print(fk_bone_and_tip_info.get_tip_in_ct())
