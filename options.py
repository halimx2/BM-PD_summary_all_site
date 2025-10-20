KIND_OPTIONS = ['-', 'BM', 'PD']
SITE_OPTIONS = {
    'WA': ['-', '26-1','26-2','26-3','26-4','26-5','26-H','27-1','27-2','27-3','27-4','27-5','28-1','28-2','28-3','28-4','28-5','28-6','29-1(HC겸용)','29-2','29-3'],
    'WA5': ['-','11-1','11-2','11-3','11-4','12-1','12-2','12-3','12-4','13-1','13-2','13-3','13-4','14-1','14-2','14-3','14-4','15-1','15-2','15-3','15-4','16-1','16-2','16-3','16-4','17-1','17-2','17-3','17-4','18-1','18-2','18-3','18-4'],
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

PROCESS_OPTIONS_NORMAL = {
    "Electrode Supply": [
        "Electrode. Unwinder"
    ],
    "Lamination": [
        "Separator.Unwinder",
        "Electrode/Separator.Combiner",
        "Laminator",
        "Cell.Final Cutter",
        "Cell.Inspector",
        "Cell.Unloader",
        "Magazine. Buffer",
        "Cell. Tracking System"
    ],
    "Stacking": [
        "Cell.Conveyor",
        "Cell.Distributor",
        "Cell.Aligner",
        "Stacked Cell.Transfer"
    ],
    "Taper": [
        "Stacked Cell.Loader",
        "LMS",
        "Half Cell.Stacker",
        "Stacked Cell.Taper",
        "Stacked Cell.Unloader"
    ],
    "Inspection": [
        "Taped Cell.Vision",
        "Taped Cell.Weight Inspector",
        "Taped Cell.Short Checker",
        "Taped Cell.Transfer Unit",
        "Taped Cell.Unloader"
    ]
}

UNIT_OPTIONS_NORMAL = {
    "Electrode.Unwinder": [
        "[01] Electrode. Unwinder", "[02] Electrode. Unwinder",
        "[01] Pancake. Air Chuck", "[02] Pancake. Air Chuck",
        "[01] Electrode. Spool EPC", "[02] Electrode. Spool EPC",
        "[01] Electrode. Splicer", "[02] Electrode. Splicer",
        "[01] Door", "[02] Door"
    ],
    "Separator.Unwinder": [
        "[01/Upper] Separator. Unwinder", "[02/Upper] Separator. Unwinder",
        "[01/Upper] Separator. Winder", "[02/Upper] Separator. Winder",
        "[01/Lower] Separator. Unwinder", "[02/Lower] Separator. Unwinder",
        "[01/Lower] Separator. Winder", "[02/Lower] Separator. Winder",
        "[02/Upper] Pancake. Air Chuck", "[03/Upper] Pancake. Air Chuck",
        "[02/Lower] Pancake. Air Chuck", "[03/Lower] Pancake. Air Chuck",
        "[01/Upper] Pancake. Air Chuck", "[04/Upper] Pancake. Air Chuck",
        "[01/Lower] Pancake. Air Chuck", "[04/Lower] Pancake. Air Chuck",
        "[01/Upper] Separator. Splicer", "[02/Upper] Separator. Splicer",
        "[01/Lower] Separator. Splicer", "[02/Lower] Separator. Splicer"
    ],
    "Electrode/Separator.Combiner": [
        "[Upper] Electrode. Conveyor", "[Center] Electrode. Conveyor", "[Lower] Electrode. Conveyor",
        "[01] Electrode / Separator. Combiner Conveyor", "[02] Electrode / Separator. Combiner Conveyor",
        "[Upper] Electrode. EPC", "[Center] Electrode. EPC", "[Lower] Electrode. EPC",
        "[Upper] Separator. EPC", "[Lower] Separator. EPC",
        "[Upper] Electrode. Cutter", "[Center] Electrode. Cutter", "[Lower] Electrode. Cutter",
        "Electrode. Dancer", "[Upper] Separator. Dancer", "[Lower] Separator. Dancer",
        "[01/Upper] PET (Separator). Dancer", "[02/Upper] PET (Separator). Dancer",
        "[01/Lower] PET (Separator). Dancer", "[02/Lower] PET (Separator). Dancer",
        "[Upper] Electrode. Cutting Linear", "[Center] Electrode. Cutting Linear", "[Lower] Electrode. Cutting Linear"
    ],
    "Laminator": [
        "[Upper] Heater", "[Lower] Heater",
        "[Upper] Sub Heater", "[Lower] Sub Heater",
        "[Upper] Lamination Roller", "[Lower] Lamination Roller",
        "[Upper] PET. Cleaner", "[Lower] PET. Cleaner",
        "[01/Upper] PET. Dancer", "[01/Lower] PET. Dancer",
        "[02/Upper] PET. Dancer", "[02/Lower] PET. Dancer",
        "[Upper] PET. Unwinder", "[Lower] PET. Unwinder",
        "[Upper] PET. Winder", "[Lower] PET. Winder",
        "Uncut Cell. Dancer", "[Upper] PET. Splicer", "[Lower] PET. Splicer",
        "Separator. Sealer", "Separator. Sealing Linear"
    ],
    "Final Cell Cutter": [
        "Uncut Cell. Conveyor", "Cell. Conveyor",
        "Cell. Cutter", "Electrode. Cutting Linear"
    ],
    "Cell.Inspector": [
        "Cell. Conveyor", "Cell. Gripper",
        "[01] Cell. Vision Inspector", "Cell. Short Inspector",
        "[02] Cell. Vision Inspector", "Cell. Linear"
    ],
    "Cell.Unloader": [
        "[01] Cell. Pusher", "[02] Cell. Pusher",
        "[01] NG Cell. Ejector", "[02] NG Cell. Ejector", "[03] NG Cell. Ejector",
        "Cell. Suction Conveyor", "[01] Cell. Buffer Lift", "[02] Cell. Buffer Lift"
    ],
    "Magazine Buffer": [
        "[01] Magazine. Lift", "[02] Magazine. Lift",
        "[01A] Magazine. Conveyor", "[01B] Magazine. Conveyor",
        "[02A] Magazine. Conveyor", "[02B] Magazine. Conveyor"
    ],
    "Cell.Conveyor": [
        "Cell. Suction Conveyor"
    ],
    "Cell.Distributor": [
        "Cell. Pick & Place (Delta)",
        "[A] Cell. Suction Conveyor", "[B] Cell. Suction Conveyor"
    ],
    "Cell.Aligner": [
        "[A] Cell. Gripper", "[B] Cell. Gripper", "[A] Cell. Vision",
        "[C] Cell. Gripper", "[D] Cell. Gripper", "[B] Cell. Vision"
    ],
    "Cell.Stacking Table": [
        "[A] Cell. Vision", "[B] Cell. Vision",
        "[1A] Stacking Table", "[2A] Stacking Table", "[1B] Stacking Table", "[2B] Stacking Table",
        "[1A] Finger Clamp", "[1B] Finger Clamp", "[1C] Finger Clamp", "[1D] Finger Clamp",
        "[2A] Finger Clamp", "[2B] Finger Clamp", "[2C] Finger Clamp", "[2D] Finger Clamp",
        "[1A] Cell. Lift", "[2A] Cell. Lift", "[1B] Cell. Lift", "[2B] Cell. Lift"
    ],
    "Stacked Cell.Transfer": [
        "[A] Stacked Cell. Transfer", "[B] Stacked Cell. Transfer",
        "[A] Stacked Cell. Gripper", "[B] Stacked Cell. Gripper"
    ],
    "Stacked Cell.Loader": [
        "[A] Air. Supply", "[B] Air. Supply",
        "[A] Stacked Cell. Rotating Table", "[B] Stacked Cell. Rotating Table",
        "[A] Stacked Cell. Transfer", "[B] Stacked Cell. Transfer"
    ],
    "LMS": [
        "Stacked Cell. Shuttle", "Stacked Cell. Clamp"
    ],
    "Half Cell.Stacker": [
        "Air. Supply", "[Upper] Half Cell. Vision", "[Lower] Half Cell. Vision",
        "SCARA Robot", "Half Cell. Pick&Place",
        "[01] Half Cell. Lift", "[02] Half Cell. Lift",
        "[01] Half Cell. Rotating Table", "[02] Half Cell. Rotating Table", "Half Cell. Table"
    ],
    "Stacked Cell.Taper": [
        "[01] Stacked Cell. Press", "[02] Stacked Cell. Press",
        "[A] Tape. Attacher", "[B] Tape. Attacher",
        "[1A] Tape. Feeder", "[2A] Tape. Feeder", "[3A] Tape. Feeder",
        "[1B] Tape. Feeder", "[2B] Tape. Feeder", "[3B] Tape. Feeder",
        "[1A] Tape. Clamp", "[2A] Tape. Clamp", "[3A] Tape. Clamp",
        "[1B] Tape. Clamp", "[2B] Tape. Clamp", "[3B] Tape. Clamp"
    ],
    "Stacked Cell.Unloader": [
        "Air. Supply", "Taped Cell. Lift"
    ],
    "Taped Cell.Vision": [
        "Taped Cell. Pick&Place", "[Upper] Taped Cell. Vision",
        "[Lower] Taped Cell. Vision", "Taped Cell. Transfer"
    ],
    "Taped Cell.Weight Inspector": [
        "Taped Cell. Pick&Place", "[Upper] Taped Cell. Weight Inspector"
    ],
    "Taped Cell.Short hecker": [
        "Taped Cell. Dual Transfer", "Taped Cell. Short Checker",
        "[01] Taped Cell. Table", "[02] Taped Cell. Table"
    ],
    "Taped Cell.Transfer Unit": [
        "Taped Cell. Pick&Place", "NG Box (vision)", "NG Box (weight)", "NG Box (short)",
        "NG Box Lift (vision)", "NG Box Lift (weight)", "NG Box Lift (short)", "OK Cell. Conveyor"
    ],
    "Taped Cell.Unloader": [
        "Taped Cell. Pick&Place", "Taped Cell. Conveyor", "Tray. Conveyor", "Tray (Empty). Conveyor"
    ]
}