import os
import numpy as np
import argparse

def MCX_check(folder: str, run_start_idx: int, run_end_idx: int):
    """Checkinig if there are missing MCX simulation files.

    Args:
        folder (str): the folder you want to check
        run_start_idx (int): checking start folder
        run_end_idx (int): checkin end fodler
    """
    record = []
    for i in range(run_start_idx, run_end_idx+1):
        filepath = os.path.join(
            folder, f"run_{i}", "post_analysis", f"run_{i}_simulation_result.json")
        if not os.path.isfile(filepath):
            record.append(i)
    if record != []:
        print(f"MCX sim checking folder: {folder}...")
        for i in record:
            print(f"run_{i} ", end=" ")
        print("doesn`t exist!")
    else:
        print(f"{folder} MC sim all complete")


def WMC_check(result_mother_folder: str, folder: str, run_start_idx: int, run_end_idx: int):
    """Checkinig if there are missing WMC files.

    Args:
        result_mother_folder (str): result mother folder
        folder (str): the folder you want to check
        run_start_idx (int): checking start folder
        run_end_idx (int): checkin end fodler
    """
    record = []
    nan = []
    for i in range(run_start_idx, run_end_idx+1):
        filepath = os.path.join(folder, f"{result_mother_folder}_mus_{i}.npy")
        if not os.path.isfile(filepath):
            record.append(i)
        else:
            data = np.load(filepath)
            if np.isnan(data).any():
                nan.append(i)
    if record != []:
        print(f"{folder} WMC sim...")
        for i in record:
            print(f"run_{i} ", end=" ")
        print("doesn`t exist!")
    else:
        print(f"{folder} WMC sim all complete")

    if nan != []:
        for i in nan:
            print(f"run_{i}", end=" ")
        print("has nan!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--root", type=str, help="This is the result mother folder")
    parser.add_argument("-s", "--subject", type=str, help="This is the subject name")
    parser.add_argument("--start", type=int, help="Choice the starting number of simulation folder")    
    parser.add_argument("--end", type=int, help="Choice the end of the simulation folder")
    parser.add_argument("-t", "--datatype", type=str, choices=['train', 'test'], help="Choose to generate training set or testing set")
    parser.add_argument("--ijv_type", type=str, choices=["ijv_large", "ijv_small"], help="This is the ijv structure you want to simulate")
    args = parser.parse_args()
    # ====================== Modify your setting here / get parser ====================== #
    result_mother_folder = args.root
    subject = args.subject
    run_start_idx = args.start
    run_end_idx = args.end
    train_or_test = args.datatype
    ijv_type = args.ijv_type
    # =================================================================================== #
    
    folder = os.path.join("dataset", result_mother_folder, train_or_test, f"{subject}_{ijv_type}")
    MCX_check(folder, run_start_idx, run_end_idx)
    folder = os.path.join("dataset", result_mother_folder, train_or_test, f"{subject}_WMC_{ijv_type}")
    WMC_check(result_mother_folder, folder, run_start_idx, run_end_idx)
