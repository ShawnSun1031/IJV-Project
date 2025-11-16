# Configuration Schemas Documentation

This document describes the three main Pydantic configuration schemas used in the IJV-Project for type-safe YAML configuration loading.

## Overview

The project uses three separate YAML configuration files, each with its own Pydantic schema for validation:

1. **`mcxlab_setting.yaml`** - MCX simulation parameters
2. **`optical_setting.yaml`** - Tissue optical properties and dataset splits
3. **`hardware_parameter.yaml`** - Hardware parameters (voxel size, source, detector)

All schemas are located in `src/ijv_project/mcx_simulation/config/` and can be imported from the config module.

## Installation

```bash
# Install project with dependencies
uv sync

# Or with pip
pip install -e .
```

## Quick Start

```python
from pathlib import Path
from ijv_project.mcx_simulation.config import (
    MCXLabSettingSchema,
    OpticalSettingSchema,
    HardwareParameterSchema,
)

# Load configurations
mcxlab_config = MCXLabSettingSchema.from_yaml("mcxlab_setting.yaml")
optical_config = OpticalSettingSchema.from_yaml("optical_setting.yaml")
hardware_config = HardwareParameterSchema.from_yaml("hardware_parameter.yaml")

# Access validated data
print(f"Number of photons: {mcxlab_config.nphoton}")
print(f"Voxel size: {hardware_config.get_voxel_size()} mm/voxel")
print(f"Train/Val/Test split: {optical_config.dataset.train}/{optical_config.dataset.val}/{optical_config.dataset.test}")
```

## Schema 1: MCXLab Setting Schema

### Purpose
Validates complete MCXLab simulation configuration including photon parameters, source/detector setup, GPU settings, and output control.

### File Location
- Schema: `src/ijv_project/mcx_simulation/config/mcxlab_setting_schema.py`
- YAML: `src/ijv_project/mcx_simulation/config/mcxlab_setting.yaml`

### Key Features
- ✅ Type-safe validation of all MCXLab parameters
- ✅ Support for multiple volume types (auto-generate, file path, explicit)
- ✅ Detector position validation
- ✅ Optical property validation
- ✅ Angle inverse CDF loading from file

### Main Classes

#### `MCXLabSettingSchema`
The main configuration class.

**Key Fields:**
- `nphoton`: Total number of photons (required, positive integer)
- `vol`: Volume configuration (VolumeConfig instance)
- `prop`: List of optical properties (min 1 medium)
- `srcpos`, `srcdir`: Source position and direction (3-4 elements)
- `detpos`: List of detector positions (optional)
- `gpuid`: GPU selection (int or string)
- `savedetflag`: Detector data save flags (string)

**Key Methods:**
```python
# Load from YAML
config = MCXLabSettingSchema.from_yaml("mcxlab_setting.yaml")

# Save to YAML
config.to_yaml("output.yaml")

# Access volume
volume_array = config.vol.get_volume()  # Returns numpy array

# Access detector positions
for det in config.detpos:
    print(f"Detector at ({det.x}, {det.y}, {det.z}) with radius {det.radius}")
```

#### `VolumeConfig`
Handles three types of volume specification:

```python
# Type 1: Auto-generate (creates uniform volume)
vol = VolumeConfig(
    type="auto_generate",
    dimensions=[40, 40, 40]
)

# Type 2: File path (loads from .npy file)
vol = VolumeConfig(
    type="file_path",
    file_path="path/to/volume.npy"
)

# Type 3: Explicit values
vol = VolumeConfig(
    type="explicit",
    values=[[[1, 1], [1, 1]], [[1, 1], [1, 1]]]
)

# Get the actual numpy array
array = vol.get_volume()
```

#### `OpticalProperty`
Single medium optical properties:

```python
prop = OpticalProperty(
    mua=0.01,   # Absorption coefficient (1/mm), must be >= 0
    mus=10.0,   # Scattering coefficient (1/mm), must be >= 0
    g=0.9,      # Anisotropy factor, must be in [-1, 1]
    n=1.37      # Refractive index, must be > 0
)
```

#### `DetectorPosition`
Detector location and size:

```python
det = DetectorPosition(
    x=30.0,      # X position in grid units
    y=20.0,      # Y position in grid units
    z=0.0,       # Z position in grid units
    radius=1.0   # Detector radius, must be > 0
)
```

#### `AngleInvCDFConfig`
Angle inverse CDF configuration:

```python
angle_config = AngleInvCDFConfig(
    file_path="angleinvcdf.csv"
)

# Load the data
angle_data = angle_config.load_data()  # Supports .npy and .csv
```

### Validation Rules

