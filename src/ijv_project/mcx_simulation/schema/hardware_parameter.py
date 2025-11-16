"""
Hardware Parameter Schema for YAML Configuration

This module defines the Pydantic schema for loading hardware_parameter.yaml files.
It provides type-safe configuration for volume parameters, source, and detector hardware.

Author: Generated for IJV-Project
License: GNU General Public License version 3 (GPLv3)
"""

from pathlib import Path

import yaml
from loguru import logger
from pydantic import BaseModel, Field, field_validator


class SourceHolder(BaseModel):
    """Source holder configuration.

    The source holder is placed in the center of the whole model and pasted onto tissue surface.
    """

    x_size: float = Field(..., gt=0.0, description="X dimension of source holder (mm)")
    y_size: float = Field(..., gt=0.0, description="Y dimension of source holder (mm)")
    z_size: float = Field(..., gt=0.0, description="Z dimension of source holder (mm)")
    irradiation_window_radius: float = Field(
        ..., gt=0.0, description="Radius of irradiation window (mm)"
    )


class LED(BaseModel):
    """LED configuration.

    The LED is placed in the center of source holder.
    """

    x_size: float = Field(..., gt=0.0, description="X dimension of LED (mm)")
    y_size: float = Field(..., gt=0.0, description="Y dimension of LED (mm)")
    surface_to_window_distance: float = Field(
        ..., gt=0.0, description="Distance from LED surface to irradiated window (mm)"
    )
    sampling_num_radiation_pattern: float = Field(
        ..., gt=0, description="Sampling number for radiation pattern"
    )
    led_profile_in_3d_filename: str = Field(
        ..., description="Filename for 3D LED profile (CSV format)"
    )
    angleinvcdf_filename: str = Field(..., description="Filename for angle inverse CDF (CSV)")

    @field_validator("led_profile_in_3d_filename", "angleinvcdf_filename")
    @classmethod
    def validate_csv_extension(cls, v: str) -> str:
        """Validate that filename has .csv extension."""
        if not v.endswith(".csv"):
            logger.warning(f"LED profile filename '{v}' doesn't have .csv extension")
        return v


class SourceConfig(BaseModel):
    """Complete source configuration including holder and LED."""

    holder: SourceHolder = Field(..., description="Source holder configuration")
    led: LED = Field(..., description="LED configuration")


class DetectorHolder(BaseModel):
    """Detector holder configuration.

    The detector holder is placed right next to the source holder.
    """

    x_size: float = Field(..., gt=0.0, description="X dimension of detector holder (mm)")
    y_size: float = Field(..., gt=0.0, description="Y dimension of detector holder (mm)")
    z_size: float = Field(..., gt=0.0, description="Z dimension of detector holder (mm)")


class Prism(BaseModel):
    """Prism configuration.

    The prism is placed in the middle of detector holder and on the skin surface.
    """

    x_size: float = Field(..., gt=0.0, description="X dimension of prism (mm)")
    y_size: float = Field(..., gt=0.0, description="Y dimension of prism (mm)")
    z_size: float = Field(..., gt=0.0, description="Z dimension of prism (mm)")


class OpticalFiber(BaseModel):
    """Optical fiber configuration for detection."""

    sds: float = Field(..., gt=0.0, description="Source-detector separation (mm)")
    radius: float = Field(..., gt=0.0, description="Fiber radius (mm)")


class DetectorConfig(BaseModel):
    """Complete detector configuration including holder, prism, and fibers."""

    holder: DetectorHolder = Field(..., description="Detector holder configuration")
    prism: Prism = Field(..., description="Prism configuration")
    fibers: list[OpticalFiber] = Field(
        ..., min_length=1, description="Optical fibers configuration"
    )

    def get_fiber_by_sds(self, sds: float, tolerance: float = 1e-6) -> OpticalFiber:
        """Get optical fiber by source-detector separation.

        Args:
            sds: Source-detector separation to search for (mm)
            tolerance: Tolerance for floating point comparison

        Returns:
            OpticalFiber matching the SDS

        Raises:
            ValueError: If no fiber with matching SDS is found
        """
        for fiber in self.fibers:
            if abs(fiber.sds - sds) < tolerance:
                return fiber

        raise ValueError(
            f"No fiber found with SDS={sds}mm. Available SDS: {[f.sds for f in self.fibers]}"
        )

    def get_all_sds(self) -> list[float]:
        """Get all source-detector separations.

        Returns:
            List of SDS values (mm)
        """
        return [fiber.sds for fiber in self.fibers]


