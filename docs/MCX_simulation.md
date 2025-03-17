How to execute MCX_sim
===


[![hackmd-github-sync-badge](https://hackmd.io/ygh1d2wOSeuPGTxB9IZHEQ/badge)](https://hackmd.io/ygh1d2wOSeuPGTxB9IZHEQ)

## Table of Contents
- [Executing Experiments](/IJV-Project/MCX_simulation/#executing-experiments)
- [Beginners Guide](/IJV-Project/MCX_simulation/#beginners-guide)
- [Details for setting](/IJV-Project/MCX_simulation/#details-for-setting)
- [MCX forum](/IJV-Project/MCX_simulation/#mcx-forum)
- [MCX cloud](/IJV-Project/MCX_simulation/#mcx-cloud)
- [Analyze the output file from MCX](/IJV-Project/MCX_simulation/#analyze-the-output-file-from-mcx)
- [TODO](/IJV-Project/MCX_simulation/#todo)

## Executing Experiments

Make sure you already have /bin/MCX in this directory.
If not, compiled from **MD703_edit_MCX_src_v2023/src** in advance.*


You should use **linux** environment to do the following commands.
If you want to execute in **Windows**, you need to fix two problems carefully:
1. Compile the **MD703_edit_MCX_src_v2023/src** in **Windows**, we use a user-define LED source pattern to make the simulation in consistent with the experiments.
2. Write your own shell script in Windows version. (bash can't work, use batch)

```
bash Run_MCX_Sim.sh
```

please see **Run_MCX_Sim.sh** for details and understand the work flows.

## Beginners Guide

If you are a total beginner to this, start here!

1. Learn some syntax about shell script [https://blog.techbridge.cc/2019/11/15/linux-shell-script-tutorial/](https://blog.techbridge.cc/2019/11/15/linux-shell-script-tutorial/)
2. Read the document about MCX source code [https://github.com/fangq/mcx](https://github.com/fangq/mcx)

## Details for setting
[LED source]:  
1. in the folder **"input_template/share_files/model_input_related"** contains the CDF of LED source (multiplied by sin due to 3D).  
2. we edited the source code, to view what we edited check this [https://github.com/fangq/mcx/pull/194/files](https://github.com/fangq/mcx/pull/194/files)    
3. more detail about LED source [see here](/handover/eric/IJV_Notebook/#20210326-mcx_corecu)  
4. Geometry model setting [IJV | 組織模型設定 July, 2021 - Revised](https://hackmd.io/@73X8klpNRmSsdgJzudHbgA/Byo9D2iCO?fbclid=IwAR11h4vS-rScHVwF4zTrYSlFVayP8p63mHKPTCLOthZ6d3p3Kd0SmH1kyDI)  

[How we execute MCX]:
1. we use **mcx_ultrasound_opsbased.py** to access the executive file which is compiled from the source code

## MCX forum 
This is the google group of MCX.  
There are lots of conversation and discussion about utilization of MCX.  
https://groups.google.com/g/mcx-users

## MCX cloud 
When you run **S3_run_sim.py**, it will generate a file called **input_run_<#>_forpreview.json**. Copy the content and paste it in the MCX cloud to view the structure you designed.

- Find the **input_run_<#>_forpreview.json** in **run_<#>/json_output/**
![image](https://hackmd.io/_uploads/SJnRGw2ST.png)
- Copy the content
- Open the MCX cloud website: https://mcx.space/cloud/# and click the JSON bottom. ![image](https://hackmd.io/_uploads/rJWomDnB6.png)
- Paste your content here ![image](https://hackmd.io/_uploads/BydGNDhHT.png)
- Change to Preview and have fun! ![image](https://hackmd.io/_uploads/rytjVP2rT.png)

## Analyze the output file from MCX
Please look at [utils.py](https://github.com/ShawnSun1031/IJV-Project/blob/main/mcx_sim/utils.py) to get the comprehension about how to analyze the output file from MCX such as pathlength, scattering count, diffuse reflectance and so on.


## TODO
- [ ] 1. Write an example code for how to use [utils.py](https://github.com/ShawnSun1031/IJV-Project/blob/main/mcx_sim/utils.py)  
- [ ] 2. To apply different NA on different SDS.  
https://github.com/ShawnSun1031/IJV-Project/blob/main/mcx_sim/S3_run_sim.py#L146  
https://github.com/ShawnSun1031/IJV-Project/blob/main/mcx_sim/mcx_ultrasound_opsbased.py#L419
- [x] 3. Create functions to access the MCX simulation results.  
Function list (reference as ma):  
https://github.com/fangq/mcx/blob/master/utils/mcxmeanpath.m  
https://github.com/fangq/mcx/blob/master/utils/mcxmeanscat.m



###### tags: `MCX` `Documentation`
