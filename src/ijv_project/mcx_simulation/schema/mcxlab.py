"""
MCXLab Configuration Schema using Pydantic v2

This module defines the complete configuration schema for MCXLab (Monte Carlo eXtreme for MATLAB/Python)
based on the official documentation and pmcx.cpp source code.

Author: Generated based on MCXLab documentation and pmcx.cpp
License: GNU General Public License version 3 (GPLv3)
"""

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field, field_validator


class OpticalProperties(BaseModel):
    """Optical properties for each medium type"""

    mua: float = Field(..., description="Absorption coefficient (1/mm)")
    mus: float = Field(..., description="Scattering coefficient (1/mm)")
    g: float = Field(..., description="Anisotropy factor")
    n: float = Field(..., description="Refractive index")


class PolarizedOpticalProperties(BaseModel):
    """Polarized optical properties for polarized MC simulation"""

    mua: float = Field(..., description="Absorption coefficient (1/mm)")
    radius: float = Field(..., description="Particle radius (micron)")
    volume_density: float = Field(..., description="Volume density (1/micron^3)")
    sphere_n: float = Field(..., description="Sphere refractive index")
    ambient_n: float = Field(..., description="Ambient medium refractive index")


class DetectorPosition(BaseModel):
    """Detector position and radius"""

    x: float = Field(..., description="X position")
    y: float = Field(..., description="Y position")
    z: float = Field(..., description="Z position")
    radius: float = Field(..., description="Detector radius")


class SourceTypes(str):
    """Enumeration of available source types"""

    PENCIL = "pencil"
    ISOTROPIC = "isotropic"
    CONE = "cone"
    GAUSSIAN = "gaussian"
    PLANAR = "planar"
    PATTERN = "pattern"
    FOURIER = "fourier"
    ARCSINE = "arcsine"
    DISK = "disk"
    FOURIERX = "fourierx"
    FOURIERX2D = "fourierx2d"
    ZGAUSSIAN = "zgaussian"
    LINE = "line"
    SLIT = "slit"
    PENCILARRAY = "pencilarray"
    PATTERN3D = "pattern3d"
    HYPERBOLOID = "hyperboloid"
    RING = "ring"


class OutputTypes(str):
    """Enumeration of output types"""

    FLUX = "flux"
    FLUENCE = "fluence"
    ENERGY = "energy"
    JACOBIAN = "jacobian"
    NSCAT = "nscat"
    WL = "wl"
    WP = "wp"
    WM = "wm"
    RF = "rf"
    LENGTH = "length"
    RFMUS = "rfmus"
    WLTOF = "wltof"
    WPTOF = "wptof"


class BoundaryConditions(str):
    """Boundary condition characters"""

    UNDEFINED = "_"
    REFLECTION = "r"
    ABSORPTION = "a"
    MIRROR = "m"
    CYCLIC = "c"


