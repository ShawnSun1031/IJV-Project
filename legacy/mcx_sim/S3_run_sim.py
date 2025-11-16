from mcx_ultrasound_opsbased import MCX
import calculateR_CV
import json
import os
import numpy as np
from glob import glob
from time import sleep
from tqdm import tqdm
import time
import argparse

# %% run
class Timer():
    """
    This is the clock timer, only measure how long we take to do simulations.
    """
    def __init__(self):
        self.o = time.time()

    def measure(self, p=1):
        x = (time.time() - self.o) / p
        x = int(x)
        if x >= 3600:
            return '{:.1f}h'.format(x / 3600)
        if x >= 60:
            return '{}m'.format(round(x / 60))
        return '{}s'.format(x)

def run_mcx(result_mother_folder: str, subject: str, mus_start: int, mus_end: int, NA_enable: int, 
            NA: float, runningNum: int, cvThreshold: float, repeatTimes: int, ijv_type: str, train_or_test: str):
    """_summary_

    Args:
        result_mother_folder (str): mother folder of simulation results.
        subject (str): subject name
        mus_start (int): the starting idx of configuration in mus_set.
        mus_end (int): the ending idx of configuration in mus_set.
        NA_enable (int): [1|0], 1: consider NA, 0: not consider NA.
        NA (float): numerical aperture of detector
        runningNum (int): Run {runningNum} times simulations then stop.
        cvThreshold (float): Do simulation until CV < cvThreshold
        repeatTimes (int): Repeat {repeatTimes} times, for first stage to calculate CV.
        ijv_type (str): ['ijv_large' | 'ijv_small']
        train_or_test (str): ['train' | 'test']
    """
    timer = Timer()
    ID = f'{subject}_{ijv_type}'
    for run_idx in tqdm(range(mus_start, mus_end+1)):
        now = time.time()
        
        # Setting
        session = f"run_{run_idx}"
        sessionID = os.path.join("dataset", result_mother_folder, train_or_test, ID, session)
        
        # Do simulation
        # initialize
        simulator = MCX(sessionID)
        
        # load config 
        with open(os.path.join(sessionID, "config.json")) as f:
            config = json.load(f)
        simulationResultPath = os.path.join(config["OutputPath"], session, "post_analysis", f"{session}_simulation_result.json")
        with open(simulationResultPath) as f:
            simulationResult = json.load(f)
        existedOutputNum = simulationResult["AnalyzedSampleNum"]
        
        # run forward mcx
        if runningNum:
            for idx in range(existedOutputNum, existedOutputNum+runningNum):
                # run
                simulator.run(idx)
                if NA_enable:
                    simulator.NA_adjust(NA)
            mean, CV = calculateR_CV.calculate_R_CV(sessionID, session, "mua_test.json")
            print(f" Session name: {sessionID} \n Reflectance mean: {mean} \nCV: {CV} ", end="\n\n")

        else:
            # run stage1 : run N sims to precalculate CV
            for idx in range(existedOutputNum, existedOutputNum+repeatTimes):
                # run
                simulator.run(idx)
                if NA_enable:
                    simulator.NA_adjust(NA)
            # calculate reflectance
            mean, CV = calculateR_CV.calculate_R_CV(sessionID, session, "mua_test.json")
            print(f"Session name: {sessionID} \n" \
                  f"Reflectance mean: {mean} \n" \
                  f"CV: {CV} \n" \
                  f"Predict CV: {CV/np.sqrt(repeatTimes+existedOutputNum)}" , end="\n\n")
            # run stage2 : run more sim to make up cvThreshold
            predict_CV = max(CV)/np.sqrt(repeatTimes+existedOutputNum)
            old_needAddOutputNum = 0
            while (predict_CV > cvThreshold):
                needAddOutputNum = int(np.ceil((max(CV)**2)/(cvThreshold**2)) - (repeatTimes+existedOutputNum))
                if needAddOutputNum > 0:
                    for idx in range(repeatTimes+existedOutputNum+old_needAddOutputNum, repeatTimes+existedOutputNum+old_needAddOutputNum+needAddOutputNum):
                        # run
                        simulator.run(idx)
                        if NA_enable:
                            simulator.NA_adjust(NA)
                    # calculate reflectance
                    mean, CV = calculateR_CV.calculate_R_CV(sessionID, session, "mua_test.json")
                    print(f"Session name: {sessionID} \n" \
                        f"Reflectance mean: {mean} \n" \
                        f"CV: {CV} \n" \
                        f"Predict CV: {CV/np.sqrt(repeatTimes+existedOutputNum+needAddOutputNum)}", end="\n\n")
                    
                    predict_CV = max(CV)/np.sqrt(repeatTimes+existedOutputNum+needAddOutputNum)
                    old_needAddOutputNum += needAddOutputNum
                else:
                    break
                    
            with open(simulationResultPath) as f:
                simulationResult = json.load(f)
            simulationResult['elapsed time'] = time.time() - now
            with open(simulationResultPath, "w") as f:
                json.dump(simulationResult, f, indent=4)

        print('ETA:{}/{}'.format(timer.measure(),
                                 timer.measure(run_idx / mus_end)))
        sleep(0.01)

#%%
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--root", type=str, help="This is the result mother folder")
    parser.add_argument("-s", "--subject", type=str, help="This is the subject name")
    parser.add_argument("--ijv_type", type=str, choices=["ijv_large", "ijv_small"], help="This is the ijv structure you want to simulate")
    parser.add_argument("--start", type=int, help="Choice the starting number of simulation folder")    
    parser.add_argument("--end", type=int, help="Choice the end of the simulation folder")
    parser.add_argument("-T", "--cvThreshold", type=float, help="This is the stop criterion for simulation")
    parser.add_argument("-n", "--runningNum", type=int, default=0, help="You want to run N times simulation then stop")
    parser.add_argument("-p", "--repeatTimes", type=int, help="You want to first repeat n times then calculate CV")
    parser.add_argument("-t", "--datatype", type=str, choices=['train', 'test'], help="Choose to generate training set or testing set")
    parser.add_argument("--NA_enable", type=int, choices=[0, 1], help="0 not consider NA, 1 consider NA")
    parser.add_argument("--NA", type=float, help="This is the fiber NA you use in the experiment")
    args = parser.parse_args()
    
    # ====================== Modify your setting here / get parser ====================== #
    result_mother_folder = args.root
    subject = args.subject
    ijv_type = args.ijv_type
    mus_start = args.start
    mus_end = args.end
    NA_enable = args.NA_enable  # 0 not consider NA, 1 consider NA
    NA = args.NA
    runningNum = args.runningNum  # (Integer or False) 
    cvThreshold = args.cvThreshold
    repeatTimes = args.repeatTimes # repeat n times to calculate CV
    train_or_test = args.datatype
    # ==================================================================================== #
    
    run_mcx(result_mother_folder = result_mother_folder, 
            subject = subject, 
            mus_start = mus_start, 
            mus_end = mus_end, 
            NA_enable = NA_enable,
            NA = NA, 
            runningNum = runningNum, 
            cvThreshold = cvThreshold, 
            repeatTimes = repeatTimes, 
            ijv_type = ijv_type,
            train_or_test= train_or_test)
    print("====================== Finish MCX Simulation !! ======================")