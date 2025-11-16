from glob import glob
import os
import json
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import sys
os.chdir(sys.path[0])
plt.close("all")
plt.rcParams.update({"mathtext.default": "regular"})
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["figure.dpi"] = 300


# %% parameters and function
# parameters
tissueType = ["skin", "fat", "muscle", "blood"]
wlFiteredStart = 630
wlFilteredEnd = 1000
wlProjectStart = 700
wlProjectEnd = 900
muspBaseWl = (wlProjectStart+wlProjectEnd)/2
wlProject = np.linspace(wlProjectStart, wlProjectEnd, num=201)

# function


def calculateMusp(wl, a, b):
    musp = a * (wl/muspBaseWl) ** (-b)
    return musp


# %% main
# present raw data and curve-fit data
musRange = {}
interpData = {}
save_ab = {}
musRange["__comment__"] = "The mus upper bound and lower bound below are all in unit of [1/mm]."
for tissue in tissueType:
    musp = {}
    muspPathSet = glob(os.path.join(tissue, "musp", "*.csv"))
    interpData[tissue] = {}
    save_ab[tissue] = {}
    for muspPath in muspPathSet:
        # read values, select wavelength, and save
        name = muspPath.split("/")[-1].split(".")[0]
        df = pd.read_csv(muspPath)
        if tissue != "blood":
            # convert 1/cm to 1/nn when tissue's type is not "blood".
            df.musp = df.musp/10
        df = df[df.wavelength >= wlFiteredStart]
        df = df[df.wavelength <= wlFilteredEnd]
        musp[name] = {}
        musp[name]["values"] = df

        # curve fit
        popt, pcov = curve_fit(
            calculateMusp, df.wavelength.values, df.musp.values)
        musp[name]["(a,b)"] = popt

        # plot
        plt.plot(df.wavelength.values, df.musp.values, marker=".", label=name)
        plt.plot(np.linspace(df.wavelength.values[0], df.wavelength.values[-1], num=100),
                 calculateMusp(np.linspace(
                     df.wavelength.values[0], df.wavelength.values[-1], num=100), *popt),
                 color=plt.gca().lines[-1].get_color(), linestyle="--", label=name+" - fit")
    plt.legend()
    plt.xlabel("wavelength [nm]")
    plt.ylabel("musp [1/cm]")
    plt.title(tissue + "'s musp")
    plt.show()

    # present curve-fit data only in project wavelength range and output largest and smallest musp, mus
    ab = np.empty((len(musp), 2))
    for idx, name in enumerate(musp.keys()):
        # rearrange (a,b)
        ab[idx] = musp[name]["(a,b)"]
        # plot curve-fit data
        plt.plot(wlProject,
                 calculateMusp(wlProject, *ab[idx]), label=name+" - fit")
        if tissue == "blood":
            interpData[tissue][name] = calculateMusp(
                wlProject, *ab[idx])/(1-0.95)
        else:
            interpData[tissue][name] = calculateMusp(
                wlProject, *ab[idx])/(1-0.9)
        save_ab[tissue][name] = musp[name]["(a,b)"]

    if tissue == "blood":
        g = 0.95
    else:
        g = 0.9
    # find smallest and largest musp, mus values
    bottomSteepestMusp = calculateMusp(
        wlProject, ab.min(axis=0)[0], ab.max(axis=0)[1])
    minMus = bottomSteepestMusp.min()/(1-g)
    print("Smallest {}'s mus: {:.4e}. (a,b) = ({:.3e}, {:.3e}). The mus: {}".format(tissue, bottomSteepestMusp.min(),
                                                                                     ab.min(axis=0)[
        0],
        ab.max(axis=0)[
        1],
        minMus))
    topSteepestMusp = calculateMusp(
        wlProject, ab.max(axis=0)[0], ab.max(axis=0)[1])
    maxMus = topSteepestMusp.max()/(1-g)
    print("Largest {}'s mus: {:.4e}. (a,b) = ({:.3e}, {:.3e}). The mus: {}".format(tissue, topSteepestMusp.max(),
                                                                                    ab.max(axis=0)[
        0],
        ab.max(axis=0)[
        1],
        maxMus), end="\n\n")
    plt.plot(wlProject, bottomSteepestMusp, linestyle="--", color="gray")
    plt.plot(wlProject, topSteepestMusp, linestyle="--", color="gray")
    plt.legend()
    plt.xlabel("wavelength [nm]")
    plt.ylabel("musp [1/mm]")
    plt.title(tissue + "'s mus - only fit (project wl)")
    plt.savefig(os.path.join('pic', f"{tissue}_mus.png"))
    plt.show()

    # save mus
    # divided by 10 to convert to mm^-1
    musRange[tissue] = [np.ceil(maxMus), np.floor(minMus)]

with open("mus_bound.json", "w") as f:
    json.dump(musRange, f, indent=4)

# %% output need parameter
output_wavelength = [730, 760, 790, 810, 850]
output_parameter = {}
output_parameter['__comment__'] = "The mus upper bound and lower bound below are all in unit of [1/mm]."
for wl in output_wavelength:
    output_parameter[f'{wl}nm'] = {}
for tissue in interpData.keys():
    for wl in output_wavelength:
        find_wl_idx = np.where(wlProject == wl)[0]
        pd_interpData = pd.DataFrame(interpData[tissue])
        get_values = pd_interpData.iloc[find_wl_idx].to_numpy()
        output_parameter[f'{wl}nm'][tissue] = [np.nanmax(get_values), np.nanmin(
            get_values)]  # divied by 10 to convert to mm^-1

with open("mus_wl_bound.json", "w") as f:
    json.dump(output_parameter, f, indent=4)

# %% save ab
output_ab = {}
output_ab['__comment__'] = "This is mus fitting upper bound a and lower bound b (a*(wl/800nm)^-b"
for tissue in save_ab.keys():
    output_ab[tissue] = {}
for tissue in save_ab.keys():
    pd_save_ab = pd.DataFrame(save_ab[tissue])
    get_values = pd_save_ab.to_numpy()
    output_ab[tissue]['max'] = [*get_values.max(axis=1)]
    output_ab[tissue]['min'] = [*get_values.min(axis=1)]

with open("mus_ab_bound.json", "w") as f:
    json.dump(output_ab, f, indent=4)