- `nphoton`: Must be positive, max 2^63-1
- `tend`: Must be greater than `tstart`
- `srctype`: Must be one of 18 valid source types (pencil, gaussian, etc.)
- `outputtype`: Must be one of 13 valid types (flux, fluence, etc.)
- `bc`: Must be 6-12 characters from set `_ramcRAMC01`
- `savedetflag`: Must contain only characters from `dspmnxvwiDSPMNXVWI`

### Example YAML

```yaml
# Required fields
nphoton: 1000000
vol:
  type: "auto_generate"
  dimensions: [40, 40, 40]
prop:
  - mua: 0.0
    mus: 0.0
    g: 1.0
    n: 1.0
  - mua: 0.01
    mus: 10.0
    g: 0.9
    n: 1.37
tstart: 0.0
tstep: 1.0e-10
tend: 5.0e-9
srcpos: [20.0, 20.0, 0.0]
srcdir: [0.0, 0.0, 1.0]

# Optional fields
srctype: "pencil"
gpuid: 1
autopilot: 1
detpos:
  - x: 30.0
    y: 20.0
    z: 0.0
    radius: 1.0
```

---

## Schema 2: Optical Setting Schema

### Purpose
Defines tissue optical property ranges and dataset split ratios for training/validation/testing.

### File Location
- Schema: `src/ijv_project/mcx_simulation/config/optical_setting_schema.py`
- YAML: `src/ijv_project/mcx_simulation/config/optical_setting.yaml`

### Key Features
- ✅ Define min/max ranges for absorption (μₐ) and scattering (μₛ) coefficients
- ✅ Configure number of values to generate in each range
- ✅ Validate dataset split ratios sum to 1.0
- ✅ Support for 5 tissue types (skin, fat, muscle, IJV, CCA)
- ✅ Generate optical property combinations automatically

### Main Classes

#### `OpticalSettingSchema`
The main configuration class.

**Key Fields:**
- `dataset`: Dataset split ratios (DatasetSplit instance)
- `tissues`: All tissue optical properties (TissueTypes instance)

**Key Methods:**
```python
# Load from YAML
config = OpticalSettingSchema.from_yaml("optical_setting.yaml")

# Get range summaries
mua_ranges = config.get_mua_range_summary()
# Returns: {'skin': (0.0006, 0.258), 'fat': (0.0079, 0.127), ...}

mus_ranges = config.get_mus_range_summary()

# Get total combinations
total = config.get_total_combinations()  # e.g., 500

# Generate all combinations
all_combos = config.generate_all_combinations()
# Returns: {'skin': [(mua1, mus1), ...], 'fat': [...], ...}
```

#### `DatasetSplit`
Dataset split configuration with automatic validation:

```python
split = DatasetSplit(
    train=0.7,  # 70% for training
    val=0.2,    # 20% for validation
    test=0.1    # 10% for testing
)
# Automatically validates that train + val + test = 1.0
```

#### `TissueTypes`
Container for all tissue properties:

```python
# Access specific tissue
ijv_tissue = config.tissues.ijv
cca_tissue = config.tissues.cca

# Get tissue by name
tissue = config.tissues.get_tissue("skin")

# Get all tissue names
names = config.tissues.get_tissue_names()
# Returns: ['skin', 'fat', 'muscle', 'ijv', 'cca']
```

#### `TissueOpticalProperties`
Single tissue optical property ranges:

```python
tissue = TissueOpticalProperties(
    mua=OpticalPropertyRange(min=0.01, max=0.1, generate_number=10),
    mus=OpticalPropertyRange(min=5.0, max=15.0, generate_number=10)
)

# Generate combinations
combos = tissue.generate_combinations()
# Returns: [(0.01, 5.0), (0.01, 6.11), ..., (0.1, 15.0)]
# Total: 10 × 10 = 100 combinations
```

#### `OpticalPropertyRange`
Range specification with generation:

```python
mua_range = OpticalPropertyRange(
    min=0.01,           # Minimum value (>= 0)
    max=0.1,            # Maximum value (> min)
    generate_number=10  # Number of values to generate
)

# Generate values (linear spacing by default)
values = mua_range.generate_values(log_scale=False)

# Generate values (logarithmic spacing)
log_values = mua_range.generate_values(log_scale=True)
```

### Validation Rules

- `min` < `max`: Enforced for all ranges
- Dataset split: `train + val + test = 1.0` (with tolerance 1e-6)
- All values: Must be non-negative

### Example YAML

