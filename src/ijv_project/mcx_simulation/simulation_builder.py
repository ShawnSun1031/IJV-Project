import hashlib
import json
from pathlib import Path
from typing import Annotated, Literal, TypeVar

import numpy as np
import numpy.typing as npt
import pandas as pd
import yaml
from loguru import logger
from pydantic import BaseModel, Field, field_validator

from ijv_project.mcx_simulation import (
    ANGLE_INVCDF_FILE,
    CONFIG_PATH,
    HARDWARE_PARAMETER_FILE,
    IJV_LARGE_OPTICAL_SETTING_FILE,
    IJV_SDS_DETID_MAP_FILE,
    MCX_OUTPUT_DIRNAME,
    MCXLAB_SETTING_FILE,
    MCXLAB_SETTING_FILE_TEMPLATE,
    ULTRASOUND_VOLUME_DIRNAME,
)
from ijv_project.mcx_simulation.schema.hardware_parameter import HardwareParameterSchema
from ijv_project.mcx_simulation.schema.mcxlab import MCXConfig
from ijv_project.mcx_simulation.schema.optical_setting import OpticalSettingSchema

DType = TypeVar("DType", bound=np.generic)

ArrayN = Annotated[npt.NDArray[DType], Literal["N"]]


class SimulationRelatedFiles(BaseModel):
    angleinvcdf: Path = Field(
        ..., description="Path to the angle CDF file for user-specified launch angle distribution"
    )
    hardware_parameter: Path = Field(..., description="Path to the hardware parameter file")
    volume: Path = Field(..., description="Path to the volume file (e.g., .npy)")
    mcxlab_setting: Path = Field(..., description="Path to the MCXLab setting YAML file")
    optical_settings: Path = Field(..., description="Path to the optical settings YAML file")

    @field_validator(
        "angleinvcdf", "hardware_parameter", "volume", "mcxlab_setting", "optical_settings"
    )
    @classmethod
    def validate_file_exists(cls, v: Path) -> Path:
        """Validate that the file exists."""
        if not v.exists():
            raise FileNotFoundError(f"File not found: {v}")
        return v


class LoadedSimulationConfig(BaseModel):
    """Container for all loaded and validated simulation configurations."""

    model_config = {"arbitrary_types_allowed": True}

    mcx_config: MCXConfig = Field(..., description="Loaded MCXLab configuration")
    hardware_config: HardwareParameterSchema = Field(
        ..., description="Loaded hardware configuration"
    )
    optical_config: OpticalSettingSchema = Field(..., description="Loaded optical settings")
    volume_data: np.ndarray = Field(..., description="Loaded volume data")
    angleinvcdf_data: np.ndarray = Field(..., description="Loaded angle CDF data")
    config_hash: str = Field(..., description="MD5 hash of all configuration files")


def calculate_simulation_hash(simulation_files: SimulationRelatedFiles) -> str:
    """
    Calculate MD5 hash of all simulation-related files for creating unique output directory.

    This ensures that simulations with different configurations get different output directories,
    enabling caching and preventing accidental overwrites.

    Args:
        simulation_files: SimulationRelatedFiles instance with paths to all config files

    Returns:
        MD5 hash string (first 8 characters)
    """
    logger.info("Calculating configuration hash...")

    hasher = hashlib.md5()

    # Hash each file in a consistent order
    file_paths = [
        simulation_files.mcxlab_setting,
        simulation_files.hardware_parameter,
        simulation_files.optical_settings,
        simulation_files.angleinvcdf,
        simulation_files.volume,
    ]

    for file_path in file_paths:
        logger.debug(f"Hashing file: {file_path}")

        # Read file content and update hash
        with open(file_path, "rb") as f:
            # Read in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)

    # Get first 8 characters of hash for shorter directory names
    full_hash = hasher.hexdigest()
    short_hash = full_hash[:8]

    logger.info(f"Configuration hash: {short_hash} (full: {full_hash})")
    return short_hash


