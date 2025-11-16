"""
Optical Setting Schema for YAML Configuration

This module defines the Pydantic schema for loading optical_setting.yaml files.
It provides type-safe configuration for tissue optical properties and dataset splits.

Author: Generated for IJV-Project
License: GNU General Public License version 3 (GPLv3)
"""

import itertools
from pathlib import Path
from typing import Annotated, Literal, TypeVar

import numpy as np
import numpy.typing as npt
import yaml
from loguru import logger
from pydantic import BaseModel, Field, field_validator, model_validator

DType = TypeVar("DType", bound=np.generic)

ArrayN = Annotated[npt.NDArray[DType], Literal["N"]]


class ReplacedOpticalProperty(BaseModel):
    """Optical property that references another tissue's property."""

    replaced_to: str = Field(..., description="Name of tissue to reference")

    @property
    def train_points(self) -> np.ndarray:
        """Not applicable for replaced properties - will be resolved at runtime."""
        raise ValueError(
            "Cannot generate points for replaced property - reference the target tissue instead"
        )

    @property
    def val_points(self) -> np.ndarray:
        """Not applicable for replaced properties - will be resolved at runtime."""
        raise ValueError(
            "Cannot generate points for replaced property - reference the target tissue instead"
        )

    @property
    def test_points(self) -> np.ndarray:
        """Not applicable for replaced properties - will be resolved at runtime."""
        raise ValueError(
            "Cannot generate points for replaced property - reference the target tissue instead"
        )


class RangeOpticalProperty(BaseModel):
    """Optical property with explicit min/max range and generation parameters."""

    min: float = Field(..., ge=0.0, description="Minimum value (1/mm)")
    max: float = Field(..., ge=0.0, description="Maximum value (1/mm)")
    generate_number: int = Field(
        default=1, ge=1, description="Number of values to generate in range"
    )

    @model_validator(mode="after")
    def validate_min_less_than_max(self) -> "RangeOpticalProperty":
        """Validate that min is less than or equal to max."""
        if self.min > self.max:
            raise ValueError(f"min ({self.min}) must be less than or equal to max ({self.max})")
        return self

    @property
    def train_points(self) -> np.ndarray:
        """Generate training points using linear spacing."""
        if self.generate_number < 2:
            if self.generate_number == 1 and self.min == self.max:
                return np.array([self.min], dtype=np.float64)
            raise ValueError("generate_number must be at least 2 to generate training points")

        return np.linspace(self.min, self.max, 3 * self.generate_number, dtype=np.float64)[::3]

    @property
    def val_points(self) -> np.ndarray:
        """Generate validation points using linear spacing."""
        if self.generate_number < 2:
            if self.generate_number == 1 and self.min == self.max:
                return np.array([self.min], dtype=np.float64)
            raise ValueError("generate_number must be at least 2 to generate validation points")

        return np.linspace(self.min, self.max, 3 * self.generate_number, dtype=np.float64)[1::3]

    @property
    def test_points(self) -> np.ndarray:
        """Generate test points using linear spacing."""
        if self.generate_number < 2:
            if self.generate_number == 1 and self.min == self.max:
                return np.array([self.min], dtype=np.float64)
            raise ValueError("generate_number must be at least 2 to generate test points")

        return np.linspace(self.min, self.max, 3 * self.generate_number, dtype=np.float64)[2::3]


# Union type for optical properties - either a range or a reference to another tissue
OpticalPropertyRange = RangeOpticalProperty | ReplacedOpticalProperty


class TissueOpticalProperties(BaseModel):
    """Optical properties for a specific tissue type."""

    media_id: int = Field(..., description="Media ID(s)")
    mua: OpticalPropertyRange = Field(..., description="Absorption coefficient range")
    mus: OpticalPropertyRange = Field(..., description="Scattering coefficient range")
    g: float = Field(..., ge=-1.0, le=1.0, description="Anisotropy factor")
    n: float = Field(..., ge=0.0, description="Refractive index")


