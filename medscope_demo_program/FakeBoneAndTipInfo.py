import numpy as np

try:
    from .AbsBoneAndTipInfo import AbsBoneAndTipInfo
except:
    from AbsBoneAndTipInfo import AbsBoneAndTipInfo

class FakeBoneAndTipInfo(AbsBoneAndTipInfo):
    def __init__(self, x_range:int, y_range:int, z_range:int) -> None:
        self.x_range = x_range
        self.y_range = y_range
        self.z_range = z_range
        
        # 模拟的器械尖端
        self.x_now = 0
        self.y_now = 0
        self.z_now = 0
        
    def acquire(self) -> None:
        self.x_now = (self.x_now + 1) % self.x_range
        self.y_now = (self.y_now + 2) % self.y_range
        self.z_now = (self.z_now + 3) % self.z_range

    def get_tip_in_ct(self) -> np.ndarray:
        return np.array([self.x_now, self.y_now, self.z_now])

    def get_bone_pose(self) -> tuple[np.ndarray, ...]:
        return np.eye(3), np.array([0, 0, 1000])
    
    def get_tool_pose(self) -> tuple[np.ndarray, ...]:
        return np.eye(3), np.array([0, 0, 1000])

if __name__ == "__main__":
    fk_bone_and_tip_info = FakeBoneAndTipInfo(100, 200, 300)

    fk_bone_and_tip_info.acquire()
    print(fk_bone_and_tip_info.get_tip_in_ct())