def load_and_validate_configs(simulation_files: SimulationRelatedFiles) -> LoadedSimulationConfig:
    """
    Load and validate all simulation configuration files.

    This function:
    1. Validates that all files exist
    2. Loads each configuration using appropriate schema
    3. Validates configuration values using Pydantic
    4. Calculates a hash for the entire configuration

    Args:
        simulation_files: SimulationRelatedFiles instance with paths to all config files

    Returns:
        LoadedSimulationConfig with all loaded configurations and hash

    Raises:
        FileNotFoundError: If any required file doesn't exist
        ValueError: If any configuration is invalid
        Exception: For other loading errors
    """
    logger.info("=" * 80)
    logger.info("LOADING AND VALIDATING SIMULATION CONFIGURATIONS")
    logger.info("=" * 80)

    try:
        # 1. Load MCXLab configuration
        logger.info(f"Loading MCXLab config from: {simulation_files.mcxlab_setting}")
        mcx_config = MCXConfig.from_yaml(simulation_files.mcxlab_setting)
        logger.success(f"✓ MCXLab config loaded: {mcx_config.nphoton:,} photons")

        # 2. Load hardware parameters
        logger.info(f"Loading hardware config from: {simulation_files.hardware_parameter}")
        with open(simulation_files.hardware_parameter) as f:
            hardware_data = yaml.safe_load(f)
        hardware_config = HardwareParameterSchema(**hardware_data)
        logger.success(
            f"✓ Hardware config loaded: voxel_size={hardware_config.hardware.voxel_size}mm"
        )

        # 3. Load optical settings
        logger.info(f"Loading optical config from: {simulation_files.optical_settings}")
        with open(simulation_files.optical_settings) as f:
            optical_data = yaml.safe_load(f)
        optical_config = OpticalSettingSchema(**optical_data)
        num_tissues = len(optical_config.tissues.get_tissue_names())
        logger.success(f"✓ Optical config loaded: {num_tissues} tissue types configured")

        # 4. Load volume data
        logger.info(f"Loading volume from: {simulation_files.volume}")
        volume_data = np.load(simulation_files.volume)
        logger.success(f"✓ Volume loaded: shape={volume_data.shape}, dtype={volume_data.dtype}")

        # 5. Load angle CDF data
        logger.info(f"Loading angleinvcdf from: {simulation_files.angleinvcdf}")
        # Check file extension to determine loading method
        angleinvcdf_data = (
            pd.read_csv(simulation_files.angleinvcdf, header=None).to_numpy().flatten()
        )
        logger.success(f"✓ Angle CDF loaded: shape={angleinvcdf_data.shape}")

        # 6. Calculate configuration hash
        config_hash = calculate_simulation_hash(simulation_files)

        logger.info("=" * 80)
        logger.success("ALL CONFIGURATIONS LOADED AND VALIDATED SUCCESSFULLY!")
        logger.info("=" * 80)

        return LoadedSimulationConfig(
            mcx_config=mcx_config,
            hardware_config=hardware_config,
            optical_config=optical_config,
            volume_data=volume_data,
            angleinvcdf_data=angleinvcdf_data,
            config_hash=config_hash,
        )

    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        raise
    except ValueError as e:
        logger.error(f"Invalid configuration: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading configurations: {e}")
        raise