class DatasetSplit(BaseModel):
    """Dataset split configuration.

    Defines the ratios for training, validation, and test sets.
    Train_set has 100% of the data, val_set has 10% of train_set, test_set has 10% of train_set.
    """

    val: float = Field(..., ge=0.0, le=1.0, description="Validation set ratio compare to train set")
    test: float = Field(..., ge=0.0, le=1.0, description="Test set ratio compare to train set")

    @field_validator("val", "test")
    def validate_ratios(cls, v: float) -> float:
        """Validate that ratios are between 0 and 1."""
        if not (0.0 <= v <= 1.0):
            raise ValueError("Ratios must be between 0 and 1")
        return v


class TissueTypes(BaseModel):
    """All tissue types with their optical properties."""

    fiber: TissueOpticalProperties = Field(..., description="Fiber tissue properties")
    air: TissueOpticalProperties = Field(..., description="Air tissue properties")
    pla: TissueOpticalProperties = Field(..., description="PLA tissue properties")
    prism: TissueOpticalProperties = Field(..., description="Prism tissue properties")

    skin: TissueOpticalProperties = Field(..., description="Skin tissue properties")
    fat: TissueOpticalProperties = Field(..., description="Fat tissue properties")
    muscle: TissueOpticalProperties = Field(..., description="Muscle tissue properties")
    perturbed: TissueOpticalProperties = Field(..., description="Perturbed tissue properties")
    ijv: TissueOpticalProperties = Field(
        ..., description="Internal jugular vein (IJV) tissue properties"
    )
    cca: TissueOpticalProperties = Field(
        ..., description="Common carotid artery (CCA) tissue properties"
    )

    def get_tissue_names(self) -> list[str]:
        """Get list of all tissue names.

        Returns:
            List of tissue names
        """
        # order by media_id
        ordered_tissues = sorted(self.model_fields.keys(), key=lambda x: getattr(self, x).media_id)  # type: ignore

        return ordered_tissues

    def get_tissue(self, name: str) -> TissueOpticalProperties:
        """Get tissue properties by name.

        Args:
            name: Name of the tissue `list(self.model_fields.keys())`

        Returns:
            TissueOpticalProperties for the specified tissue

        Raises:
            ValueError: If tissue name is invalid
        """

        if name not in self.model_fields:
            raise ValueError(f"Invalid tissue name: {name}")
        return getattr(self, name)

    @property
    def mus_train_set(self) -> np.ndarray:
        """Get mus training set across all tissues."""
        # note that cca mus is tied to ijv mus, so only 1 mus value for cca
        mus_values = []
        record_replaced_info: dict[int, str] = {}
        record_tissue_idx: dict[str, int] = {}
        for i, tissue in enumerate(self.get_tissue_names()):
            record_tissue_idx[tissue] = i
            tissue_prop = getattr(self, tissue).mus
            if isinstance(tissue_prop, ReplacedOpticalProperty):
                record_replaced_info[i] = tissue_prop.replaced_to
                mus_values.append([-1])  # placeholder for replaced tissue
            else:
                mus_values.append(tissue_prop.train_points.tolist())

        # Generate all combinations
        all_combinations = np.array(list(itertools.product(*mus_values)))

        # Replace placeholders with actual values from replaced tissues
        for idx, replaced_to in record_replaced_info.items():
            replaced_idx = record_tissue_idx[replaced_to]
            all_combinations[:, idx] = all_combinations[:, replaced_idx]

        return all_combinations

    @property
    def mus_val_set(self) -> np.ndarray:
        """Get mus validation set across all tissues."""
        # note that cca mus is tied to ijv mus, so only 1 mus value for cca
        mus_values = []
        record_replaced_info: dict[int, str] = {}
        record_tissue_idx: dict[str, int] = {}
        for i, tissue in enumerate(self.get_tissue_names()):
            record_tissue_idx[tissue] = i
            tissue_prop = getattr(self, tissue).mus
            if isinstance(tissue_prop, ReplacedOpticalProperty):
                record_replaced_info[i] = tissue_prop.replaced_to
                mus_values.append([-1])  # placeholder for replaced tissue
            else:
                mus_values.append(tissue_prop.val_points.tolist())

        # Generate all combinations
        all_combinations = np.array(list(itertools.product(*mus_values)))

        # Replace placeholders with actual values from replaced tissues
        for idx, replaced_to in record_replaced_info.items():
            replaced_idx = record_tissue_idx[replaced_to]
            all_combinations[:, idx] = all_combinations[:, replaced_idx]

        return all_combinations

    @property
    def mus_test_set(self) -> np.ndarray:
        """Get mus test set across all tissues."""
        # note that cca mus is tied to ijv mus, so only 1 mus value for cca
        mus_values = []
        record_replaced_info: dict[int, str] = {}
        record_tissue_idx: dict[str, int] = {}
        for i, tissue in enumerate(self.get_tissue_names()):
            record_tissue_idx[tissue] = i
            tissue_prop = getattr(self, tissue).mus
            if isinstance(tissue_prop, ReplacedOpticalProperty):
                record_replaced_info[i] = tissue_prop.replaced_to
                mus_values.append([-1])  # placeholder for replaced tissue
            else:
                mus_values.append(tissue_prop.test_points.tolist())

        # Generate all combinations
        all_combinations = np.array(list(itertools.product(*mus_values)))

        # Replace placeholders with actual values from replaced tissues
        for idx, replaced_to in record_replaced_info.items():
            replaced_idx = record_tissue_idx[replaced_to]
            all_combinations[:, idx] = all_combinations[:, replaced_idx]

        return all_combinations

    @property
    def mua_train_set(self) -> np.ndarray:
        """Get mua training set across all tissues."""
        mua_values = []
        record_replaced_info: dict[int, str] = {}
        record_tissue_idx: dict[str, int] = {}
        for i, tissue in enumerate(self.get_tissue_names()):
            record_tissue_idx[tissue] = i
            tissue_prop = getattr(self, tissue).mua
            if isinstance(tissue_prop, ReplacedOpticalProperty):
                record_replaced_info[i] = tissue_prop.replaced_to
                mua_values.append([-1])  # placeholder for replaced tissue
            else:
                mua_values.append(tissue_prop.train_points.tolist())

        # Generate all combinations
        all_combinations = np.array(list(itertools.product(*mua_values)))

        # Replace placeholders with actual values from replaced tissues
        for idx, replaced_to in record_replaced_info.items():
            replaced_idx = record_tissue_idx[replaced_to]
            all_combinations[:, idx] = all_combinations[:, replaced_idx]

        return all_combinations

    @property
    def mua_val_set(self) -> np.ndarray:
        """Get mua validation set across all tissues."""
        mua_values = []
        record_replaced_info: dict[int, str] = {}
        record_tissue_idx: dict[str, int] = {}
        for i, tissue in enumerate(self.get_tissue_names()):
            record_tissue_idx[tissue] = i
            tissue_prop = getattr(self, tissue).mua
            if isinstance(tissue_prop, ReplacedOpticalProperty):
                record_replaced_info[i] = tissue_prop.replaced_to
                mua_values.append([-1])  # placeholder for replaced tissue
            else:
                mua_values.append(tissue_prop.val_points.tolist())

        # Generate all combinations
        all_combinations = np.array(list(itertools.product(*mua_values)))

        # Replace placeholders with actual values from replaced tissues
        for idx, replaced_to in record_replaced_info.items():
            replaced_idx = record_tissue_idx[replaced_to]
            all_combinations[:, idx] = all_combinations[:, replaced_idx]

        return all_combinations

    @property
    def mua_test_set(self) -> np.ndarray:
        """Get mua test set across all tissues."""
        mua_values = []
        record_replaced_info: dict[int, str] = {}
        record_tissue_idx: dict[str, int] = {}
        for i, tissue in enumerate(self.get_tissue_names()):
            record_tissue_idx[tissue] = i
            tissue_prop = getattr(self, tissue).mua
            if isinstance(tissue_prop, ReplacedOpticalProperty):
                record_replaced_info[i] = tissue_prop.replaced_to
                mua_values.append([-1])  # placeholder for replaced tissue
            else:
                mua_values.append(tissue_prop.test_points.tolist())

        # Generate all combinations
        all_combinations = np.array(list(itertools.product(*mua_values)))

        # Replace placeholders with actual values from replaced tissues
        for idx, replaced_to in record_replaced_info.items():
            replaced_idx = record_tissue_idx[replaced_to]
            all_combinations[:, idx] = all_combinations[:, replaced_idx]

        return all_combinations


