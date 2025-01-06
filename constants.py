from enum import Enum

treshold = -0.2

modeltype_filepath = "core/model/saved_models/checkpoint"
modelsuccess_filepath = "core/model/saved_models/success"

fields_to_keep = ["Euler_X","Euler_Y","Euler_Z","Gyr_X", "Gyr_Y", "Gyr_Z", "Acc_X", "Acc_Y", "Acc_Z", "Combination"]

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
        "2805": {
            "path": "2805/1514",
            "sample_time_fine_synchro": 3476410869 + 4000000
        },
        "28051": {
            "path": "2805/1413",
            "sample_time_fine_synchro": 906470971 + 4000000
        },
        "28052": {
            "path": "2805/1310",
            "sample_time_fine_synchro": 1457943469 + 12000000
        },
        "3005": {
            "path": "3005/1311",
            "sample_time_fine_synchro": 743655957
        },
        "30051": {
            "path": "3005/1412",
            "sample_time_fine_synchro": 324024124 + 29000000
        },
        "30052": {
            "path": "3005/1510",
            "sample_time_fine_synchro": 3768432639 + 12000000
        },
        "0406": {
            "path": "0406/1019",
            "sample_time_fine_synchro": 3541152851
        },
        "04061": {
            "path": "0406/0927",
            "sample_time_fine_synchro": 404239229 + 17000000
        },
        "1007": {
            "path": "1007/1108",
            "sample_time_fine_synchro": 217437574
        },
        "10071": {
            "path": "1007/1006",
            "sample_time_fine_synchro": 3523005443 + 17000000
        },
        "10072": {
            "path": "1007/0910",
            "sample_time_fine_synchro": 105458733 + 19000000
        },
        "2907": {
            "path": "2907/1010",
            "sample_time_fine_synchro": 367750883
        },
        "29071": {
            "path": "2907/0911",
            "sample_time_fine_synchro": 229029957 + 20000000
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

    NONE = 8  # none is intended to be used when the annotation could not be completed (ice skater off frame at the time of the jump)

class jumpSuccess(Enum):
    FALL = 0
    SUCCESS = 1
    NONE = 2 # used before the annotation