class MCXConfig(BaseModel):
    """
    Complete MCXLab configuration schema following Pydantic v2

    This schema covers all configuration parameters supported by MCXLab
    as documented in the readme and implemented in pmcx.cpp
    """

    model_config = ConfigDict(
        validate_assignment=True, arbitrary_types_allowed=True, extra="forbid"
    )

    # ===== Required Fields =====
    nphoton: int = Field(..., description="Total number of photons to simulate")
    vol: Any = Field(..., description="3D/4D array specifying media index in domain")
    prop: list[OpticalProperties] | None = Field(
        default=None, description="Optical properties array [mua, mus, g, n] for each medium"
    )
    tstart: float = Field(..., description="Starting time of simulation (seconds)")
    tstep: float = Field(..., description="Time-gate width (seconds)")
    tend: float = Field(..., description="Ending time of simulation (seconds)")
    srcpos: list[float] | list[list[float]] | None = Field(
        default=None, description="Source position [x,y,z] or [x,y,z,w0] in grid units"
    )
    srcdir: list[float] | list[list[float]] = Field(
        ..., description="Source direction [vx,vy,vz] or [vx,vy,vz,focal_length]"
    )

    # ===== MC Simulation Settings =====
    seed: int | Any | None = Field(default=-1, description="Random number generator seed")
    respin: int | None = Field(default=1, description="Number of simulation repetitions")
    isreflect: int | None = Field(
        default=1, description="Consider refractive index mismatch (1) or matched (0)"
    )
    bc: str | None = Field(default=None, description="Boundary conditions string (6-12 chars)")
    isnormalized: int | None = Field(
        default=1, description="Normalize output fluence to unitary source"
    )
    isspecular: int | None = Field(
        default=0, description="Calculate specular reflection if source is outside"
    )
    maxgate: int | None = Field(default=None, description="Number of time-gates per simulation")
    minenergy: float | None = Field(
        default=0.0, description="Terminate photon when weight less than this level"
    )
    unitinmm: float | None = Field(default=1.0, description="Length unit for grid edge length")
    shapes: str | None = Field(
        default=None, description="JSON string for additional shapes in grid"
    )
    invcdf: list[float] | None = Field(
        default=None, description="User-specified scattering phase function"
    )
    angleinvcdf: Any = Field(default=None, description="User-specified launch angle distribution")
    gscatter: int | None = Field(
        default=int(1e9), description="Number of scattering events before ignoring anisotropy"
    )
    detphotons: Any | None = Field(default=None, description="Detected photon data for replay mode")
    polprop: list[PolarizedOpticalProperties] | None = Field(
        default=None, description="Polarized optical properties"
    )

    # ===== GPU Settings =====
    autopilot: int | None = Field(
        default=0, description="Automatically set threads and blocks (1) or manual (0)"
    )
    nblocksize: int | None = Field(default=64, description="Number of CUDA thread blocks")
    nthread: int | None = Field(default=2048, description="Total CUDA thread number")
    gpuid: int | str | None = Field(
        default=1, description="GPU index or binary string for multiple GPUs"
    )
    workload: list[float] | None = Field(
        default=None, description="Relative loads for each selected GPU"
    )
    isgpuinfo: int | None = Field(default=0, description="Print GPU info (1) or not (0)")

    # ===== Source-Detector Parameters =====
    detpos: list[DetectorPosition] | None = Field(
        default=None, description="Detector positions [x,y,z,radius]"
    )
    maxdetphoton: int | None = Field(
        default=1000000, description="Maximum number of photons saved by detectors"
    )
    srctype: str | None = Field(default="pencil", description="Source type")
    srcparam1: list[float] | list[list[float]] | None = Field(
        default=None, description="Source parameter 1 (source-type dependent)"
    )
    srcparam2: list[float] | list[list[float]] | None = Field(
        default=None, description="Source parameter 2 (source-type dependent)"
    )
    srcpattern: Any | None = Field(
        default=None, description="Source pattern array for pattern/pattern3d sources"
    )
    srcnum: int | None = Field(
        default=1, description="Number of source patterns for simultaneous simulation"
    )
    srcid: int | None = Field(
        default=0, description="Source ID selector for multi-source simulation"
    )
    omega: float | None = Field(
        default=None, description="Source modulation frequency (rad/s) for RF replay"
    )
    srciquv: list[float] | None = Field(
        default=None, description="Stokes vector [I,Q,U,V] of incident light"
    )
    lambda_: float | None = Field(
        default=None, alias="lambda", description="Source light wavelength (nm) for polarized MC"
    )
    issrcfrom0: int | None = Field(
        default=1, description="First voxel is [0,0,0] (1) or [1,1,1] (0)"
    )
    replaydet: int | None = Field(default=None, description="Detector index for replay mode")
    voidtime: int | None = Field(
        default=1, description="Start timer at launch (1) or first non-zero voxel (0)"
    )

    # ===== Output Control =====
    savedetflag: str | None = Field(
        default="dp", description="String controlling detected photon data fields"
    )
    issaveexit: bool | None = Field(default=False, description="Save exit position and direction")
    ismomentum: bool | None = Field(default=False, description="Save photon momentum transfer")
    issaveref: bool | None = Field(
        default=False, description="Save diffuse reflectance/transmittance"
    )
    issave2pt: bool | None = Field(default=True, description="Save volumetric output")
    issavedet: int | None = Field(default=True, description="Save detected photon data control")
    outputtype: str | None = Field(default="flux", description="Output type")
    session: str | None = Field(default=None, description="Session string for output file names")

    # ===== Debug Parameters =====
    debuglevel: str | None = Field(
        default="P", description="Debug flag string combination of R,M,P,T"
    )
    flog: int | str | None = Field(default="/dev/null", description="Log printing control")
    istrajstokes: bool | None = Field(
        default=False, description="Include Stokes IQUV vector in trajectory output"
    )
    maxjumpdebug: int | None = Field(
        default=10000000, description="Maximum trajectory positions stored"
    )

    # ===== Additional Parameters from pmcx.cpp =====
    isref3: int | None = Field(default=None, description="3D reflection handling")
    isrefint: int | None = Field(default=None, description="Internal reflection handling")
    sradius: float | None = Field(default=None, description="Source radius parameter")
    printnum: int | None = Field(default=None, description="Print control number")
    faststep: bool | None = Field(default=None, description="Enable fast stepping")
    maxvoidstep: int | None = Field(default=None, description="Maximum void steps")
    steps: list[float] | None = Field(default=None, description="Step size vector [x,y,z]")
    crop0: list[int] | None = Field(default=None, description="Crop start position [x,y,z]")
    crop1: list[int] | None = Field(default=None, description="Crop end position [x,y,z]")
    issaveseed: bool | None = Field(default=False, description="Save random number seeds")

    @field_validator("nphoton")
    @classmethod
    def validate_nphoton(cls, v):
        if v <= 0:
            raise ValueError("nphoton must be positive")
        if v > 2**63 - 1:
            raise ValueError("nphoton exceeds maximum supported value")
        return v

    @field_validator("prop")
    @classmethod
    def validate_prop(cls, v):
        if len(v) == 0:
            raise ValueError("prop array cannot be empty")
        # First row should typically be background [0,0,1,1]
        return v

    @field_validator("tstart", "tstep", "tend")
    @classmethod
    def validate_time_params(cls, v):
        if v < 0:
            raise ValueError("Time parameters must be non-negative")
        return v

    @field_validator("srcpos", "srcdir")
    @classmethod
    def validate_source_vectors(cls, v):
        if isinstance(v, list):
            if len(v) == 0:
                raise ValueError("Source vectors cannot be empty")
            if isinstance(v[0], list):
                # Multiple sources
                for src in v:
                    if len(src) < 3 or len(src) > 4:
                        raise ValueError("Each source vector must have 3 or 4 elements")
            else:
                # Single source
                if len(v) < 3 or len(v) > 4:
                    raise ValueError("Source vector must have 3 or 4 elements")
        return v

    @field_validator("bc")
    @classmethod
    def validate_bc(cls, v):
        if v is not None:
            if len(v) < 6 or len(v) > 12:
                raise ValueError("BC string must be 6-12 characters")
            valid_chars = set("_ramcRAMC01")
            if not all(c in valid_chars for c in v):
                raise ValueError("Invalid characters in BC string")
        return v

    @field_validator("srctype")
    @classmethod
    def validate_srctype(cls, v):
        if v is not None:
            valid_types = {
                "pencil",
                "isotropic",
                "cone",
                "gaussian",
                "planar",
                "pattern",
                "fourier",
                "arcsine",
                "disk",
                "fourierx",
                "fourierx2d",
                "zgaussian",
                "line",
                "slit",
                "pencilarray",
                "pattern3d",
                "hyperboloid",
                "ring",
            }
            if v not in valid_types:
                raise ValueError(f"Invalid source type: {v}")
        return v

    @field_validator("outputtype")
    @classmethod
    def validate_outputtype(cls, v):
        if v is not None:
            valid_types = {
                "flux",
                "fluence",
                "energy",
                "jacobian",
                "nscat",
                "wl",
                "wp",
                "wm",
                "rf",
                "length",
                "rfmus",
                "wltof",
                "wptof",
            }
            if v not in valid_types:
                raise ValueError(f"Invalid output type: {v}")
        return v

    @field_validator("debuglevel")
    @classmethod
    def validate_debuglevel(cls, v):
        if v is not None:
            valid_chars = set("RMPT")
            if not all(c.upper() in valid_chars for c in v):
                raise ValueError("Debug level must contain only R, M, P, T characters")
        return v

    @field_validator("savedetflag")
    @classmethod
    def validate_savedetflag(cls, v):
        if v is not None:
            valid_chars = set("dspmnxvwi")
            if not all(c.lower() in valid_chars for c in v):
                raise ValueError("Invalid characters in savedetflag")
        return v

    # def read_volume_data_from_path(self, vol_path: Path) -> np.ndarray:
    #     """Helper function to read volume data based on vol_config"""
    #     if not vol_path.is_absolute():
    #         # Make path relative to YAML file location

    #     if not vol_path.exists():
    #         logger.warning(f"Volume file not found: {vol_path}")
    #         return np.array([])

    #     logger.info(f"Loading volume from {vol_path}")
    #     return np.load(vol_path)

    @classmethod
    def from_yaml(cls, yaml_path: str | Path) -> "MCXConfig":
        """
        Load MCXConfig from a YAML file.

        Args:
            yaml_path: Path to the YAML configuration file

        Returns:
            MCXConfig instance with loaded configuration

        Raises:
            FileNotFoundError: If YAML file doesn't exist
            ValueError: If YAML format is invalid or required fields are missing

        Example:
            >>> config = MCXConfig.from_yaml("config/mcxlab_setting.yaml")
        """
        yaml_path = Path(yaml_path)

        if not yaml_path.exists():
            raise FileNotFoundError(f"YAML configuration file not found: {yaml_path}")

        logger.info(f"Loading MCXConfig from {yaml_path}")

        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        if not data:
            raise ValueError(f"Empty YAML file: {yaml_path}")

        # Process volume data
        if "vol" in data and isinstance(data["vol"], dict):
            vol_config = data["vol"]
            vol_type = vol_config.get("type")

            if vol_type == "file_path":
                vol_path = Path(vol_config["file_path"])
                if not vol_path.is_absolute():
                    # Make path relative to YAML file location
                    vol_path = yaml_path.parent / vol_path

                if not vol_path.exists():
                    logger.warning(f"Volume file not found: {vol_path}")
                else:
                    logger.info(f"Loading volume from {vol_path}")
                    data["vol"] = np.load(vol_path)

            elif vol_type == "auto_generate":
                dimensions = vol_config["dimensions"]
                logger.info(f"Auto-generating volume with dimensions {dimensions}")
                data["vol"] = np.ones(dimensions, dtype=np.uint8)

            elif vol_type == "explicit":
                data["vol"] = np.array(vol_config["values"], dtype=np.uint8)
            else:
                raise ValueError(
                    f"Invalid vol type: {vol_type}. Must be 'file_path', 'auto_generate', or 'explicit'"
                )

        # Process optical properties
        if "prop" in data and isinstance(data["prop"], list):
            props = []
            for prop_dict in data["prop"]:
                if isinstance(prop_dict, dict):
                    props.append(OpticalProperties(**prop_dict))
                elif isinstance(prop_dict, list) and len(prop_dict) == 4:
                    # Handle [mua, mus, g, n] format
                    props.append(
                        OpticalProperties(
                            mua=prop_dict[0], mus=prop_dict[1], g=prop_dict[2], n=prop_dict[3]
                        )
                    )
                else:
                    raise ValueError(f"Invalid prop format: {prop_dict}")
            data["prop"] = props

        # Process detector positions
        if "detpos" in data and isinstance(data["detpos"], list):
            detectors = []
            for det_dict in data["detpos"]:
                if isinstance(det_dict, dict):
                    detectors.append(DetectorPosition(**det_dict))
                elif isinstance(det_dict, list) and len(det_dict) == 4:
                    # Handle [x, y, z, radius] format
                    detectors.append(
                        DetectorPosition(
                            x=det_dict[0], y=det_dict[1], z=det_dict[2], radius=det_dict[3]
                        )
                    )
                else:
                    raise ValueError(f"Invalid detpos format: {det_dict}")
            data["detpos"] = detectors

        # Process angleinvcdf if it's a file path
        if "angleinvcdf" in data and isinstance(data["angleinvcdf"], dict):
            if "file_path" in data["angleinvcdf"]:
                angle_path = Path(data["angleinvcdf"]["file_path"])
                if not angle_path.is_absolute():
                    angle_path = yaml_path.parent / angle_path

                if not angle_path.exists():
                    logger.warning(f"Angle invcdf file not found: {angle_path}")
                else:
                    logger.info(f"Loading angleinvcdf from {angle_path}")
                    data["angleinvcdf"] = pd.read_csv(angle_path)["angleinvcdf"].to_list()

        # Process srcpos if needed
        if "srcpos" in data:
            srcpos = data["srcpos"]
            if isinstance(srcpos, dict) and "file_path" in srcpos:
                srcpos_path = Path(srcpos["file_path"])
                if not srcpos_path.is_absolute():
                    srcpos_path = yaml_path.parent / srcpos_path
                logger.info(f"Loading srcpos from {srcpos_path}")
                data["srcpos"] = np.load(srcpos_path).tolist()

        # Remove null values (YAML nulls become Python None)
        data = {k: v for k, v in data.items() if v is not None}

        logger.success(f"Successfully loaded configuration with {data.get('nphoton', 0):,} photons")

        # Create and return MCXConfig instance
        return cls(**data)

    def to_pmcx_dict(self) -> dict:
        """Create MCXConfig from dictionary, handling nested models."""
        result = self.model_dump()
        if "prop" in result and isinstance(result["prop"], list):
            result["prop"] = np.double(
                [[p["mua"], p["mus"], p["g"], p["n"]] for p in result["prop"]]  # type: ignore
            )
        if "detpos" in result and isinstance(result["detpos"], list):
            result["detpos"] = np.double(
                [[d["x"], d["y"], d["z"], d["radius"]] for d in result["detpos"]]  # type: ignore
            )

        # remove None values for pmcx compatibility
        result = {k: v for k, v in result.items() if v is not None}
        return result


