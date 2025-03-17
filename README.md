Internal-Jugular-Vein Project
===
-   Author: [Chin-Hsuan Sun](https://shawnsun1031.github.io/)
-   License: MIT License
-   Update Date: 2023/12/13
-   Download Size: 128 MB
-   Github Link: [https://github.com/ShawnSun1031/IJV-Project](https://github.com/ShawnSun1031/IJV-Project)
-   Contact :email:: dicky10311111@gmail.com 
-   IJV Web Site Link: [https://shawnsun1031.github.io/IJV-Project/](https://shawnsun1031.github.io/IJV-Project/)

> [!NOTE] 
> This is the description of the IJV project, which aims to ensure code behavior consistency. Please ensure that your environment aligns with the following specifications.

![Static Badge](https://img.shields.io/badge/python-v3.8.0-blue)
![Static Badge](https://img.shields.io/badge/pip-v20.2.0_(python3.8)-orange)
![Static Badge](https://img.shields.io/badge/cuda-v11.7.0-green)
![Static Badge](https://img.shields.io/badge/OS-ubuntu_18.04-purple)



## Table of Contents
- [Introduction](#Introduction)
- [Installation](#Installation)
- [Project Flows](#Project-Flows)
    - [Simulation](#Simulation)
    - [*In-vivo*](#In-vivo)
- [Desciprtion of Each Folder](#Desciprtion-of-Each-Folder)
- [Reference](#Reference)

## Introduction
> &nbsp;&nbsp;&nbsp;The primary objective of this study is to quantitatively measure changes in internal jugular vein oxygen saturation non-invasively using near-infrared spectroscopy. Initially, a surrogate model based on neural networks is employed to accelerate the Monte Carlo method which is traditionally used to simulate photon transport in tissue. Subsequently, another neural network is applied to establish a predictive model for oxygen saturation changes. The input to this model consists of spectral features extracted using formulas same as modified Beer-Lambert law, while the output represents oxygen saturation changes.  
> &nbsp;&nbsp;&nbsp;As for the measurement system, the study utilizes 20 wavelength points based on the absorption spectra of blood, within the wavelength range of 700 nm to 850 nm. A dual-channel system is set up, with the short channel having a distance of 10 mm between the light source and detector, and the long channel having a distance of 20 mm. This design effectively minimizes the impact of superficial tissues and enhances the signal from deeper tissues including the internal jugular vein area. During simulation, a three-dimensional numerical model is constructed based on ultrasound images of each subject’s neck, ensuring
that simulation results closely resemble reality, thus providing more accurate simulated data.  
> &nbsp;&nbsp;&nbsp;To evaluate the prediction model’s performance, the study investigates the impacts of factors such as human respiration, changes in oxygen levels in surrounding tissues, and measurement noise on the predictive model. The results indicate that the effects of respiration may lead to a maximum increase of 3% to 4% in root-mean-square error (RMSE). Changes in oxygen levels in surrounding tissues have a less significant impact, with a maximum RMSE increase of only 1%. Measurement signal errors can cause an RMSE increase of 1% to 2%.  
> &nbsp;&nbsp;&nbsp;For model generalization, the study conducts simulated experiments using transfer learning. Through experimentation, it is observed that by using a thousandth of the original dataset and employing transfer learning, an RMSE of 3.5% can be achieved, while without transfer learning and using only a thousandth of the dataset, an RMSE of 7% is obtained.  
> &nbsp;&nbsp;&nbsp;Based on the simulation results, the prediction model established in this study predicts changes in internal jugular vein oxygen saturation with an RMSE of less than 1.5%. In vivo experiments involve measuring diffuse reflectance spectra from living subjects, extracting spectral features using the formulas designed in this study, and inputting them into the prediction model after appropriate normalization. The prediction results are consistent with expected physiological response and spectral features in the measured data.  
>  &mdash; <cite>[Chin-Hsuan Sun][1]</cite>  

[1]: https://shawnsun1031.github.io/

## Installation
> [!TIP]
> Suggestion: create a ${\rm\color{red}{virtual \space environment}}$ and activate it.  
> **How to creaete a virtual environment?**  
> For **Anaconda** user, Read [**this document**](https://hackmd.io/@aMXX54b3ToSm3kTNB_LuWQ/BJ_No2Rkp)
> From 2025, I highly recommand  you to use [uv](https://docs.astral.sh/uv/) to manage your python package

> [!IMPORTANT]
> 1. make sure your local computer has ${\rm\color{red}{cuda \space toolkit}}$
> 2. ${\rm\color{red}{recompile}}$ the MCX source code at [MD703_edit_MCX_src_v2023/src](https://github.com/ShawnSun1031/IJV-Project/tree/main/MD703_edit_MCX_src_v2023/src)
> 3. Install the dependencies: `pip install -r requirements.txt`
> 4. Install [cupy](https://docs.cupy.dev/en/latest/install.html) package


## Project Flows
### Simulation
1. Building Numerical Model of IJV by Ultrasound Image
2. MCX (Monte Carlo) simulation
3. Surrogate Model (To accerlerate the MC simulation)
    > To understand the concept, read this paper: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5905904/
5. Prediction Model 
### *In-vivo*
1. In-vivo experiment to validate simulation (ex: hyperventilation, valsalva maneuver, etc.)
2. Preprocess raw data
3. Calibration (remove system response)
4. Feed processed data into prediction data

## Desciprtion of Each Folder
* MCX_src_modified_by_MD703
    * We modified the source code of MCX (https://github.com/fangq/mcx). Please see [**this file**](https://hackmd.io/@73X8klpNRmSsdgJzudHbgA/SyeF6nI9P#20210409---mcx_corecu-%E4%BF%AE%E6%94%B9) to check what we modified if you're intereseted in. (adjust the source pattern)  
* absoprtion_spectrum_by_substance
    * The diffuse reflectance spectra is generated by the chromophore in the tissue.
* find_OPs_boundary
    * Based on multiple literature, finding the possible boundary of each optical parameters.
* mcx_sim
    * Run Monte Carlo simulation based on the open source **MCX** we modified
* ultrasound_image_processing_parallel
    * Constuct the numerical model of IJV by ultrasound image.
* surrogate_model
    * Build the surrogate model to replace traditional MC simulation.


## Reference
* To understand more detail, basically this repository is followed by my master thesis. Please check NAS:Data/BOSI Lab/Thesis/R10 to access the full text version.