class OpticalSettingSchema(BaseModel):
    """
    Complete schema for optical_setting.yaml configuration file.

    This schema validates and loads optical property boundaries for different tissue types
    and dataset split ratios.
    """

    dataset: DatasetSplit = Field(..., description="Dataset split ratios")
    tissues: TissueTypes = Field(..., description="Optical properties for all tissue types")

    @classmethod
    def from_yaml(cls, yaml_path: str | Path) -> "OpticalSettingSchema":
        """Load configuration from YAML file.

        Args:
            yaml_path: Path to the YAML configuration file

        Returns:
            Validated OpticalSettingSchema instance

        Raises:
            FileNotFoundError: If YAML file doesn't exist
            ValueError: If YAML is invalid or validation fails
        """
        path = Path(yaml_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {yaml_path}")

        logger.info(f"Loading optical setting from: {path}")

        with open(path) as f:
            data = yaml.safe_load(f)

        try:
            config = cls(**data)
            logger.success("Optical setting loaded and validated successfully")
            return config
        except Exception as e:
            logger.error(f"Failed to validate optical setting: {e}")
            raise

    def to_yaml(self, yaml_path: str | Path) -> None:
        """Save configuration to YAML file.

        Args:
            yaml_path: Path where to save the YAML file
        """
        path = Path(yaml_path)
        logger.info(f"Saving optical setting to: {path}")

        data = self.model_dump(exclude_none=True)

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        logger.success("Optical setting saved successfully")

    @property
    def mua_range_summary(self) -> dict[str, tuple[float, float]]:
        """Get summary of mua ranges for all tissues.

        Returns:
            Dictionary mapping tissue name to (min, max) mua values
        """
        out_dict = {}
        for tissue_name in self.tissues.get_tissue_names():
            tissue = self.tissues.get_tissue(tissue_name)
            if isinstance(tissue.mua, ReplacedOpticalProperty):
                replaced_tissue = self.tissues.get_tissue(tissue.mua.replaced_to)
                # Get the range from the replaced tissue
                if isinstance(replaced_tissue.mua, RangeOpticalProperty):
                    out_dict[tissue_name] = (replaced_tissue.mua.min, replaced_tissue.mua.max)
                else:
                    raise ValueError(
                        f"Replaced tissue {tissue.mua.replaced_to} must have range property"
                    )
            else:
                out_dict[tissue_name] = (tissue.mua.min, tissue.mua.max)

        return out_dict

    @property
    def mus_range_summary(self) -> dict[str, tuple[float, float]]:
        """Get summary of mus ranges for all tissues.

        Returns:
            Dictionary mapping tissue name to (min, max) mus values
        """
        out_dict = {}
        for tissue_name in self.tissues.get_tissue_names():
            tissue = self.tissues.get_tissue(tissue_name)
            if isinstance(tissue.mus, ReplacedOpticalProperty):
                replaced_tissue = self.tissues.get_tissue(tissue.mus.replaced_to)
                # Get the range from the replaced tissue
                if isinstance(replaced_tissue.mus, RangeOpticalProperty):
                    out_dict[tissue_name] = (replaced_tissue.mus.min, replaced_tissue.mus.max)
                else:
                    raise ValueError(
                        f"Replaced tissue {tissue.mus.replaced_to} must have range property"
                    )
            else:
                out_dict[tissue_name] = (tissue.mus.min, tissue.mus.max)

        return out_dict

    @property
    def total_mus_combinations(self) -> int:
        """Calculate total number of mus combinations across all tissues.

        mus_combinations = (mus_skin * mus_fat * mus_muscle * mus_ijv * mus_cca(1) )

        Returns:
            Total number of mus combinations across all tissues

        Note: Replaced properties (e.g., CCA mus tied to IJV mus) count as 1
        """
        total = 1
        for tissue_name in self.tissues.get_tissue_names():
            tissue = self.tissues.get_tissue(tissue_name)
            if isinstance(tissue.mus, ReplacedOpticalProperty):
                # Replaced properties contribute 1 to the total
                mus_num = 1
            else:
                mus_num = tissue.mus.generate_number
            total *= mus_num
        return total

    @property
    def total_mua_combinations(self) -> int:
        """Calculate total number of mua combinations across all tissues.

        mua_combinations = (mua_skin * mua_fat * mua_muscle * mua_ijv * mua_cca)

        Returns:
            Total number of mua combinations across all tissues

        Note: Replaced properties contribute 1 to the total
        """
        total = 1
        for tissue_name in self.tissues.get_tissue_names():
            tissue = self.tissues.get_tissue(tissue_name)
            if isinstance(tissue.mua, ReplacedOpticalProperty):
                # Replaced properties contribute 1 to the total
                mua_num = 1
            else:
                mua_num = tissue.mua.generate_number
            total *= mua_num
        return total

    @property
    def mus_dataset(self) -> dict[str, np.ndarray]:
        """Get mus dataset split into train, val, test sets.

        Returns:
            Dictionary with keys 'train', 'val', 'test' mapping to mus parameter arrays
        """
        assert self.tissues.mus_train_set.shape[0] == self.total_mus_combinations, (
            f"Expected {self.total_mus_combinations} mus_train samples, but got {self.tissues.mus_train_set.shape[0]}"
        )
        assert self.tissues.mus_val_set.shape[0] == self.total_mus_combinations, (
            f"Expected {self.total_mus_combinations} mus_val samples, but got {self.tissues.mus_val_set.shape[0]}"
        )
        assert self.tissues.mus_test_set.shape[0] == self.total_mus_combinations, (
            f"Expected {self.total_mus_combinations} mus_test samples, but got {self.tissues.mus_test_set.shape[0]}"
        )

        # Shuffle the datasets for fair sampling
        np.random.shuffle(self.tissues.mus_val_set)
        np.random.shuffle(self.tissues.mus_test_set)

        # Split into val/test based on dataset ratios
        n_val = int(self.dataset.val * self.total_mus_combinations)
        n_test = int(self.dataset.test * self.total_mus_combinations)

        return {
            "train": self.tissues.mus_train_set,
            "val": np.sort(self.tissues.mus_val_set[:n_val], axis=0),
            "test": np.sort(self.tissues.mus_test_set[:n_test], axis=0),
        }

    @property
    def mua_dataset(self) -> dict[str, np.ndarray]:
        """Get mua dataset split into train, val, test sets.

        Returns:
            Dictionary with keys 'train', 'val', 'test' mapping to mua parameter arrays
        """
        assert self.tissues.mua_train_set.shape[0] == self.total_mua_combinations, (
            f"Expected {self.total_mua_combinations} mua_train samples, but got {self.tissues.mua_train_set.shape[0]}"
        )
        assert self.tissues.mua_val_set.shape[0] == self.total_mua_combinations, (
            f"Expected {self.total_mua_combinations} mua_val samples, but got {self.tissues.mua_val_set.shape[0]}"
        )
        assert self.tissues.mua_test_set.shape[0] == self.total_mua_combinations, (
            f"Expected {self.total_mua_combinations} mua_test samples, but got {self.tissues.mua_test_set.shape[0]}"
        )

        # Shuffle the datasets for fair sampling
        np.random.shuffle(self.tissues.mua_val_set)
        np.random.shuffle(self.tissues.mua_test_set)

        # Split into val/test based on dataset ratios
        n_val = int(self.dataset.val * self.total_mua_combinations)
        n_test = int(self.dataset.test * self.total_mua_combinations)

        return {
            "train": self.tissues.mua_train_set,
            "val": np.sort(self.tissues.mua_val_set[:n_val], axis=0),
            "test": np.sort(self.tissues.mua_test_set[:n_test], axis=0),
        }

    @property
    def mc_mua_mean(self) -> ArrayN[np.floating]:
        """Calculate mean mua across all tissues for MC simulation."""
        mua_means = []
        for tissue_name in self.tissues.get_tissue_names():
            tissue = self.tissues.get_tissue(tissue_name)
            if isinstance(tissue.mua, ReplacedOpticalProperty):
                replaced_tissue = self.tissues.get_tissue(tissue.mua.replaced_to)
                if isinstance(replaced_tissue.mua, RangeOpticalProperty):
                    mean_val = (replaced_tissue.mua.min + replaced_tissue.mua.max) / 2.0
                else:
                    raise ValueError(
                        f"Replaced tissue {tissue.mua.replaced_to} must have range property"
                    )
            else:
                mean_val = (tissue.mua.min + tissue.mua.max) / 2.0
            mua_means.append(mean_val)
        return np.array(mua_means, dtype=np.float64)