class MCXLabResult(BaseModel):
    """
    MCXLab simulation result schema
    """

    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    flux: Any | None = Field(default=None, description="Volumetric fluence data")
    stat: dict | None = Field(default=None, description="Simulation statistics")
    detphoton: dict | None = Field(default=None, description="Detected photon data")
    vol: Any | None = Field(default=None, description="Preprocessed volume")
    seeds: Any | None = Field(default=None, description="Random number seeds")
    traj: Any | None = Field(default=None, description="Photon trajectory data")


# Example usage and validation
def create_example_config() -> MCXConfig:
    """Create an example MCXLab configuration"""

    # Define optical properties
    props = [
        OpticalProperties(mua=0.0, mus=0.0, g=1.0, n=1.0),  # Background
        OpticalProperties(mua=0.005, mus=1.0, g=0.0, n=1.37),  # Tissue 1
        OpticalProperties(mua=0.2, mus=10.0, g=0.9, n=1.37),  # Tissue 2
    ]

    # Define detectors
    detectors = [
        DetectorPosition(x=30, y=20, z=1, radius=1),
        DetectorPosition(x=30, y=40, z=1, radius=1),
        DetectorPosition(x=20, y=30, z=1, radius=1),
        DetectorPosition(x=40, y=30, z=1, radius=1),
    ]

    # Create volume (example: 60x60x60 with inclusion)
    vol = np.ones((60, 60, 60), dtype=np.uint8)
    vol[20:40, 20:40, 10:30] = 2  # Add inclusion
    vol[:, :, 0] = 0  # Pad with zeros for reflectance

    config = MCXConfig(
        # Required parameters
        nphoton=int(1e7),
        vol=vol,
        prop=props,
        tstart=0.0,
        tstep=5e-10,
        tend=5e-9,
        srcpos=[30, 30, 1],
        srcdir=[0, 0, 1],
        # Optional parameters
        detpos=detectors,
        issrcfrom0=1,
        issaveref=True,
        gpuid=1,
        autopilot=1,
        session="example_simulation",
    )

    return config
