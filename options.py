KIND_OPTIONS = ['-', 'BM', 'PD']
SITE_OPTIONS = {
    'WA': ['-', '26-1','26-2','26-3','26-4','26-5','26-H','27-1','27-2','27-3','27-4','27-5','28-1','28-2','28-3','28-4','28-5','28-6','29-1(HC겸용)','29-2','29-3'],
    'UC1': ['-','HC1','HC2','1-1','1-2','1-3','2-1','2-2','2-3','3-1','3-2','3-3','4-1','4-2','4-3','5-1','5-2','5-3','HC3','HC4','6-1','6-2','6-3','7-1','7-2','7-3','8-1','8-2','8-3','9-1','9-2','9-3','10-1','10-2','10-3'],
    'UC2': ['-','HC1','HC2','1-1','1-2','1-3','2-1','2-2','2-3','3-1','3-2','3-3','4-1','4-2','4-3','5-1','5-2','5-3','HC3','HC4','6-1','6-2','6-3','7-1','7-2','7-3','8-1','8-2','8-3','9-1','9-2','9-3','10-1','10-2','10-3'],
    'MI1': ['-','1-1','1-2','1-3','1-4','1-5','1-H','2-1','2-2','2-3','2-4'],
    'MI2': ['-','3-1','3-2','3-3','3-4','3-5','3-H','4-1','4-2','4-3','4-4','4-5','4-6','5-1','5-2','5-3','5-4','5-5(HC겸용)'],
    'MI3': ['-','HC1','HC2','1-1','1-2','1-3','2-1','2-2','2-3','3-1','3-2','3-3','4-1','4-2','4-3','5-1','5-2','5-3'],
    'NSE': ['-','1-1','1-2','1-3','1-4','1-5','1-H','2-1','2-2','2-3','2-4','2-5','2-H','3-1','3-2','3-3','3-4','3-5','4-1','4-2','4-3','4-4','4-5','4-6'],
    'L-H': ['-','1-1','1-2','1-3','2-1','2-2','2-3','2-4','3-1','3-2','3-3','4-1','4-2','4-3','5-1','5-2','5-3','6-1','6-2','6-3','HC1','HC2']
}
PROCESS_OPTIONS = {
    'Electrode Supply': ['-', 'Pancake.Loader'],
    'Lamination': ['-', 'Separator.Unwinder','Electrode/Separator.Combiner','Laminator','Cell.FinalCutter','Cell.TrackingSystem','Cell.Inspector','Cell.Unloader'],
    'D-Stacking': ['-','[01]Cell.Loading C/V','[02]Cell.Loading C/V','[01]Cell.Stacker','[02]Cell.Stacker','[03]Cell.Stacker','Stacked Cell.Transfer'],
    'Taper': ['-','HalfCell.Loading','HalfCell.Stack','LMS','[01]StackedCell.Taper','[02]StackedCell.Taper'],
    'Inspection': ['-','TapedCell.Vision','TapedCell.Rotate','TapedCell.ShortInspector','Cell.TrackingSystem','TapedCell.Transfer','TapedCell.Unloader']
}
UNIT_OPTIONS = {
    "Pancake.Loader": [
        "[01/A] Pancake. Conveyor", "[01/B] Pancake. Conveyor", "[01/C] Pancake. Conveyor",
        "[02/A] Pancake. Conveyor", "[02B] Pancake. Conveyor", "[02/C] Pancake. Conveyor",
        "Pancake. Hoist",
        "[01/A] Pancake. Unwinder", "[02/A] Pancake. Unwinder", "[03/A] Pancake. Unwinder", "[04/A] Pancake. Unwinder",
        "[01/B] Pancake. Unwinder", "[02/B] Pancake. Unwinder", "[03/B] Pancake. Unwinder", "[04/B] Pancake. Unwinder",
        "[01/A] Electrode. Vacuum Plate", "[02/A] Electrode. Vacuum Plate", "[03/A] Electrode. Vacuum Plate", "[04/A] Electrode. Vacuum Plate",
        "[01/B] Electrode. Vacuum Plate", "[02/B] Electrode. Vacuum Plate", "[03/B] Electrode. Vacuum Plate", "[04/B] Electrode. Vacuum Plate",
        "[01/A] Electrode. Auto Splicer Cutter", "[02/A] Electrode. Auto Splicer Cutter",
        "[03/A] Electrode. Auto Splicer Cutter", "[04/A] Electrode. Auto Splicer Cutter",
        "[01/B] Electrode. Auto Splicer Cutter", "[02/B] Electrode. Auto Splicer Cutter",
        "[03/B] Electrode. Auto Splicer Cutter", "[04/B] Electrode. Auto Splicer Cutter",
        "Electrode. Tape Feeder", "Electrode. Scrape Box",
        "[01/A] Electrode. Idle Roller", "[02/A] Electrode. Idle Roller",
        "[01/B] Electrode. Idle Roller", "[02/B] Electrode. Idle Roller",
        "[01/A] Dancer. Roller", "[02/A] Dancer. Roller",
        "[01/B] Dancer. Roller", "[02/B] Dancer. Roller",
        "[01/A] Adjust Roller", "[02/A] Adjust Roller",
        "[01/B] Adjust Roller", "[02/B] Adjust Roller",
        "[01/A] Electrode. EPC", "[02/A] Electrode. EPC",
        "[03/A] Electrode. EPC", "[04/A] Electrode. EPC",
        "[01/B] Electrode. EPC", "[02/B] Electrode. EPC",
        "[03/B] Electrode. EPC", "[04/B] Electrode. EPC",
        "[01/A] Winder Diameter Sensor", "[02/A] Winder Diameter Sensor",
        "[03/A] Winder Diameter Sensor", "[04/A] Winder Diameter Sensor",
        "[01/B] Winder Diameter Sensor", "[02/B] Winder Diameter Sensor",
        "[03/B] Winder Diameter Sensor", "[04/B] Winder Diameter Sensor",
        "[01/A] PET tape sensor", "[02/A] PET tape sensor",
        "[03/A] PET tape sensor", "[04/A] PET tape sensor",
        "[01/B] PET tape sensor", "[02/B] PET tape sensor",
        "[03/B] PET tape sensor", "[04/B] PET tape sensor",
        "[01] Tab Direction Vision", "[02] Tab Direction Vision",
        "ATR"
    ],
    "Separator.Unwinder": [
        "[01/Upper] Separator. Unwinder", "[02/Upper] Separator. Unwinder",
        "[01/Upper] Separator. PET. Winder", "[02/Upper] Separator. PET. Winder",
        "[01/Lower] Separator. Unwinder", "[02/Lower] Separator. Unwinder",
        "[01/Lower] Separator. PET. Winder", "[02/Lower] Separator. PET. Winder",
        "[01/Upper] Separator. PET. Ionizer", "[02/Upper] Separator. PET. Ionizer",
        "[01/Lower] Separator. PET. Ionizer", "[02/Lower] Separator. PET. Ionizer",
        "[01/Upper] Separator. Auto Splicer Vacuum Plate", "[02/Upper] Separator. Auto Splicer Vacuum Plate",
        "[03/Upper] Separator. Auto Splicer Vacuum Plate", "[04/Upper] Separator. Auto Splicer Vacuum Plate",
        "[Upper] Separator. Auto Splicer Tape feeder", "[Upper] Separator. Auto Splicer Tape clamp",
        "[Upper] Separator. Auto Splicer Cutter", "[Upper] Separator. Auto Splicer Residual Sepa collector",
        "[Upper] Separator. Auto Splicer Residual Sepa collector",
        "[01/Lower] Separator. Auto Splicer vacuum plate", "[02/Lower] Separator. Auto Splicer vacuum plate",
        "[03/Lower] Separator. Auto Splicer  vacuum plate", "[04/Lower] Separator. Auto Splicer  vacuum plate",
        "[Lower] Separator. Auto Splicer Tape feeder", "[Lower] Separator. Auto Splicer Tape clamp",
        "[Lower] Separator. Auto Splicer Separator cutter", "[Lower ] Separator. Auto Splicer Residual Sepa collector",
        "[Lower] Separator. Auto Splicer Residual Sepa collector",
        "[01/Upper] Electrode. Manual Splicer", "[01/Center] Electrode. Manual Splicer",
        "[01/Upper] Separator. Winder Diameter Sensor", "[02/Upper] Separator. Winder Diameter Sensor",
        "[01/Lower] Separator. Winder Diameter Sensor", "[02/Lower] Separator. Winder Diameter Sensor",
        "[01/Upper] Separator. End Tape Sensor", "[02/Upper] Separator. End Tape Sensor",
        "[01/Lower] Separator. End Tape Sensor", "[02/Lower] Separator. End Tape Sensor",
        "[Upper] Separator. Manual Splicer", "[Lower] Separator. Manual Splicer"
    ],
    "Electrode/Separator.Combiner": [
        "[Upper] Electrode. Feeding Roller", "[Center] Electrode. Feeding Roller",
        "[01] Electrode / Separator. Nip Roller", "[01] Electrode / Separator. Temporary Heating Roller",
        "[02] Electrode / Separator. Nip Roller", "[02] Electrode / Separator. Temporary Heating Roller",
        "[Upper] Electrode. EPC", "[Center] Electrode. EPC",
        "[Upper] Separator. EPC", "[Lower] Separator. EPC",
        "[Upper] Electrode. Cutter", "[Center] Electrode. Cutter",
        "[Upper] Electrode Cutting Linear", "[Center] Electrode Cutting Linear",
        "[Upper] Separator. Dancer", "[Lower] Separator. Dancer",
        "[Lower] Separator. Corona(not applied)",
        "[Upper] Electrode. Idle Roller", "[Center] Electrode. Idle Roller",
        "[Upper] Separator. Idle Roller", "[Lower] Separator. Idle Roller",
        "[Upper] PET (Separator). Idle Roller", "[Lower] PET (Separator).Idle Roller",
        "Magnet",
        "[02/Upper] Electrode. Manual Splicer", "[02/Center] Electrode. Manual Splicer",
        "[Upper] Electrode Connection PET Winder", "[Center] Electrode. V Groove Vision",
        "[Upper] Electrode. Connection Tape Sensor", "[Center] Electrode. Connection Tape Sensor",
        "[Upper] Separator. Connection Tape Sensor", "[Lower] Separator. Connection Tape Sensor",
        "[Upper] Electrode. Stopper", "[Center] Electrode. Stopper",
        "[Upper] Separator. KANSEN Expander Roller", "[Lower] Separator. KANSEN Expander Roller"
    ],
    "Laminator": [
        "[01/Upper] Heating Zone", "[01/Lower] Heating Zone",
        "[Upper] Sub Heater", "[Lower] Sub Heater",
        "[Upper] Lamination Roller", "[Lower] Lamination Roller",
        "[a] PET. Cleaner", "[b] PET. Cleaner", "[c] PET. Cleaner", "[d] PET. Cleaner",
        "[01/Upper] PET. Dancer", "[02/Upper] PET. Dancer",
        "[01/Lower] PET. Dancer", "[02/Lower] PET. Dancer",
        "[Upper] PET. Unwinder", "[Lower] PET. Unwinder",
        "[Upper] PET. Winder", "[Lower] PET. Winder",
        "Uncut Cell. Dancer", "[Upper] PET. Splicer(Manual)", "[Lower] PET. Splicer(Manual)",
        "Separator. Sealer", "Separator. Sealing Linear",
        "Uncut Cell. Air Blow/Suction", "Uncut Cell. Union Vision (#합치)",
        "[01/Upper] PET. Ionizer", "[02/Upper] PET. Ionizer",
        "[01/Lower] PET. Ionizer", "[02/Lower] PET. Ionizer",
        "[Upper] PET. Idle Roller", "[Lower] PET. Idle Roller",
        "Magnet", "[Upper] Separator. Longside Sealer", "[Lower] Separator. Longside Sealer",
        "Separator. Longside Sealer. Vision",
        "[Upper] Sub Roller", "[Lower] Sub Roller",
        "Particle Prevention Unit"
    ],
    "Cell.FinalCutter": [
        "Uncut Cell. Conveyor", "Cell. Grip Nip Roller", "Cell. Cutter", "Electrode. Cutting Linear"
    ],
    "Cell.TrackingSystem": [
        "Cell. BCR", "[01] Cell. BCR", "[02] Cell. BCR"
    ],
    "Cell.Inspector": [
        "Cell. Suction Conveyor", "Cell. Short Inspector", "Cell. Vision Inspector",
        "Cell. NG Mark Vision", "Cell. Short Inspector Linear", "Cell. Vision Inspector Linear",
        "Cell. Blow & Suction", "Cell. Thickness Sensor"
    ],
    "Cell.Unloader": [
        "[01] NG Cell. Pusher", "[02] NG Cell. Pusher", "[03] NG Cell. Pusher",
        "[01] NG Cell. Box", "[02] NG Cell. Box", "[03] NG Cell. Box",
        "Cell. Suction Conveyor", "OK Cell. Pusher"
    ],
    "[01]Cell.Loading C/V": [
        "[Lower] Cell. Loading C/V"],
    "[02]Cell.Loading C/V": [
        "[Upper] Cell. Loading C/V", "[01] Cell. NG Box", "[02] Cell. NG Box", "Cell. Lower Separator Vision"],
    "[01]Cell.Stacker": [
        "Cell. Pusher", "[01/A] Cell. Gripper", "[02/A] Cell. Gripper", "[03/A] Cell. Gripper",
        "[01/B] Cell. Gripper", "[02/B] Cell. Gripper", "[03/B] Cell. Gripper",
        "Cell. Align Vision", "Cell. Align Table", "Table Transfer Linear", "Cell. Stack Vision"
    ],
    "[02]Cell.Stacker": [
        "Cell. Pusher", "[01/A] Cell. Gripper", "[02/A] Cell. Gripper", "[03/A] Cell. Gripper",
        "[01/B] Cell. Gripper", "[02/B] Cell. Gripper", "[03/B] Cell. Gripper",
        "Cell. Align Vision", "Cell. Align Table", "Table Transfer Linear", "Cell. Stack Vision"
    ],
    "[03]Cell.Stacker": [
        "Cell. Pusher", "[01/A] Cell. Gripper", "[02/A] Cell. Gripper", "[03/A] Cell. Gripper",
        "[01/B] Cell. Gripper", "[02/B] Cell. Gripper", "[03/B] Cell. Gripper",
        "Cell. Align Vision", "Cell. Align Table", "Table Transfer Linear", "Cell. Stack Vision"
    ],
    "Stacked Cell.Transfer": ["-", "Stacked Cell. Transfer", "Stacked Cell. Gripper"],
    "HalfCell.Loading": [
        "[A] Half Cell. Magazine", "[B] Half Cell. Magazine", "[C] Half Cell. Magazine",
        "Half Cell. Vibrator", "Half Cell. Pick & Place", "Half Cell. Thickness Inspector",
        "Half Cell. Rotate", "[A] Half Cell. NG Box", "[B] Half Cell. NG Box"
    ],
    "HalfCell.Stack": [
        "Half Cell. Buffer Table", "Half Cell. Vision NG Box",
        "Half Cell. Scara Robot", "Half Cell. Vision"
    ],
    "LMS": [
        "Stacked Cell. Shuttle", "[01] LMS. Stacked Cell Clamp Air Supply",
        "[02] LMS. Stacked Cell Clamp Air Supply", "[03] LMS. Stacked Cell Clamp Air Supply",
        "[04] LMS. Stacked Cell Clamp Air Supply", "[05] LMS. Stacked Cell Clamp Air Supply",
        "Shuttle. In Lift", "Shuttle. Out Lift", "Shuttle. Blow & Suction Cleaner",
        "Shuttle. Buffer01", "Shuttle. Buffer02", "Stacked Cell. NG Pick & Place",
        "Stacked Cell. NG Box", "Stacked Cell. Rotate", "Stacked Cell. BCR"
    ],
    "[01]StackedCell.Taper": [
        "Stacked Cell. Press", "[01] Tape. Attacher", "[02] Tape. Attacher",
        "[03] Tape. Attacher", "[04] Tape. Attacher", "[05] Tape. Attacher",
        "[06] Tape. Attacher", "[01] Tape. Upper Clamp", "[02] Tape. Upper Clamp",
        "[03] Tape. Upper Clamp", "[04] Tape. Upper Clamp", "[05] Tape. Upper Clamp",
        "[06] Tape. Upper Clamp", "[01] Tape. Lower Clamp", "[02] Tape. Lower Clamp",
        "[03] Tape. Lower Clamp", "[04] Tape. Lower Clamp", "[05] Tape. Lower Clamp",
        "[06] Tape. Lower Clamp", "[01] Tape. Tape Supply", "[02] Tape. Tape Supply",
        "[03] Tape. Tape Supply", "[04] Tape. Tape Supply", "[05] Tape. Tape Supply",
        "[06] Tape. Tape Supply", "[01] Tape. Cutter", "[02] Tape. Cutter",
        "[03] Tape. Cutter", "[04] Tape. Cutter", "[05] Tape. Cutter",
        "[06] Tape. Cutter", "NG Tape. Receiver"
    ],
    "[02]StackedCell.Taper": [
        "Stacked Cell. Press", "[01] Tape. Attacher", "[02] Tape. Attacher",
        "[03] Tape. Attacher", "[04] Tape. Attacher", "[05] Tape. Attacher",
        "[06] Tape. Attacher", "[01] Tape. Upper Clamp", "[02] Tape. Upper Clamp",
        "[03] Tape. Upper Clamp", "[04] Tape. Upper Clamp", "[05] Tape. Upper Clamp",
        "[06] Tape. Upper Clamp", "[01] Tape. Lower Clamp", "[02] Tape. Lower Clamp",
        "[03] Tape. Lower Clamp", "[04] Tape. Lower Clamp", "[05] Tape. Lower Clamp",
        "[06] Tape. Lower Clamp", "[01] Tape. Tape Supply", "[02] Tape. Tape Supply",
        "[03] Tape. Tape Supply", "[04] Tape. Tape Supply", "[05] Tape. Tape Supply",
        "[06] Tape. Tape Supply", "[01] Tape. Cutter", "[02] Tape. Cutter",
        "[03] Tape. Cutter", "[04] Tape. Cutter", "[05] Tape. Cutter",
        "[06] Tape. Cutter", "NG Tape. Receiver"
    ],
    "TapedCell.Vision": [
        "[01] Taped Cell. Pick & Place", "[Upper/Lower] Taped Cell. Vision",
        "[4-side] Taped Cell. Vision", "Taped Cell. Rotating Table",
        "[02] Taped Cell. Pick & Place", "Taped Cell. Weight Inspector"
    ],
    "TapedCell.Rotate": [
        "TapedCell.Rotate"],
    "TapedCell.ShortInspector": [
        "Taped Cell. Shuttle", "Taped Cell. Short, Thickness Inspector"],
    "TapedCell.Transfer": [
        "NG Taped Cell. Transfer", "[01] NG Box", "[02] NG Box",
        "[03] NG Box", "[04] NG Box", "NG Box Transfer",
        "OK Taped Cell. Transfer", "Taped Cell. Conveyor", "Taped Cell. Align"
    ],
    "TapedCell.Unloader": [
        "Taped Cell. Pick & Place", "[01] Taped Cell. Lift", "[02] Taped Cell. Lift",
        "[01] Tray(Empty). Conveyor", "[02] Tray(Empty). Conveyor", "Tray(Empty). Conveyor",
        "Tray. Conveyor", "[A] Tray. Lift", "[B] Tray. Lift", "Tray. Cleaner",
        "Tray. Conveyor Free Roller", "Tray(Empty). Conveyor Free Roller"
    ]
}
