from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.interpolate import PchipInterpolator


def get_angelinvcdf_from_pdf(hardware_path: str):
    '''
    input: path of pdf file
    output: angelinvcdf, a 2-column numpy array, first column is angle (0~89), second column is cdf value (0~1)
    '''
    hardware_parameters = yaml.safe_load(open(hardware_path))
    led_profile_in_3d_filename = Path(hardware_parameters['hardware']['source']['led']['led_profile_in_3d_filename']).name
    led_profile_in_3d = np.genfromtxt(
        led_profile_in_3d_filename, delimiter=",", skip_header=1)

    angle = led_profile_in_3d[:, 0]
    pdf = np.cumsum(led_profile_in_3d[:, 1])
    inversecdf_func = PchipInterpolator(pdf, angle)
    sampling_seeds = np.linspace(0, 1, num=int(float(
        hardware_parameters["hardware"]["source"]["led"]["sampling_num_radiation_pattern"]))
    )
    sampling_angles = inversecdf_func(sampling_seeds)

    angelinvcdf = (np.deg2rad(sampling_angles) / np.pi).tolist()

    angleinvcdf_filename = Path(hardware_parameters['hardware']['source']['led']['angleinvcdf_filename']).name
    df = pd.DataFrame({
        'probability': sampling_seeds,
        'angleinvcdf': angelinvcdf
    })
    df.to_csv(angleinvcdf_filename, index=False)

if __name__ == "__main__":
    hardware_path = "../hardware_parameter.yaml"
    get_angelinvcdf_from_pdf(hardware_path)