class SimulationBuilder:
    def __init__(
        self,
        subject_id: str,
        volume_path: Path,
        config_path: Path = CONFIG_PATH,
        output_dir: Path = MCX_OUTPUT_DIRNAME,
    ) -> None:
        self.subject_id = subject_id
        self.volume_path = volume_path
        self.config_path = config_path
        self.output_dir = output_dir

        self.unique_output_dir: Path | None = None
        self.loaded_configs: LoadedSimulationConfig | None = None

        self.optical_settings: OpticalSettingSchema | None = None
        self.mus_dataset: dict[str, np.ndarray] | None = None
        self.mua_dataset: dict[str, np.ndarray] | None = None

    def create_simulation_metadata(
        self,
        optical_setting_file: Path,
    ) -> tuple[Path, LoadedSimulationConfig]:
        """
        Create simulation directory structure with unique hash-based naming.

        Args:
            subject_id: Subject identifier
            config_path: Path to directory containing configuration files
            volume_path: Path to volume .npy file
            output_dir: Base output directory (default: ./mcx_output)

        Returns:
            Tuple of (unique_output_dir, loaded_configs)

        Raises:
            FileNotFoundError: If any required file doesn't exist
            ValueError: If any configuration is invalid
        """
        logger.info("=" * 80)
        logger.info("CREATING SIMULATION DIRECTORY STRUCTURE")
        logger.info("=" * 80)
        logger.info(f"Subject ID: {self.subject_id}")
        logger.info(f"Config path: {self.config_path}")
        logger.info(f"Volume path: {self.volume_path}")
        logger.info(f"Base output dir: {self.output_dir}")

        # 1. Create SimulationRelatedFiles instance and validate existence
        simulation_files = SimulationRelatedFiles(
            angleinvcdf=ANGLE_INVCDF_FILE,
            hardware_parameter=HARDWARE_PARAMETER_FILE,
            volume=self.volume_path,
            mcxlab_setting=MCXLAB_SETTING_FILE_TEMPLATE,
            optical_settings=optical_setting_file,
        )
        logger.success("✓ All required files exist")

        # 2. Load and validate all configurations
        self.loaded_configs = load_and_validate_configs(simulation_files)

        # 3. Create unique output directory with hash
        unique_dir_name = f"{self.subject_id}_{self.loaded_configs.config_hash}"
        self.unique_output_dir = self.output_dir / unique_dir_name

        logger.info(f"\nCreating unique output directory: {self.unique_output_dir}")

        # Check if directory already exists (simulation may have been run before)
        if self.unique_output_dir.exists():
            logger.warning(f"Output directory already exists: {self.unique_output_dir}")
            logger.warning(
                "This may indicate the simulation was already run with these exact parameters"
            )
            logger.info("Continuing anyway - outputs may be overwritten")
        else:
            self.unique_output_dir.mkdir(parents=True, exist_ok=True)
            logger.success(f"✓ Created output directory: {self.unique_output_dir}")

        # 4. Create metadata directory
        metadata_dir = self.unique_output_dir / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        logger.success(f"✓ Created metadata directory: {metadata_dir}")

        # 5. Copy metadata files to metadata directory
        for file_attr, file_path in simulation_files.model_dump().items():
            dest_path = metadata_dir / file_path.name
            with open(file_path, "rb") as src_file, open(dest_path, "wb") as dest_file:
                dest_file.write(src_file.read())
            logger.success(f"✓ Copied {file_attr} to metadata directory: {dest_path}")

        # 6. pre-build detpos to save the `ijv_sds_detid_map.json` file
        self._get_detpos(save_map_path=metadata_dir / IJV_SDS_DETID_MAP_FILE)

        logger.info("=" * 80)
        logger.success("SIMULATION DIRECTORY SETUP COMPLETE!")
        logger.info("=" * 80)
        logger.info(f"Output directory: {self.unique_output_dir}")
        logger.info(f"Metadata saved to: {metadata_dir}")

        return self.unique_output_dir, self.loaded_configs

    def generate_optical_parameters(
        self,
        op_case_name: Literal["ijv_large", "ijv_small"] | str,
        optical_setting_file: Path,
        save_path: Path | None = None,
    ) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
        logger.info("Generating optical parameters...")
        self.optical_settings = OpticalSettingSchema.from_yaml(optical_setting_file)

        logger.info("Dataset split:")
        logger.info(f"  Val:   {self.optical_settings.dataset.val:.1%}")
        logger.info(f"  Test:  {self.optical_settings.dataset.test:.1%}")

        self.mus_dataset = self.optical_settings.mus_dataset
        self.mua_dataset = self.optical_settings.mua_dataset
        logger.info(
            f"  Mus train/val/test: {self.mus_dataset['train'].shape[0]}/"
            f"{self.mus_dataset['val'].shape[0]}/{self.mus_dataset['test'].shape[0]}"
        )
        logger.info(
            f"  Mua train/val/test: {self.mua_dataset['train'].shape[0]}/"
            f"{self.mua_dataset['val'].shape[0]}/{self.mua_dataset['test'].shape[0]}"
        )
        logger.info("=" * 80)
        # save datasets to CSV for inspection
        if self.unique_output_dir is None:
            raise ValueError(
                "Unique output directory not set. Please run create_simulation_metadata() first."
            )

        if save_path is None:
            save_path = self.unique_output_dir / op_case_name / "optical_parameters"

        save_path.mkdir(parents=True, exist_ok=True)
        mus_columns = [
            f"mus_{tissue_name}" for tissue_name in self.optical_settings.tissues.get_tissue_names()
        ]
        mua_columns = [
            f"mua_{tissue_name}" for tissue_name in self.optical_settings.tissues.get_tissue_names()
        ]
        for dataset_type in ["train", "val", "test"]:
            pd.DataFrame(self.mus_dataset[dataset_type], columns=mus_columns).to_csv(
                save_path / f"mus_{dataset_type}.csv", index=False
            )
            pd.DataFrame(self.mua_dataset[dataset_type], columns=mua_columns).to_csv(
                save_path / f"mua_{dataset_type}.csv", index=False
            )
        logger.success(f"\nGenerated datasets saved to: {save_path}")

        return self.mus_dataset, self.mua_dataset

    def _get_mcx_optical_parameters(
        self,
        mus_values: ArrayN[np.floating],
        mua_values: ArrayN[np.floating],
    ) -> list[dict[str, float]]:
        """Get MCX optical parameters dictionary from mus and mua values arrays."""
        if self.optical_settings is None:
            raise ValueError(
                "Optical settings not loaded. Please run generate_optical_parameters() first."
            )

        tissue_names = self.optical_settings.tissues.get_tissue_names()
        if len(mus_values) != len(tissue_names) or len(mua_values) != len(tissue_names):
            raise ValueError(
                "Length of mus/mua values does not match number of tissues in optical settings."
            )

        optical_params: list[dict[str, float]] = []  # list of optical_param_dict
        for i, tissue_name in enumerate(tissue_names):
            # we already ensure the order of mus/mua matches tissue order in optical settings
            optical_params.append(
                {
                    "mus": float(mus_values[i]),
                    "mua": float(mua_values[i]),
                    "g": float(self.optical_settings.tissues.get_tissue(tissue_name).g),
                    "n": float(self.optical_settings.tissues.get_tissue(tissue_name).n),
                }
            )

        return optical_params

    def _get_srcpos(self) -> list[float]:
        """Get source position from loaded hardware configuration."""
        if self.loaded_configs is None:
            raise ValueError(
                "Loaded configurations not available. Please run create_simulation_metadata() first."
            )

        # Put the source at the center of the transducer face
        vol = np.load(self.volume_path)
        dim_x, dim_y, _ = vol.shape
        src_x = dim_x // 2  # Center in x
        src_y = dim_y // 2  # Center in y
        src_z = self._mm_to_voxel(
            self.loaded_configs.hardware_config.hardware.detector.holder.z_size - 1e-4
        )  # Just above the holder
        return [src_x, src_y, src_z]

    def _mm_to_voxel(self, length_mm: float) -> float:
        """Convert length in mm to voxel units based on hardware voxel size."""
        if self.loaded_configs is None:
            raise ValueError(
                "Loaded configurations not available. Please run create_simulation_metadata() first."
            )
        voxel_size = self.loaded_configs.hardware_config.hardware.voxel_size  # in mm
        return length_mm / voxel_size

    def _get_detpos(self, save_map_path: Path | None = None) -> list[dict[str, float]]:
        """Get detector positions from loaded hardware configuration."""
        if self.loaded_configs is None:
            raise ValueError(
                "Loaded configurations not available. Please run create_simulation_metadata() first."
            )
        # Placeholder implementation - replace with actual logic based on hardware config
        src_x, src_y, _ = self._get_srcpos()
        det_z = self._mm_to_voxel(
            self.loaded_configs.hardware_config.hardware.detector.holder.z_size
            - self.loaded_configs.hardware_config.hardware.detector.prism.z_size
        )
        detectors = []
        sds_detid_map = {}
        det_id = 1
        for fiber in self.loaded_configs.hardware_config.hardware.detector.fibers:
            sds = self._mm_to_voxel(fiber.sds)
            radius = self._mm_to_voxel(fiber.radius)
            sds_det_id_list = []

            # right - bottom
            detectors.append(
                {
                    "x": src_x + sds,
                    "y": src_y - 2 * radius,
                    "z": det_z,
                    "radius": radius,
                }
            )
            sds_det_id_list.append(det_id)
            det_id += 1

            # left - bottom
            detectors.append(
                {
                    "x": src_x - sds,
                    "y": src_y - 2 * radius,
                    "z": det_z,
                    "radius": radius,
                },
            )
            sds_det_id_list.append(det_id)
            det_id += 1

            # right - middle
            detectors.append({"x": src_x + sds, "y": src_y, "z": det_z, "radius": radius})
            sds_det_id_list.append(det_id)
            det_id += 1

            # left - middle
            detectors.append({"x": src_x - sds, "y": src_y, "z": det_z, "radius": radius})
            sds_det_id_list.append(det_id)
            det_id += 1

            # right - top
            detectors.append(
                {
                    "x": src_x + sds,
                    "y": src_y + 2 * radius,
                    "z": det_z,
                    "radius": radius,
                }
            )
            sds_det_id_list.append(det_id)
            det_id += 1

            # left - top
            detectors.append(
                {
                    "x": src_x - sds,
                    "y": src_y + 2 * radius,
                    "z": det_z,
                    "radius": radius,
                }
            )
            sds_det_id_list.append(det_id)
            det_id += 1

            sds_detid_map[f"{fiber.sds:.1f}"] = sds_det_id_list

        # Save sds_detid_map to json
        if save_map_path is not None:
            with open(save_map_path, "w") as f:
                json.dump(sds_detid_map, f, indent=4)

        return detectors

    def create_simulation_directories(
        self,
        op_case_name: Literal["ijv_large", "ijv_small"] | str,
        optical_setting_file: Path,
    ):
        """Create necessary directories for MCX simulations and WMC post-processing.

        1. create train/val/test directories for MCX simulations for each, create subdirectories
            based on the number of mus combination defined in optical_parameters folder
           (e.g. train/mus_0001, train/mus_0002, ..., val/mus_0001, etc.)
        2. copy metadata/mcxlab_setting.template.yaml to each subdirectory and rename to mcxlab_setting.yaml
        3. replace the setting in mcxlab_setting.yaml for each subdirectory based on
            3.1 the mus/mua combination
            3.2 the hardware parameters defined in hardware_parameter.yaml
            3.3 the volume file path
            3.4 the angleinvcdf file path

        Raises:
            ValueError: If unique output directory is not set.
        """

        logger.info("Creating simulation directories...")
        if self.unique_output_dir is None:
            raise ValueError(
                "Unique output directory not set. Please run create_simulation_metadata() first."
            )

        if self.loaded_configs is None:
            raise ValueError(
                "Loaded configurations not available. Please run create_simulation_metadata() first."
            )

        if self.mus_dataset is None or self.mua_dataset is None:
            self.mus_dataset, _ = self.generate_optical_parameters(
                op_case_name, optical_setting_file
            )
            self.optical_settings = OpticalSettingSchema.from_yaml(optical_setting_file)

        base_dirs = ["train", "val", "test"]
        for base_dir in base_dirs:
            mus_data = self.mus_dataset[base_dir]
            num_combinations = mus_data.shape[0]
            for i in range(num_combinations):
                sim_dir = self.unique_output_dir / op_case_name / base_dir / f"sim_{i:04d}"
                sim_dir.mkdir(parents=True, exist_ok=True)

                # Copy and modify mcxlab_setting.template.yaml
                template_path = self.unique_output_dir / "metadata" / MCXLAB_SETTING_FILE_TEMPLATE
                sim_setting_path = sim_dir / MCXLAB_SETTING_FILE

                with open(template_path) as f:
                    mcx_config_data = yaml.safe_load(f)

                # Modify settings based on mus/mua and hardware parameters
                # (This is a placeholder - actual implementation would depend on the schema)
                mcx_config_data["prop"] = self._get_mcx_optical_parameters(
                    mus_values=mus_data[i],
                    mua_values=self.optical_settings.mc_mua_mean,  # type: ignore
                )

                mcx_config_data["srcpos"] = self._get_srcpos()
                mcx_config_data["detpos"] = self._get_detpos()

                # mcx_config_data["srcpos"] = [20.0, 20.0, 0.0]
                # mcx_config_data["detpos"] = [
                #     {
                #         "x": 20.0,
                #         "y": 20.0,
                #         "z": 0.0,
                #         "radius": 5.0,
                #     },
                #     {
                #         "x": 40.0,
                #         "y": 20.0,
                #         "z": 0.0,
                #         "radius": 5.0,
                #     },
                # ]
                mcx_config_data["angleinvcdf"]["file_path"] = str(ANGLE_INVCDF_FILE)
                mcx_config_data["vol"]["type"] = "file_path"
                mcx_config_data["vol"]["file_path"] = str(self.volume_path)
                mcx_config_data["unitinmm"] = (
                    self.loaded_configs.hardware_config.hardware.voxel_size
                )

                # mcx_config_data['hardware'] = self.loaded_configs.hardware_config.hardware.model_dump()
                # mcx_config_data['volume_file'] = str(self.volume_path)

                with open(sim_setting_path, "w") as f:
                    yaml.safe_dump(mcx_config_data, f)

            logger.success(
                f"✓ Created simulation directory: {self.unique_output_dir / op_case_name / base_dir}"
            )


if __name__ == "__main__":
    sim_builder = SimulationBuilder(
        subject_id="example_subject_1",
        volume_path=ULTRASOUND_VOLUME_DIRNAME / "HW_20230903_merge_vol.npy",
    )

    sim_builder.create_simulation_metadata(optical_setting_file=IJV_LARGE_OPTICAL_SETTING_FILE)
