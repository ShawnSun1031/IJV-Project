import os
import shutil
import json
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--root", type=str, help="This is the result mother folder")
parser.add_argument("-s", "--subject", type=str, help="This is the subject name")
parser.add_argument("-d", "--date", type=str, help="date of ultrasound data")
parser.add_argument("-n", "--PhotonNum", type=int, help="number of photon to simulate")
parser.add_argument("-v", "--VoxelSize", type=float, help="must be same when you create numeric model of IJV structure")
parser.add_argument("--NA", type=float, help="This is the fiber NA you use in the experiment")
args = parser.parse_args()

# ====================== Modify your setting here / get parser ====================== #
result_folder = args.root
subject = args.subject
date = args.date # date of ultrasound data
PhotonNum = args.PhotonNum
VoxelSize = args.VoxelSize # must be same when you create numeric model of IJV structure 
DetectorNA = args.NA
# ====================================================================== #

# %% run
train_or_test_set = ['train', 'test']
ijv_types = ['ijv_large', 'ijv_small']
# copy config.json ijv_dense_symmetric_detectors_backgroundfiber_pmc.json model_parameters.json mua_test.json to each sim
copylist = ["config.json",
            "ijv_dense_symmetric_detectors_backgroundfiber_pmc.json",
            "model_parameters.json",
            "mua_test.json"]
for train_or_test in train_or_test_set:
    mus_set = np.load(os.path.join("OPs_used", f"mus_set_{train_or_test}.npy"))
    for ijv_type in ijv_types:
        sessionID = f'{subject}_{ijv_type}'

        os.makedirs(os.path.join(
            "dataset", result_folder, train_or_test, sessionID), exist_ok=True)

        # create runfile folder
        for run_idx in range(1, mus_set.shape[0]+1):
            run_name = f"run_{run_idx}"
            os.makedirs(os.path.join("dataset", result_folder,
                        train_or_test, sessionID, run_name), exist_ok=True)
            for filename in copylist:
                src = os.path.join("input_template", filename)
                dst = os.path.join("dataset", result_folder,
                                train_or_test, sessionID, run_name, filename)
                shutil.copyfile(src, dst)

                if filename == "config.json":
                    with open(dst) as f:
                        config = json.load(f)
                    config["SessionID"] = run_name
                    config["PhotonNum"] = PhotonNum
                    config["BinaryPath"] = os.path.join(os.getcwd(), "bin")
                    config["VolumePath"] = os.path.join(os.getcwd(
                    ), "ultrasound_data", f"{subject}_{date}_merge_vol.npy")
                    config["MCXInputPath"] = os.path.join(os.getcwd(
                    ), "dataset", result_folder, train_or_test, sessionID, run_name, "ijv_dense_symmetric_detectors_backgroundfiber_pmc.json")
                    config["OutputPath"] = os.path.join(
                        os.getcwd(), "dataset", result_folder, train_or_test, sessionID)
                    config["Type"] = sessionID
                    config["VoxelSize"] = VoxelSize
                    config["DetectorNA"] = DetectorNA
                    with open(dst, "w") as f:
                        json.dump(config, f, indent=4)

                if filename == "ijv_dense_symmetric_detectors_backgroundfiber_pmc.json":
                    with open(dst) as f:
                        mcxInput = json.load(f)
                    # 0 : Fiber
                    # 1 : Air
                    # 2 : PLA
                    # 3 : Prism
                    # 4 : Skin
                    mcxInput["Domain"]["Media"][4]["mus"] = mus_set[run_idx-1][0]
                    # 5 : Fat
                    mcxInput["Domain"]["Media"][5]["mus"] = mus_set[run_idx-1][1]
                    # 6 : Muscle
                    mcxInput["Domain"]["Media"][6]["mus"] = mus_set[run_idx-1][2]
                    # 7 : Muscle or IJV (Perturbed Region)
                    if sessionID.find("small") != -1:
                        # muscle
                        mcxInput["Domain"]["Media"][7]["mus"] = mus_set[run_idx-1][2]
                    elif sessionID.find("large") != -1:
                        # ijv
                        mcxInput["Domain"]["Media"][7]["mus"] = mus_set[run_idx-1][3]
                    else:
                        raise Exception(
                            "Something wrong in your config[VolumePath] !")
                    # 8 : IJV
                    mcxInput["Domain"]["Media"][8]["mus"] = mus_set[run_idx-1][3]
                    # 9 : CCA
                    mcxInput["Domain"]["Media"][9]["mus"] = mus_set[run_idx-1][4]
                    with open(dst, "w") as f:
                        json.dump(mcxInput, f, indent=4)

                if filename == "model_parameters.json":
                    with open(dst) as f:
                        modelParameters = json.load(f)
                    modelParameters["OptParam"]["Skin"]["mus"] = mus_set[run_idx-1][0]
                    modelParameters["OptParam"]["Fat"]["mus"] = mus_set[run_idx-1][1]
                    modelParameters["OptParam"]["Muscle"]["mus"] = mus_set[run_idx-1][2]
                    modelParameters["OptParam"]["IJV"]["mus"] = mus_set[run_idx-1][3]
                    modelParameters["OptParam"]["CCA"]["mus"] = mus_set[run_idx-1][4]
                    modelParameters['HardwareParam']['Source']['Beam']['ProfilePath'] = os.path.join(
                        "input_template", "shared_files", "model_input_related")
                    with open(dst, "w") as f:
                        json.dump(modelParameters, f, indent=4)
