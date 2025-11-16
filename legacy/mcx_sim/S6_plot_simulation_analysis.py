import os
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import json
import argparse
import scienceplots
plt.style.use('science')

def GetCV(folder: str, run_start_idx: int, run_end_idx: int) -> (dict,list,list):
    # initial CV_set for saving
    filepath = os.path.join(folder, f"run_{run_start_idx}", "post_analysis", f"run_{run_start_idx}_simulation_result.json")
    with open(filepath, 'r') as f:
        data = json.load(f)
    GroupingSampleCV = data["GroupingSampleCV"]
    AnalyzedSampleNum = data["AnalyzedSampleNum"]
    CV_set = {}
    for using_SDS in GroupingSampleCV.keys():
        CV_set[using_SDS] = []
    SDS_used = list(GroupingSampleCV.keys())
    
    # initial used_total_photon  for saving
    used_total_photon = []
    
    # for each folder get the CV results then save with different SDS
    for i in range(run_start_idx, run_end_idx+1):
        filepath = os.path.join(folder, f"run_{i}", "post_analysis", f"run_{i}_simulation_result.json")
        with open(filepath, 'r') as f:
            data = json.load(f)
        GroupingSampleCV = data["GroupingSampleCV"]
        AnalyzedSampleNum = data["AnalyzedSampleNum"]
        SimBasedPhotonNum = float(data["PhotonNum"]["RawSample"])
        
        # save CV results
        for using_SDS in GroupingSampleCV.keys():
            using_CV = GroupingSampleCV[using_SDS]
            predicted_CV = using_CV/(AnalyzedSampleNum**0.5)
            CV_set[using_SDS].append(predicted_CV)
        
        # save total photon used
        used_total_photon = AnalyzedSampleNum*SimBasedPhotonNum
    
    return CV_set, SDS_used, used_total_photon

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
    CV_set, SDS_used, used_total_photon = GetCV(folder, run_start_idx, run_end_idx)     
    
    os.makedirs(os.path.join("pic", result_mother_folder, train_or_test, f"{subject}_{ijv_type}"), exist_ok=True)
    # plot CV results
    for using_SDS in SDS_used:
        plt.figure()
        plt.title(f'{using_SDS}')
        plt.scatter([i for i in range(run_start_idx, run_end_idx+1)], CV_set[using_SDS])
        plt.xlabel("MCX sim order")
        plt.ylabel("CV(\%)")
        plt.savefig(os.path.join("pic", result_mother_folder, train_or_test, f"{subject}_{ijv_type}", f"{using_SDS}.png"), dpi=300, format='png', bbox_inches='tight')
        plt.close()
    
    # plot used photon results
    plt.figure()
    plt.scatter([i for i in range(run_start_idx, run_end_idx+1)], used_total_photon)
    plt.xlabel("MCX sim order")
    plt.ylabel("Number Photons")
    plt.savefig(os.path.join("pic", result_mother_folder, train_or_test, f"{subject}_{ijv_type}", f"total_photons.png"), dpi=300, format='png', bbox_inches='tight')
    plt.close()
