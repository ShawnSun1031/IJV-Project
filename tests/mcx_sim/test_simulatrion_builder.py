# mypy: ignore-errors
from pathlib import Path

import numpy as np
import pytest

from ijv_project.mcx_simulation import IJV_LARGE_OPTICAL_SETTING_FILE
from ijv_project.mcx_simulation.simulation_builder import SimulationBuilder


@pytest.fixture
def volume_path(temp_test_dir: Path) -> Path:
    vol = np.zeros((10, 10, 10), dtype=np.uint8)
    vol[2:5, 2:5, 2:5] = 1
    vol_path = temp_test_dir / "test_volume.npy"
    np.save(vol_path, vol)
    return vol_path


def test_simulation_builder(volume_path):
    sim_builder = SimulationBuilder(
        subject_id="example_subject_1",
        volume_path=volume_path,
    )

    sim_builder.create_simulation_metadata(optical_setting_file=IJV_LARGE_OPTICAL_SETTING_FILE)
