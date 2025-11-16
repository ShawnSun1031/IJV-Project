"""MCX simulation module using pmcx library.

This module provides a modern interface to Monte Carlo photon transport simulation
using the pmcx Python library, replacing the deprecated binary-based approach.

Key Features:
- MCXRunner: Main simulation runner with pmcx integration
- White Monte Carlo (WMC): Run simulations with mua=0, apply mua in post-processing
- CV-based stopping criterion for WMC
- Proper weight recalculation using photon trajectories
- Parameter generation for train/test splits
- Automated simulation directory setup
"""

from pathlib import Path

from ijv_project.mcx_simulation.mcx_runner import MCXRunner, SimulationResult

__all__ = [
    # Core simulation
    "MCXRunner",
    "SimulationResult",
]


# Constant Variables for Configuration Files and Directories
CONFIG_PATH = Path(__file__).parent / "config"
IJV_LARGE_OPTICAL_SETTING_FILE = CONFIG_PATH / "ijv_large_optical_setting.yaml"
IJV_SMALL_OPTICAL_SETTING_FILE = CONFIG_PATH / "ijv_small_optical_setting.yaml"
HARDWARE_PARAMETER_FILE = CONFIG_PATH / "hardware_parameter.yaml"
MCXLAB_SETTING_FILE_TEMPLATE = CONFIG_PATH / "mcxlab_setting_template.yaml"
ANGLE_INVCDF_FILE = CONFIG_PATH / "led_source" / "angleinvcdf.csv"
MCX_OUTPUT_DIRNAME = Path(__file__).parent / "mcx_output"
ULTRASOUND_VOLUME_DIRNAME = Path(__file__).parent / "ultrasound_data"


MCXLAB_SETTING_FILE = "mcxlab_setting.yaml"
IJV_SDS_DETID_MAP_FILE = "ijv_sds_detid_map.json"
