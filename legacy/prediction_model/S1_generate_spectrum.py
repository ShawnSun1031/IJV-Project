import numpy as np
import os
import random
import json
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl
import scienceplots
mpl.rcParams.update(mpl.rcParamsDefault)
plt.style.use('science')
plt.rcParams.update({'font.size': 36})
os.makedirs("pic", exist_ok=True)

# function
def calculateMus(wl, tissue, a, b):
    musp = a * (wl/MUSPBASEWL) ** (-b)
    if tissue == "blood":
        mus = musp/(1-0.95)
    else:
        mus = musp/(1-0.9)
    return mus

def plot_IJV_spectrum(ijv_gen, blc):
    plt.figure(figsize=(12,8))
    count = 0 # for plot train and test
    for idx, b in enumerate(blc):
        for k in ijv_gen.keys():   
            if k.find((str(b))) != -1: # plot each bloodConc as same set
                spec_numpy = pd.DataFrame(ijv_gen[k]).to_numpy()
                if (idx%3) == 0:
                    plt.plot(used_wl,spec_numpy.reshape(-1), 'b', alpha=0.7)
                    if count == 0:
                        plt.plot(used_wl,spec_numpy.reshape(-1), 'b',label='testing', alpha=0.5)
                        count += 1
                elif (idx%3) == 1:
                    plt.plot(used_wl,spec_numpy.reshape(-1), 'g', alpha=0.7)
                    if count == 0:
                        plt.plot(used_wl,spec_numpy.reshape(-1), 'g',label='validation', alpha=0.5)
                        count += 1
                else:
                    plt.plot(used_wl,spec_numpy.reshape(-1), 'r', alpha=0.7)
                    if count == 1:
                        plt.plot(used_wl,spec_numpy.reshape(-1), 'r', label='training', alpha=0.5)
                        count += 1    
    plt.xlabel('wavelength(nm)')
    plt.ylabel("$\mu_a$($mm^{-1}$)")
    plt.title('ijv $\mu_a$ spectrum')
    # plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join("pic", "ijv_mua.png"), dpi=300, format='png', bbox_inches='tight')
    plt.show()  

def plot_used_spectrum(tissue, spec, mua_or_mus):
    spec_numpy = pd.DataFrame(spec).to_numpy()
    plt.figure(figsize=(12,8))
    for idx, i in enumerate(range(spec_numpy.shape[0])):
        if (idx%3) == 0:
            plt.plot(used_wl,spec_numpy[i], 'b')
        elif (idx%3) == 1:
            plt.plot(used_wl,spec_numpy[i], 'g')
        elif (idx%3) == 2:
            plt.plot(used_wl,spec_numpy[i], 'r')
    plt.xlabel('wavelength(nm)')
    if mua_or_mus == "mus":
        plt.ylabel("$\mu_s$($mm^{-1}$)")
        plt.title(f'{tissue} $\mu_s$ spectrum')
    elif mua_or_mus == "mua":
        plt.ylabel("$\mu_a$($mm^{-1}$)")
        plt.title(f'{tissue} $\mu_a$ spectrum')
    # plt.legend(['testing','training'])
    
    plt.savefig(os.path.join("pic", f'{tissue}_{mua_or_mus}_spectrum.png'), dpi=300, format='png', bbox_inches='tight')
    plt.show()

def random_gen_mus(num, used_wl, tissue, a_max, a_min, b_max, b_min):
    a_list = list(np.linspace(a_max,a_min,num))
    random.shuffle(a_list)
    b_list = list(np.linspace(b_max,b_min,num))
    random.shuffle(b_list)
    spec = {}
    for wl in used_wl:
        spec[f'{wl}nm'] = []
    for i in range(num):
        for wl in used_wl:
            spec[f'{wl}nm'].append(calculateMus(wl, tissue, a_list[i], b_list[i]))
    
    return spec

def random_gen_mua(num, used_wl, tissue, mua_bound):
    spec = {}
    for wl in used_wl:
        spec[f'{wl}nm'] = []
    for wl in used_wl:
        [mua_max, mua_min] = mua_bound[f'{wl}nm'][tissue]
        mua = list(np.linspace(mua_max,mua_min,num))
        for i in range(num):
            spec[f'{wl}nm'].append(mua[i])
    
    return spec 

