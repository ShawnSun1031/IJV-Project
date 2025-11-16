import numpy as np
import cupy as cp
import jdata as jd
import json
import os
from glob import glob
from tqdm import tqdm
import argparse

#%%
class post_processing:

    def __init__(self, result_mother_folder: str, train_or_test: str, ID: str, datasetpath: str, USED_SDS: np.ndarray, 
                 mua_set: np.ndarray, mus_set: np.ndarray, 
                 air_mua: float=0, PLA_mua: float=10000, prism_mua:float=0):
        self.result_mother_folder = result_mother_folder
        self.train_or_test = train_or_test
        self.ID = ID
        self.datasetpath = datasetpath
        self.USED_SDS = cp.array(USED_SDS) # convert to GPU type
        self.mua_set = mua_set
        self.total_mua_conditions = mua_set.shape[0]
        self.mus_set = mus_set
        self.total_mus_conditions = mus_set.shape[0]
        
        self.air_mua = air_mua
        self.PLA_mua = PLA_mua
        self.prism_mua = prism_mua
    
        # process mua set
        if self.ID.find("small") != -1:
            self.mua_used = np.array([self.total_mua_conditions*[self.air_mua],
                                      self.total_mua_conditions*[self.PLA_mua],
                                      self.total_mua_conditions*[self.prism_mua],
                                      list(self.mua_set[:, 0]),  # skin mua
                                      list(self.mua_set[:, 1]),  # fat mua
                                      list(self.mua_set[:, 2]),  # musle mua
                                      # perturbed region = musle
                                      list(self.mua_set[:, 2]),
                                      list(self.mua_set[:, 3]),  # IJV mua
                                      list(self.mua_set[:, 4])  # CCA mua
                                      ])
        elif self.ID.find("large") != -1:
            self.mua_used = np.array([self.total_mua_conditions*[self.air_mua],
                                      self.total_mua_conditions*[self.PLA_mua],
                                      self.total_mua_conditions*[self.prism_mua],
                                      list(self.mua_set[:, 0]),  # skin mua
                                      list(self.mua_set[:, 1]),  # fat mua
                                      list(self.mua_set[:, 2]),  # musle mua
                                      # perturbed region = IJV mua
                                      list(self.mua_set[:, 3]),
                                      list(self.mua_set[:, 3]),  # IJV mua
                                      list(self.mua_set[:, 4])  # CCA mua
                                      ])
        else:
            raise Exception("Something wrong in your ID name !")
    
    def create_folder(self):
        os.makedirs(os.path.join("dataset", self.result_mother_folder, self.train_or_test,
                self.datasetpath), exist_ok=True)
        
    # private method
    def __get_used_mus(self, mus_run_idx: int):
        self.mus_used = np.array([self.mus_set[mus_run_idx-1, 0],  # skin_mus
                            self.mus_set[mus_run_idx-1, 1],  # fat_mus
                            self.mus_set[mus_run_idx-1, 2],  # musle_mus
                            self.mus_set[mus_run_idx-1, 3],  # ijv_mus
                            self.mus_set[mus_run_idx-1, 4]  # cca_mus
                            ])
        return self.mus_used

    # private method
    def __get_config(self, mus_run_idx: int):
        self.session = f"run_{mus_run_idx}"
        with open(os.path.join(os.path.join(self.ID, self.session), "config.json")) as f:
            config = json.load(f)  # about detector na, & photon number
        with open(os.path.join(os.path.join(self.ID, self.session), "model_parameters.json")) as f:
            modelParameters = json.load(f) # about index of materials & fiber number
        self.photonNum = int(config["PhotonNum"])
        self.fiberSet = modelParameters["HardwareParam"]["Detector"]["Fiber"]
        
        # about paths of detected photon data
        self.detOutputPathSet = glob(os.path.join(config["OutputPath"], self.session, "mcx_output", "*.jdat"))
        self.detOutputPathSet.sort(key=lambda x: int(x.split("_")[-2]))
        self.detectorNum = len(self.fiberSet)*3*2
    
    def WMC(self, mus_run_idx: int):
        self.__get_config(mus_run_idx)
        dataset_output = np.empty([self.total_mua_conditions, 10+len(self.fiberSet)])
        
        used_mus = self.__get_used_mus(mus_run_idx)
        used_mus = np.tile(used_mus, self.total_mua_conditions).reshape(self.total_mua_conditions, 5)
        used_mua = cp.array(self.mua_used)
        
        reflectance = cp.zeros((self.detectorNum, self.total_mua_conditions))
        group_reflectance = cp.zeros((len(self.fiberSet), self.total_mua_conditions))
        
        for detOutputIdx, detOutputPath in enumerate(self.detOutputPathSet):
            # main
            # sort (to make calculation of cv be consistent in each time)
            detOutput = jd.load(detOutputPath)
            info = detOutput["MCXData"]["Info"]
            photonData = detOutput["MCXData"]["PhotonData"]
            photonData["ppath"] = photonData["ppath"] * info["LengthUnit"] # unit conversion for photon pathlength
            photonData["detid"] = photonData["detid"] - 1  # shift detid from 0 to start
            for detectorIdx in range(info["DetNum"]):
                ppath = cp.asarray(
                    photonData["ppath"][photonData["detid"][:, 0] == detectorIdx].astype(np.float64))

                # batch ppath for GPU use
                max_memory = 100000
                if ppath.shape[0] > max_memory:
                    for idx, ppath_idx in enumerate(range(0, ppath.shape[0]//max_memory)):
                        if idx == 0:
                            batch_ppath_reflectance = cp.exp(
                                -ppath[max_memory*(ppath_idx):max_memory*(ppath_idx+1)]@used_mua).sum(axis=0)
                            # print(f'idx ={max_memory*(ppath_idx)} ~ {max_memory*(ppath_idx+1)} \n   r : {batch_ppath_reflectance}')
                        else:
                            batch_ppath_reflectance += cp.exp(-ppath[max_memory*(
                                ppath_idx):max_memory*(ppath_idx+1)]@used_mua).sum(axis=0)
                            # print(f'idx ={max_memory*(ppath_idx)} ~ {max_memory*(ppath_idx+1)} \n   r : {batch_ppath_reflectance}')
                    batch_ppath_reflectance += cp.exp(-ppath[max_memory*(
                        ppath_idx+1):]@used_mua).sum(axis=0)
                    # print(f'idx =\{max_memory*(ppath_idx+1)} to last \n   r : {batch_ppath_reflectance}')
                else:
                    batch_ppath_reflectance = cp.exp(-ppath@used_mua).sum(axis=0)

                reflectance[detectorIdx][:] = batch_ppath_reflectance / self.photonNum
            for fiberIdx in range(len(self.fiberSet)):
                group_reflectance[fiberIdx][:] = group_reflectance[fiberIdx][:] + \
                    cp.mean(reflectance[self.USED_SDS][:], axis=0)
                self.USED_SDS = self.USED_SDS + 2*3

        output_R = (group_reflectance/(detOutputIdx+1)).T  # mean

        dataset_output[:, 10:] = cp.asnumpy(output_R)
        used_mua = used_mua[3:]  # truncate air_mua, PLA_mua, prism_mua, get mua of skin, fat, muscle, perturbed, IJV, CCA
        used_mua = cp.concatenate([used_mua[:3], used_mua[4:]]).T
        used_mua = cp.asnumpy(used_mua) # Nx : num of conditions, Ny : tissue
        dataset_output[:, :10] = np.concatenate([used_mus, used_mua], axis=1)
        
        return dataset_output

#%%
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
    
    USED_SDS = np.array([0, 1, 2, 3, 4, 5])
    mua_set = np.load(os.path.join("OPs_used", f"mua_set_{train_or_test}.npy"))
    mus_set = np.load(os.path.join("OPs_used", f"mus_set_{train_or_test}.npy"))
    ID = os.path.join("dataset", result_mother_folder, train_or_test, f"{subject}_{ijv_type}")
    datasetpath = f"{subject}_WMC_{ijv_type}"
    
    processsor = post_processing(result_mother_folder=result_mother_folder,
                                 train_or_test=train_or_test,
                                 ID=ID,
                                 datasetpath=datasetpath,
                                 USED_SDS=USED_SDS,
                                 mua_set=mua_set,
                                 mus_set=mus_set)
    processsor.create_folder()

    for mus_run_idx in tqdm(range(run_start_idx, run_end_idx+1)):
        print(f"\n Now run mus_set_{mus_run_idx} idx")
        dataset_output = processsor.WMC(mus_run_idx)
        np.save(os.path.join("dataset", result_mother_folder, train_or_test, datasetpath,
                f"{result_mother_folder}_mus_{mus_run_idx}.npy"), dataset_output)
    print("====================== Finish WMC!! ======================")
