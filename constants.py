from enum import Enum

treshold = -0.2

JUMPWINDOWFRAMEBEGIN = 150  # in frames
JUMPWINDOWFRAMEEND = 250  # in frames

SYNCHROFRAME = 200  # in frames

NB_CLASSES_USED = 7 # excludes false positive and none

modeltype_filepath = "core/model/saved_models/checkpoint"
modelsuccess_filepath = "core/model/saved_models/success"

fields_to_keep = ["Euler_X","Euler_Y","Euler_Z","Gyr_X", "Gyr_Y", "Gyr_Z", "Acc_X", "Acc_Y", "Acc_Z"]


sessions = {
        "1331": {
            "path": "2009/1331",
            "sample_time_fine_synchro": 969369596 - 4000000
        },
        "1414": {
            "path": "2009/1414",
            "sample_time_fine_synchro": 3572382138 + ((320 - 66 + 10) * 1200000)
        },
        "1304": {
            "path": "1110/1304",
            "sample_time_fine_synchro": 115376653
        },
        "1404": {
            "path": "1110/1404",
            "sample_time_fine_synchro": 3702624824
        },
        "1128": {
            "path": "1128",
            "sample_time_fine_synchro": 1479527966
        },
        "2805": {
            "path": "2805/1413",
            "sample_time_fine_synchro": 0
        },
        "3005": {
            "path": "3005/1311",
            "sample_time_fine_synchro": 743655957
        },
        "0406": {
            "path": "0406/1019",
            "sample_time_fine_synchro": 3541152851
        }
    }

class jumpType(Enum):
    """
    figure skating jump type enum
    """

    # toe jumps
    TOE_LOOP = 0
    FLIP = 1
    LUTZ = 2

    # edge jumps
    SALCHOW = 3
    LOOP = 4
    AXEL = 5

    FALSE_POSITIVE = 7
    NONE = 8  # none is intended to be used when the annotation could not be completed (ice skater off frame at the time of the jump)

class jumpSuccess(Enum):
    FALL = 0
    SUCCESS = 1
    NONE = 2 # used before the annotation