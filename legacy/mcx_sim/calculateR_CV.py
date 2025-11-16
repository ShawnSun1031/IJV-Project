import numpy as np
import jdata as jd
import os
from glob import glob
import json


def calculate_R_CV(sessionID, session, muaPath):
    with open(os.path.join(sessionID, muaPath)) as f:
        mua = json.load(f)
    muaUsed = [mua["1: Air"],
               mua["2: PLA"],
               mua["3: Prism"],
               mua["4: Skin"],
               mua["5: Fat"],
               mua["6: Muscle"],
               mua["7: Muscle or IJV (Perturbed Region)"],
               mua["8: IJV"],
               mua["9: CCA"]
               ]
    mua = np.array(muaUsed)
    with open(os.path.join(sessionID, "config.json")) as f:
        config = json.load(f)  # about detector na, & photon number
    with open(os.path.join(sessionID, "model_parameters.json")) as f:
        # about index of materials & fiber number
        modelParameters = json.load(f)
    fiberSet = modelParameters["HardwareParam"]["Detector"]["Fiber"]
    # about paths of detected photon data
    detOutputPathSet = glob(os.path.join(
        config["OutputPath"], session, "mcx_output", "*.jdat"))
    photonNum = int(config["PhotonNum"])
    detOutputPathSet.sort(key=lambda x: int(x.split("_")[-2]))
    detectorNum = len(fiberSet)*3*2
    reflectance = np.empty((len(detOutputPathSet), detectorNum))

    for detOutputIdx, detOutputPath in enumerate(detOutputPathSet):
        # main
        # sort (to make calculation of cv be consistent in each time)
        detOutput = jd.load(detOutputPath)
        info = detOutput["MCXData"]["Info"]
        photonData = detOutput["MCXData"]["PhotonData"]

        # unit conversion for photon pathlength
        photonData["ppath"] = photonData["ppath"] * info["LengthUnit"]

        photonData["detid"] = photonData["detid"] - 1  # shift detid from 0 to start

        for detectorIdx in range(info["DetNum"]):
            ppath = photonData["ppath"][photonData["detid"]
                                        [:, 0] == detectorIdx]
            # I = I0 * exp(-mua*L)
            weight = np.exp(-np.matmul(ppath, mua))
            reflectance[detOutputIdx][detectorIdx] = weight.sum() / photonNum

    left_right_reflectance = reflectance.reshape(
        len(detOutputPathSet), len(fiberSet), 3, 2).mean(axis=-1)
    group_reflectance = left_right_reflectance.mean(axis=-1)
    mean = np.mean(group_reflectance, axis=0)
    std = np.std(group_reflectance, axis=0)
    CV = std/mean*100

    with open(os.path.join(config["OutputPath"], session, "post_analysis", f"{session}_simulation_result.json")) as f:
        result = json.load(f)

    result["AnalyzedSampleNum"] = group_reflectance.shape[0]

    result["GroupingSampleValues"] = {f"sds_{detectorIdx}": group_reflectance[:, detectorIdx].tolist(
    ) for detectorIdx in range(group_reflectance.shape[1])}

    result["GroupingSampleValues"] = {f"sds_{detectorIdx}": group_reflectance[:, detectorIdx].tolist(
    ) for detectorIdx in range(group_reflectance.shape[1])}
    result["GroupingSampleStd"] = {
        f"sds_{detectorIdx}": std[detectorIdx] for detectorIdx in range(std.shape[0])}
    result["GroupingSampleMean"] = {
        f"sds_{detectorIdx}": mean[detectorIdx] for detectorIdx in range(mean.shape[0])}
    result["GroupingSampleCV"] = {
        f"sds_{detectorIdx}": CV[detectorIdx] for detectorIdx in range(CV.shape[0])}

    with open(os.path.join(config["OutputPath"], session, "post_analysis", "{}_simulation_result.json".format(session)), "w") as f:
        json.dump(result, f, indent=4)

    return mean, CV


# %%
if __name__ == "__main__":
    sessionID = "large_ijv_mus_baseline"
    muaPath = "mua.json"
    group_reflectance, CV = calculate_R_CV(sessionID, muaPath)