def random_gen_ijv_mua(used_wl,mua_bound, blc, bloodConc, SO2):
    spec = []
    for wl in used_wl:
        mua_min = mua_bound[f'{wl}nm'][f"ijv_bloodConc_{bloodConc[1]}_bloodSO2_{SO2:.2f}"][0]
        mua_max = mua_bound[f'{wl}nm'][f"ijv_bloodConc_{bloodConc[0]}_bloodSO2_{SO2:.2f}"][0]
        mua_new = mua_min + (blc-bloodConc[1])*(mua_max-mua_min)/(bloodConc[0]-bloodConc[1])
        spec.append(mua_new)

    return spec 

def random_gen_muscle_mua(num, used_wl, tissue, muscle_wl, blc, SO2, hbO2, hb, water):
    spec = {}
    for wl in used_wl:
        spec[f'{wl}nm'] = []
    for wl in used_wl:
        wl_idx = np.where(muscle_wl==wl)[0]
        # alpha = 1%
        spec[f'{wl}nm'] = list((2.303*0.12*blc*(SO2*hbO2[wl_idx]+(1-SO2)*hb[wl_idx])/64500) + (0.7*water[wl_idx]))
    
    return spec
    
if __name__ == "__main__":
    MUSPBASEWL = 800 #nm
    bloodConc = [174,138]
    SO2 = [i/100 for i in range(40,91,1)]
    used_wl = [700, 710, 717, 725, 732, 740, 743, 748, 751, 753, 
        758, 763, 768, 780, 792, 798, 805, 815, 830, 850]
    num = 30 # number of spectrum used
    
    with open(os.path.join("OPs_used","mus_ab_bound.json"),"r") as f:
        mus_ab_bound = json.load(f)
    with open(os.path.join("OPs_used","mua_wl_bound.json"),"r") as f:
        mua_bound = json.load(f)
    
    # mus_gen
    tissue = ['skin', 'fat', 'muscle', 'blood']
    mus_gen = {}
    for t in tissue:
        mus_spec = random_gen_mus(num, used_wl, t,  mus_ab_bound[f'{t}']['max'][0], mus_ab_bound[f'{t}']['min'][0], 
                                    mus_ab_bound[f'{t}']['max'][1], mus_ab_bound[f'{t}']['min'][1])
        mus_gen[t] = mus_spec
        plot_used_spectrum(t, mus_spec, "mus")
    
    # mua_gen --> for skin fat cca muscle
    tissue = ['skin', 'fat', 'cca', 'muscle']
    mua_gen = {}
    for t in tissue:
        mua_spec = random_gen_mua(num, used_wl, t, mua_bound)
        mua_gen[t] = mua_spec
        plot_used_spectrum(t, mua_spec, "mua")

    # mua_gen --> for ijv     
    ijv_gen = {}
    blc = np.linspace(bloodConc[0],bloodConc[1],num, dtype=int).tolist()
    random.shuffle(blc)
    for b in blc:
        ijv_save = np.empty((len(SO2), len(used_wl)+1)) # record SO2 + wavelength
        for idx, s in enumerate(SO2):
            ijv_spec = random_gen_ijv_mua(used_wl, mua_bound, b, bloodConc, s)
            ijv_gen[f"ijv_bloodConc_{b}_bloodSO2_{s}"] = ijv_spec
            ijv_save[idx] = np.array([s]+ijv_spec)
        columns = ['SO2'] + [f'{wl}_nm' for wl in used_wl]
        ijv_save = pd.DataFrame(ijv_save, columns=columns)
        ijv_save.to_csv(os.path.join("OPs_used", f"ijv_mua_bloodConc_{b}.csv"), index=False)
    plot_IJV_spectrum(ijv_gen, blc)

    mua_gen.update(ijv_gen)
    with open(os.path.join("OPs_used","mus_spectrum.json"), "w") as f:
        json.dump(mus_gen, f, indent=4)
    with open(os.path.join("OPs_used","mua_spectrum.json"), "w") as f:
        json.dump(mua_gen, f, indent=4)
    used_bloodConc = {'bloodConc' : blc}
    with open(os.path.join("OPs_used", "bloodConc.json"), "w") as f:
        json.dump(used_bloodConc, f, indent=4)
    used_wl = {'wavelength' : used_wl}
    with open(os.path.join('OPs_used', "wavelength.json"), "w") as f:
        json.dump(used_wl, f, indent=4)
    used_SO2 = {"train_SO2" : SO2[::5],
                "test_SO2" : SO2}
    with open(os.path.join("OPs_used", "SO2.json"), "w") as f:
        json.dump(used_SO2, f,indent=4)