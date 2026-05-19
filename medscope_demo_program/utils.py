import os
DIRNOW = os.path.dirname(os.path.abspath(__file__))
TOOL_DIR = os.path.join(DIRNOW, "AimooeTools")
ACTION_JSON = os.path.join(DIRNOW, "data", "action.json") # 录制的信息

DATA_DIR = os.path.join(DIRNOW, "data")
CT_FILE = os.path.join(DATA_DIR, "CT.nii")
SEG_CT_FILE = os.path.join(DATA_DIR, "SegmentationCT.nii")
BONE_STL = os.path.join(DATA_DIR, "BONE-1.real.stl")
PLANE_WITH_BONE_1 = os.path.join(DATA_DIR, "PLANE_WITH_BONE_1.stl")
TOOL_STL = os.path.join(DATA_DIR, "TPS-B4D0-015.stl")
TOOL_TIP_STL = os.path.join(DATA_DIR, "TPS-B4D0-015-TIP.stl")
