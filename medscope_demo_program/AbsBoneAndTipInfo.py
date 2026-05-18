import abc
import numpy as np

# 抽象类
class AbsBoneAndTipInfo(abc.ABC):
    def __init__(self) -> None:
        pass
    
    @abc.abstractmethod
    def acquire(self) -> None:
        pass

    @abc.abstractmethod
    def get_tip_in_ct(self) -> np.ndarray:
        return np.array([0, 0, 0])

    @abc.abstractmethod
    def get_bone_pose(self) -> tuple[np.ndarray, ...]:
        return np.eye(3), np.array([0, 0, 0])
    
    @abc.abstractmethod
    def get_tool_pose(self) -> tuple[np.ndarray, ...]:
        return np.eye(3), np.array([0, 0, 0])