```yaml
dataset:
  train: 0.7
  val: 0.2
  test: 0.1

tissues:
  skin:
    mua:
      min: 0.0006
      max: 0.258
      generate_number: 10
    mus:
      min: 10.0
      max: 28.0
      generate_number: 10

  ijv:  # Internal jugular vein
    mua:
      min: 0.2146
      max: 0.7409
      generate_number: 10
    mus:
      min: 23.0
      max: 52.0
      generate_number: 10
```

### Usage Example

```python
# Load config
config = OpticalSettingSchema.from_yaml("optical_setting.yaml")

# Generate IJV combinations
ijv_combos = config.tissues.ijv.generate_combinations()
print(f"Generated {len(ijv_combos)} IJV combinations")

# Use with linear or log spacing
ijv_combos_log = config.tissues.ijv.generate_combinations(
    mua_log_scale=True,  # Logarithmic for absorption
    mus_log_scale=False  # Linear for scattering
)
```

---

## Schema 3: Hardware Parameter Schema

### Purpose
Defines hardware specifications including voxel size, source (holder + LED), and detector (holder + prism + fibers).

### File Location
- Schema: `src/ijv_project/mcx_simulation/config/hardware_parameter_schema.py`
- YAML: `src/ijv_project/mcx_simulation/config/hardware_parameter.yaml`

### Key Features
- ✅ Voxel size configuration for unit conversion
- ✅ Source holder and LED specifications
- ✅ Detector holder, prism, and optical fiber configurations
- ✅ Source-detector separation (SDS) management
- ✅ Automatic unit conversion (mm ↔ voxels)

### Main Classes

#### `HardwareParameterSchema`
The main configuration class.

**Key Fields:**
- `hardware`: All hardware parameters (HardwareParameters instance)

**Key Methods:**
```python
# Load from YAML
config = HardwareParameterSchema.from_yaml("hardware_parameter.yaml")

# Get voxel size
voxel_size = config.get_voxel_size()  # e.g., 0.25 mm/voxel

# Get summaries
src_summary = config.get_source_summary()
det_summary = config.get_detector_summary()

# Get file paths
led_profile_path = config.get_source_led_profile_path(base_dir=Path("data"))
angleinvcdf_path = config.get_angleinvcdf_path(base_dir=Path("data"))
```

#### `HardwareParameters`
Core hardware parameters with unit conversion:

```python
# Access hardware config
hw = config.hardware

# Unit conversion
voxels = hw.mm_to_voxels(10.0)  # Convert 10mm to voxels
mm = hw.voxels_to_mm(40)        # Convert 40 voxels to mm

# Access components
voxel_size = hw.voxel_size
source = hw.source
detector = hw.detector
```

#### `SourceConfig`
Source configuration (holder + LED):

```python
source = SourceConfig(
    holder=SourceHolder(
        x_size=20.0,
        y_size=20.0,
        z_size=10.0,
        irradiation_window_radius=1.5
    ),
    led=LED(
        x_size=1.8,
        y_size=2.55,
        surface_to_window_distance=6.0,
        sampling_num_radiation_pattern=1e4,
        led_profile_in_3d_filename="LED_profile.csv",
        angleinvcdf_filename="angleinvcdf.csv"
    )
)

# Access components
window_radius = source.holder.irradiation_window_radius
led_size = (source.led.x_size, source.led.y_size)
```

#### `DetectorConfig`
Detector configuration (holder + prism + fibers):

```python
detector = DetectorConfig(
    holder=DetectorHolder(x_size=20.0, y_size=25.0, z_size=6.0),
    prism=Prism(x_size=20.0, y_size=5.0, z_size=5.0),
    fibers=[
        OpticalFiber(sds=10.0, radius=0.3675),
        OpticalFiber(sds=20.0, radius=0.3675),
    ]
)

# Get all SDS values
sds_list = detector.get_all_sds()  # [10.0, 20.0]

# Get specific fiber by SDS
fiber_10mm = detector.get_fiber_by_sds(10.0)
print(f"Fiber radius: {fiber_10mm.radius} mm")
```

#### `OpticalFiber`
Single optical fiber specification:

```python
fiber = OpticalFiber(
    sds=10.0,       # Source-detector separation (mm)
    radius=0.3675   # Fiber radius (mm)
)
```

### Validation Rules

- All dimensions: Must be positive (> 0)
- LED filenames: Warning if not `.csv` extension
- Fiber SDS lookup: Must match exactly (with tolerance)

### Example YAML