class HardwareParameters(BaseModel):
    """Hardware parameters for simulation setup."""

    voxel_size: float = Field(..., gt=0.0, description="Voxel size for MCX simulation (mm/voxel)")
    source: SourceConfig = Field(..., description="Source configuration")
    detector: DetectorConfig = Field(..., description="Detector configuration")

    def mm_to_voxels(self, mm: float) -> float:
        """Convert millimeters to voxels.

        Args:
            mm: Distance in millimeters

        Returns:
            Distance in voxels
        """
        return mm / self.voxel_size

    def voxels_to_mm(self, voxels: float) -> float:
        """Convert voxels to millimeters.

        Args:
            voxels: Distance in voxels

        Returns:
            Distance in millimeters
        """
        return voxels * self.voxel_size


class HardwareParameterSchema(BaseModel):
    """
    Complete schema for hardware_parameter.yaml configuration file.

    This schema validates and loads hardware parameters including voxel size,
    source configuration (holder, LED), and detector configuration (holder, prism, fibers).
    """

    hardware: HardwareParameters = Field(..., description="Hardware parameters")

    @classmethod
    def from_yaml(cls, yaml_path: str | Path) -> "HardwareParameterSchema":
        """Load configuration from YAML file.

        Args:
            yaml_path: Path to the YAML configuration file

        Returns:
            Validated HardwareParameterSchema instance

        Raises:
            FileNotFoundError: If YAML file doesn't exist
            ValueError: If YAML is invalid or validation fails
        """
        path = Path(yaml_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {yaml_path}")

        logger.info(f"Loading hardware parameter from: {path}")

        with open(path) as f:
            data = yaml.safe_load(f)

        try:
            config = cls(**data)
            logger.success("Hardware parameter loaded and validated successfully")
            return config
        except Exception as e:
            logger.error(f"Failed to validate hardware parameter: {e}")
            raise

    def to_yaml(self, yaml_path: str | Path) -> None:
        """Save configuration to YAML file.

        Args:
            yaml_path: Path where to save the YAML file
        """
        path = Path(yaml_path)
        logger.info(f"Saving hardware parameter to: {path}")

        data = self.model_dump(exclude_none=True)

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        logger.success("Hardware parameter saved successfully")

    def get_voxel_size(self) -> float:
        """Get voxel size in mm/voxel.

        Returns:
            Voxel size
        """
        return self.hardware.voxel_size

    def get_source_led_profile_path(self, base_dir: Path | None = None) -> Path:
        """Get full path to LED profile file.

        Args:
            base_dir: Base directory for LED profile. If None, uses parent of config file.

        Returns:
            Path to LED profile file
        """
        filename = self.hardware.source.led.led_profile_in_3d_filename
        if base_dir is None:
            return Path(filename)
        return Path(base_dir) / filename

    def get_angleinvcdf_path(self, base_dir: Path | None = None) -> Path:
        """Get full path to angle inverse CDF file.

        Args:
            base_dir: Base directory for angle InvCDF. If None, uses parent of config file.

        Returns:
            Path to angle inverse CDF file
        """
        filename = self.hardware.source.led.angleinvcdf_filename
        if base_dir is None:
            return Path(filename)
        return Path(base_dir) / filename

    def get_detector_summary(self) -> dict:
        """Get summary of detector configuration.

        Returns:
            Dictionary with detector configuration summary
        """
        return {
            "num_fibers": len(self.hardware.detector.fibers),
            "sds_values": self.hardware.detector.get_all_sds(),
            "fiber_radii": [f.radius for f in self.hardware.detector.fibers],
        }

    def get_source_summary(self) -> dict:
        """Get summary of source configuration.

        Returns:
            Dictionary with source configuration summary
        """
        return {
            "holder_size": (
                self.hardware.source.holder.x_size,
                self.hardware.source.holder.y_size,
                self.hardware.source.holder.z_size,
            ),
            "window_radius": self.hardware.source.holder.irradiation_window_radius,
            "led_size": (
                self.hardware.source.led.x_size,
                self.hardware.source.led.y_size,
            ),
            "led_to_window_distance": self.hardware.source.led.surface_to_window_distance,
        }
