<!-- # Welcome to IJV-Project

For full documentation visit [mkdocs.org](https://www.mkdocs.org).

## Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files. -->

# Welcome to IJV-Project
The primary objective of this study is to quantitatively measure changes in internal jugular vein oxygen saturation non-invasively using near-infrared spectroscopy. Initially, a surrogate model based on neural networks is employed to accelerate the Monte Carlo method which is traditionally used to simulate photon transport in tissue. Subsequently, another neural network is applied to establish a predictive model for oxygen saturation changes. The input to this model consists of spectral features extracted using formulas same as modified Beer-Lambert law, while the output represents oxygen saturation changes.  

As for the measurement system, the study utilizes 20 wavelength points based on the absorption spectra of blood, within the wavelength range of 700 nm to 850 nm. A dual-channel system is set up, with the short channel having a distance of 10 mm between the light source and detector, and the long channel having a distance of 20 mm. This design effectively minimizes the impact of superficial tissues and enhances the signal from deeper tissues including the internal jugular vein area. During simulation, a three-dimensional numerical model is constructed based on ultrasound images of each subject’s neck, ensuring
that simulation results closely resemble reality, thus providing more accurate simulated data.  

To evaluate the prediction model’s performance, the study investigates the impacts of factors such as human respiration, changes in oxygen levels in surrounding tissues, and measurement noise on the predictive model. The results indicate that the effects of respiration may lead to a maximum increase of 3% to 4% in root-mean-square error (RMSE). Changes in oxygen levels in surrounding tissues have a less significant impact, with a maximum RMSE increase of only 1%. Measurement signal errors can cause an RMSE increase of 1% to 2%.  

For model generalization, the study conducts simulated experiments using transfer learning. Through experimentation, it is observed that by using a thousandth of the original dataset and employing transfer learning, an RMSE of 3.5% can be achieved, while without transfer learning and using only a thousandth of the dataset, an RMSE of 7% is obtained.  

Based on the simulation results, the prediction model established in this study predicts changes in internal jugular vein oxygen saturation with an RMSE of less than 1.5%. In vivo experiments involve measuring diffuse reflectance spectra from living subjects, extracting spectral features using the formulas designed in this study, and inputting them into the prediction model after appropriate normalization. The prediction results are consistent with expected physiological response and spectral features in the measured data.  
>  &mdash; <cite>[Chin-Hsuan Sun][1]</cite>  

## Publication
![Publication Image](/publication1.png)  
Quantifying changes in oxygen saturation of the internal jugular vein in vivo using deep neural networks and subject-specific three-dimensional Monte Carlo models
Published in Optics Letters Vol. 49, Issue 10, 2024

Central venous oxygen saturation (ScvO2) is an important parameter for assessing global oxygen usage and guiding clinical interventions. However, measuring ScvO2 requires invasive catheterization. As an alternative, we aim to noninvasively and continuously measure changes in oxygen saturation of the internal jugular vein (SijvO2) by a multi-channel near-infrared spectroscopy system. The relation between the measured reflectance and changes in SijvO2 is modeled by Monte Carlo simulations and used to build a prediction model using deep neural networks (DNNs). The prediction model is tested with simulated data to show robustness to individual variations in tissue optical properties. The proposed technique is promising to provide a noninvasive tool for monitoring the stability of brain oxygenation in broad patient populations.

Recommended citation: Chin-Hsuan Sun, Hao-Wei Lee, Ya-Hua Tsai, Jia-Rong Luo & Kung-Bin Sung (2024). Quantifying changes in oxygen saturation of the internal jugular vein in vivo using deep neural networks and subject-specific three-dimensional Monte Carlo models. Optics Letters. 49(10). [https://doi.org/10.1364/OL.517960](https://doi.org/10.1364/OL.517960)

