from glob import glob
import os
import json
import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
from colour import Color
import matplotlib.pyplot as plt
import sys

# %% move to current file path
os.chdir(sys.path[0])

plt.close("all")
plt.rcParams.update({"mathtext.default": "regular"})
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["figure.dpi"] = 300


# %% parameters
tissueType = ["skin", "fat", "muscle", "blood"]
wlProjectStart = 700
wlProjectEnd = 900
wlProject = np.linspace(wlProjectStart, wlProjectEnd, num=201)
bloodConcSet = np.array([138, 174])
# bloodSO2Set = {"ijv": np.linspace(0.4, 0.9, 6),
#                "cca": np.linspace(0.9, 1.0, 2)
#                }  # for analysis of blood SO2
bloodSO2Set = {"ijv": np.array([i/100 for i in range(40, 91, 1)]),
               "cca": np.linspace(0.9, 1.0, 2)
               }  # for analysis of blood SO2
# [i/100 for i in range(44,90,5)]

# %% main
# read raw data, do interpolation, and plot
rawData = {}  # raw data
interpData = {}  # processed data
for tissue in tissueType:
    if tissue == "blood":
        epsilonHbO2HbPath = "blood/mua/epsilon_hemoglobin.txt"
        epsilonHbO2Hb = pd.read_csv(
            epsilonHbO2HbPath, sep="\t", names=["wl", "HbO2", "Hb"])
        cs = CubicSpline(epsilonHbO2Hb.wl.values,
                         epsilonHbO2Hb.HbO2.values, extrapolate=False)
        epsilonHbO2Used = cs(wlProject)  # [cm-1/M]
        cs = CubicSpline(epsilonHbO2Hb.wl.values,
                         epsilonHbO2Hb.Hb.values, extrapolate=False)
        epsilonHbUsed = cs(wlProject)  # [cm-1/M]
        muaHbO2Set = 2.303 * epsilonHbO2Used * \
            (bloodConcSet[:, None] / 64532)  # [1/cm]
        muaHbSet = 2.303 * epsilonHbUsed * \
            (bloodConcSet[:, None] / 64500)  # [1/cm]
        for key in bloodSO2Set.keys():
            interpData[key] = {}
            muaWholeBloodSet = muaHbO2Set * \
                bloodSO2Set[key][:, None, None] + muaHbSet * \
                (1-bloodSO2Set[key][:, None, None])  # [1/cm]
            # visualization
            colorSet = list(Color("lightcoral").range_to(
                Color("darkred"), bloodSO2Set[key].size))
            for i in range(muaWholeBloodSet.shape[0]):
                for j in range(muaWholeBloodSet[i].shape[0]):
                    if j == muaWholeBloodSet[i].shape[0]-1:
                        plt.plot(wlProject, muaWholeBloodSet[i][j], c=colorSet[i].get_hex(
                        ), label=np.round(bloodSO2Set[key][i], 1))
                    else:
                        plt.plot(
                            wlProject, muaWholeBloodSet[i][j], c=colorSet[i].get_hex())
            plt.legend()
            plt.xlabel("wl [nm]")
            plt.ylabel("mua [1/cm]")
            plt.title("{}'s mua in different SO2, conc={}".format(
                key, bloodConcSet))
            plt.savefig(os.path.join("pic", f"{key}_differentSO2"))
            plt.show()
            for SO2_idx, bloodSO2 in enumerate(bloodSO2Set[key]):
                for BC_idx, BC in enumerate(bloodConcSet):
                    interpData[key][f"Parah's data bloodConc {BC} bloodSO2 {bloodSO2}"] = muaWholeBloodSet[SO2_idx][BC_idx]
    else:
        interpData[tissue] = {}
        muaPathSet = glob(os.path.join(tissue, "mua", "*.csv"))
        for muaPath in muaPathSet:
            name = muaPath.split("/")[-1].replace(".csv", "")
            # read raw data
            df = pd.read_csv(muaPath)
            # rawData[tissue][name] = df
            # plot raw data
            plt.plot(df.wavelength.values, df.mua.values, label=name)
            # interpolate to wl-project and save
            cs = CubicSpline(df.wavelength.values,
                             df.mua.values, extrapolate=False)
            interpData[tissue][name] = cs(wlProject)
        plt.legend(fontsize="x-small")
        plt.xlabel("wavelength [nm]")
        plt.ylabel("mua [1/cm]")
        plt.title(tissue + "'s mua raw data")
        plt.savefig(os.path.join("pic", f"{tissue}_mua_raw_data"))
        plt.show()

# plot interpolated data
for tissue in tissueType:
    if tissue != "blood":
        for source, data in interpData[tissue].items():
            plt.plot(wlProject, data, label=source)
        plt.legend(fontsize="x-small")
        plt.xlabel("wavelength [nm]")
        plt.ylabel("mua [1/cm]")
        plt.title(tissue + "'s mua interp data")
        plt.savefig(os.path.join("pic", f"{tissue}_interp_mua"))
        plt.show()

# show mua upper bound and lower bound and save to .json file
muaRange = {}
muaRange["__comment__"] = "The mua upper bound and lower bound below are all in unit of [1/mm]."
for tissue in interpData.keys():
    tissue = 'ijv'
    allmua = np.array(list(interpData[tissue].values()))
    muaRange[tissue] = [np.ceil(np.nanmax(allmua)*1e3)/1e3/10, np.floor(
        np.nanmin(allmua)*1e3)/1e3/10]  # divided  by 10 to convert to mm^-1
    print(
        f"{tissue}'s mua ---> min={np.nanmin(muaRange[tissue])}, max={np.nanmax(muaRange[tissue])}")


with open("mua_bound.json", "w") as f:
    json.dump(muaRange, f, indent=4)

# %% output need parameter
output_wavelength = list(np.rint(np.linspace(700, 900, 200)).astype(int))
output_parameter = {}
output_parameter['__comment__'] = "The mua upper bound and lower bound below are all in unit of [1/mm]."
a = {}
for wl in output_wavelength:
    output_parameter[f'{wl}nm'] = {}
    a[f'{wl}nm'] = {}
for tissue in interpData.keys():
    for wl in output_wavelength:
        find_wl_idx = np.where(wlProject == wl)[0]
        pd_interpData = pd.DataFrame(interpData[tissue])
        if tissue == "ijv":
            for k in interpData[tissue].keys():
                bloodConc = k.split()[-3]
                bloodSO2 = k.split()[-1]
                output_parameter[f'{wl}nm'][f'{tissue}_bloodConc_{bloodConc}_bloodSO2_{float(bloodSO2):.2f}'] = list(
                    interpData[tissue][k][find_wl_idx]/10)  # divied by 10 to convert to mm^-1
        get_values = pd_interpData.iloc[find_wl_idx].to_numpy()
        output_parameter[f'{wl}nm'][tissue] = [np.nanmax(
            get_values)/10, np.nanmin(get_values)/10]  # divied by 10 to convert to mm^-1

with open("mua_wl_bound.json", "w") as f:
    json.dump(output_parameter, f, indent=4)