```yaml
hardware:
  voxel_size: 0.25  # mm/voxel

  source:
    holder:
      x_size: 20.0
      y_size: 20.0
      z_size: 10.0
      irradiation_window_radius: 1.5

    led:
      x_size: 1.8
      y_size: 2.55
      surface_to_window_distance: 6.0
      sampling_num_radiation_pattern: 1e4
      led_profile_in_3d_filename: LED_profile_in3D_pfForm_0to89.csv
      angleinvcdf_filename: angleinvcdf.csv

  detector:
    holder:
      x_size: 20.0
      y_size: 25.0
      z_size: 6.0

    prism:
      x_size: 20.0
      y_size: 5.0
      z_size: 5.0

    fibers:
      - sds: 10.0
        radius: 0.3675
      - sds: 20.0
        radius: 0.3675
```

### Usage Example

```python
# Load config
config = HardwareParameterSchema.from_yaml("hardware_parameter.yaml")

# Unit conversion
voxel_size = config.get_voxel_size()
sds_10mm_voxels = config.hardware.mm_to_voxels(10.0)
print(f"10mm = {sds_10mm_voxels} voxels (voxel_size={voxel_size}mm)")

# Access detector fibers
for fiber in config.hardware.detector.fibers:
    print(f"SDS: {fiber.sds}mm, Radius: {fiber.radius}mm")

# Get specific fiber
fiber = config.hardware.detector.get_fiber_by_sds(20.0)
print(f"20mm fiber radius: {fiber.radius}mm")
```

---

## Integration Example

Combining all three schemas:

```python
from pathlib import Path
from ijv_project.mcx_simulation.config import (
    MCXLabSettingSchema,
    OpticalSettingSchema,
    HardwareParameterSchema,
)

# Load all configurations
config_dir = Path("src/ijv_project/mcx_simulation/config")
mcxlab = MCXLabSettingSchema.from_yaml(config_dir / "mcxlab_setting.yaml")
optical = OpticalSettingSchema.from_yaml(config_dir / "optical_setting.yaml")
hardware = HardwareParameterSchema.from_yaml(config_dir / "hardware_parameter.yaml")

# Convert source position from voxels to mm
voxel_size = hardware.get_voxel_size()
src_pos_voxels = mcxlab.srcpos
src_pos_mm = [x * voxel_size for x in src_pos_voxels]
print(f"Source: {src_pos_voxels} voxels = {src_pos_mm} mm")

# Get IJV optical property ranges
ijv_mua_range = optical.tissues.ijv.mua
print(f"IJV mua: [{ijv_mua_range.min}, {ijv_mua_range.max}] 1/mm")

# Get detector SDS values
sds_values = hardware.hardware.detector.get_all_sds()
print(f"Detector SDS: {sds_values} mm")
```

---

## Testing

Run the example script to verify all schemas work correctly:

```bash
# Using uv (recommended)
uv run python examples/load_config_schemas.py

# Using python directly
python examples/load_config_schemas.py
```

Expected output:
- ✅ All configurations load successfully
- ✅ Validation passes
- ✅ Data accessible through type-safe API
- ✅ Unit conversions work correctly

---

## Error Handling

All schemas provide clear validation errors:

```python
try:
    config = MCXLabSettingSchema.from_yaml("invalid.yaml")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

Common validation errors:
- **Missing required fields**: Clear message indicating which field
- **Invalid ranges**: min >= max for optical properties
- **Invalid dataset split**: train + val + test ≠ 1.0
- **File not found**: Volume files, LED profiles, etc.
- **Invalid enums**: srctype, outputtype, etc.

---

## API Reference

### Common Methods

All three schemas share these methods:

```python
# Load from YAML file
config = Schema.from_yaml(yaml_path: Union[str, Path]) -> Schema

# Save to YAML file
config.to_yaml(yaml_path: Union[str, Path]) -> None

# Convert to dictionary
data = config.model_dump(exclude_none=True)

# Convert to JSON
json_str = config.model_dump_json(indent=2)
```

---

## Benefits of Using Schemas

1. **Type Safety**: Catch errors at configuration time, not runtime
2. **Validation**: Automatic validation of all parameters
3. **Documentation**: Self-documenting with field descriptions
4. **IDE Support**: Full autocomplete and type hints
5. **Maintainability**: Easy to update and extend
6. **Testing**: Simple to create test configurations

---

## Future Enhancements

Potential improvements:
- [ ] JSON schema export for external tools
- [ ] Configuration validation CLI tool
- [ ] Configuration diff tool
- [ ] Configuration templates for common scenarios
- [ ] Integration with MCX simulation runner

---

## References

- **MCX Documentation**: https://github.com/fangq/mcx
- **Pydantic v2**: https://docs.pydantic.dev/latest/
- **Project Repository**: https://github.com/ShawnSun1031/IJV-Project

---

**Last Updated**: October 2025
**Version**: 0.2.0
