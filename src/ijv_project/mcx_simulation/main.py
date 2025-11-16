""" """

import enum
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer

from ijv_project import logger
from ijv_project.mcx_simulation import (
    IJV_LARGE_OPTICAL_SETTING_FILE,
    IJV_SDS_DETID_MAP_FILE,
    IJV_SMALL_OPTICAL_SETTING_FILE,
    ULTRASOUND_VOLUME_DIRNAME,
)
from ijv_project.mcx_simulation.mcx_runner import MCXRunner
from ijv_project.mcx_simulation.schema.mcxlab import MCXConfig
from ijv_project.mcx_simulation.simulation_builder import SimulationBuilder


class IJVType(str, enum.Enum):
    IJV_LARGE = "ijv_large"
    IJV_SMALL = "ijv_small"


class DatasetType(str, enum.Enum):
    TRAIN = "train"
    VAL = "val"
    TEST = "test"


@dataclass
class DefaultSettings:
    dataset_type: DatasetType = DatasetType.TRAIN
    subject_id: str = "example_subject_1"
    ijv_type: IJVType = IJVType.IJV_LARGE
    ultrasound_volume_file: Path = ULTRASOUND_VOLUME_DIRNAME / "HW_20230903_merge_vol.npy"
    mcx_run_start: int = 1
    mcx_run_end: int = 10
    na: float | None = 0.37
    n_iterations: int = 3
    cv_threshold: float | None = 2.5


def main(
    dataset_type: Annotated[
        DatasetType, typer.Argument(help="Dataset type")
    ] = DefaultSettings.dataset_type,
    subject_id: Annotated[
        str, typer.Argument(help="ID of the subject")
    ] = DefaultSettings.subject_id,
    ijv_type: Annotated[IJVType, typer.Argument(help="IJV type")] = DefaultSettings.ijv_type,
    ultrasound_volume_file: Annotated[
        Path, typer.Option(help="Path to the ultrasound volume file")
    ] = DefaultSettings.ultrasound_volume_file,
    mcx_run_start: Annotated[
        int, typer.Option(help="Starting run index")
    ] = DefaultSettings.mcx_run_start,
    mcx_run_end: Annotated[
        int, typer.Option(help="Ending run index")
    ] = DefaultSettings.mcx_run_end,
    na: Annotated[float | None, typer.Option(help="Numerical Aperture value")] = DefaultSettings.na,
    n_iterations: Annotated[
        int,
        typer.Option(
            help="Number of iterations for the simulation, if `cv_threshold` is specified cv calculation will perform each `n_iterations`."
        ),
    ] = DefaultSettings.n_iterations,
    cv_threshold: Annotated[
        float | None, typer.Option(help="Coefficient of Variation threshold(%)")
    ] = DefaultSettings.cv_threshold,
) -> None:
    """Main function demonstrating the complete simulation preparation workflow.

    This function orchestrates the entire workflow for preparing MCX simulations,
    including directory creation, parameter generation, and metadata handling.
    """
    # Configure logging
    logger.info("Starting MCX Simulation Preparation Workflow")

    # ==========================
    # Workflow Steps
    # ==========================
    # ==========================
    # Step 1: Build Simulation Files
    # ==========================
    sim_builder = SimulationBuilder(
        subject_id=subject_id,
        volume_path=ultrasound_volume_file,
    )
    # Create metadata
    sim_builder.create_simulation_metadata(
        optical_setting_file=IJV_LARGE_OPTICAL_SETTING_FILE
        if ijv_type == IJVType.IJV_LARGE
        else IJV_SMALL_OPTICAL_SETTING_FILE
    )

    # Generate optical parameters
    sim_builder.generate_optical_parameters(
        op_case_name=ijv_type,
        optical_setting_file=IJV_LARGE_OPTICAL_SETTING_FILE
        if ijv_type == IJVType.IJV_LARGE
        else IJV_SMALL_OPTICAL_SETTING_FILE,
    )

    # Create simulation files and directories
    sim_builder.create_simulation_directories(
        op_case_name=ijv_type,
        optical_setting_file=IJV_LARGE_OPTICAL_SETTING_FILE
        if ijv_type == IJVType.IJV_LARGE
        else IJV_SMALL_OPTICAL_SETTING_FILE,
    )

    # ==========================
    # Step 2: Run MCX simulations
    # ==========================
    # TODO: add na logic in MCXRunner
    if sim_builder.unique_output_dir is None:
        raise ValueError("Simulation output directory is not set.")

    for i in range(mcx_run_start, mcx_run_end + 1):
        sim_dir = sim_builder.unique_output_dir / ijv_type / dataset_type / f"sim_{i:04d}"
        config = MCXConfig.from_yaml(sim_dir / "mcxlab_setting.yaml")
        sds_detid_map = json.load(
            open(sim_builder.unique_output_dir / "metadata" / IJV_SDS_DETID_MAP_FILE)
        )
        runner = MCXRunner(config, sds_detid_map, save_dir=sim_dir)
        runner.run(
            n_iterations=n_iterations,
            cv_threshold=cv_threshold,
        )

    # ==========================
    # Step 3: Apply WMC post-processing
    # ==========================
    raise NotImplementedError("WMC post-processing is not implemented yet.")


if __name__ == "__main__":
    typer.run(main)
