# Simulation Setup Guide

This guide explains how to set up MCX simulations with automatic configuration loading, validation, and hash-based directory naming.

## Overview

The simulation setup system provides:
- **Configuration Loading**: Automatic loading and validation of all configuration files
- **Type Safety**: Pydantic-based validation ensures correctness
- **Hash-Based Naming**: Unique output directories based on configuration content
- **Metadata Tracking**: Automatic metadata generation for reproducibility
- **Caching Support**: Same configurations reuse the same directory

## Quick Start

```python
from pathlib import Path
from ijv_project.mcx_simulation.main import create_simulation_directories

# Create simulation setup
output_dir, loaded_configs = create_simulation_directories(
    subject_id="Subject001",
    config_path=Path("config/"),
    volume_path=Path("data/volume.npy"),
    output_dir=Path("outputs/mcx_simulations/"),
)

# Use the loaded configurations
mcx_config = loaded_configs.mcx_config
volume = loaded_configs.volume_data
hardware = loaded_configs.hardware_config
optical = loaded_configs.optical_config
```

## Required Configuration Files

The system expects these files in the `config_path` directory:

1. **mcxlab_setting.yaml** - MCX simulation parameters
2. **hardware_parameter.yaml** - Hardware configuration (voxel size, source, detector)
3. **optical_setting.yaml** - Optical properties for tissue types
4. **angleinvcdf.csv** - Launch angle distribution for LED source

### File Structure

```
config/
├── mcxlab_setting.yaml      # MCX simulation settings
├── hardware_parameter.yaml  # Hardware configuration
├── optical_setting.yaml     # Optical properties
└── angleinvcdf.csv          # Angle distribution

data/
└── volume.npy               # 3D tissue volume

outputs/
└── mcx_simulations/
    └── Subject001_a1b2c3d4/  # Hash-based unique directory
        ├── metadata/
        │   └── simulation_metadata.json
        └── (simulation outputs)
```

## Configuration Loading Process

The `create_simulation_directories` function performs these steps:

### 1. File Existence Validation

```python
simulation_files = SimulationRelatedFiles(
    angleinvcdf=config_path / "angleinvcdf.csv",
    hardware_parameter=config_path / "hardware_parameter.yaml",
    volume=volume_path,
    mcxlab_setting=config_path / "mcxlab_setting.yaml",
    optical_settings=config_path / "optical_setting.yaml",
)
```

All files are checked for existence using Pydantic validators.

### 2. Configuration Loading & Validation

Each configuration file is loaded with its appropriate schema:

```python
# MCX configuration
mcx_config = MCXConfig.from_yaml(mcxlab_setting.yaml)

# Hardware configuration
hardware_config = HardwareParameterSchema.from_yaml(hardware_parameter.yaml)

# Optical configuration
optical_config = OpticalSettingSchema.from_yaml(optical_setting.yaml)

# Volume data
volume_data = np.load(volume.npy)

# Angle distribution
angleinvcdf_data = np.loadtxt(angleinvcdf.csv)
```

All configurations are validated using Pydantic models, ensuring:
- Required fields are present
- Values are within valid ranges
- Types are correct
- Cross-field constraints are satisfied

### 3. Configuration Hashing

A hash is calculated from all configuration files:

```python
config_hash = calculate_simulation_hash(simulation_files)
# Example output: "a1b2c3d4" (first 8 chars of MD5)
```

**Why hashing?**
- **Uniqueness**: Different configurations get different directories
- **Caching**: Same configurations reuse existing results
- **Reproducibility**: Configuration hash links outputs to exact inputs
- **Safety**: Prevents accidental overwrites of different simulations

### 4. Directory Creation

A unique output directory is created:

```
outputs/mcx_simulations/Subject001_a1b2c3d4/
```

Format: `{subject_id}_{config_hash}`

### 5. Metadata Generation

Simulation metadata is saved in JSON format:

```json
{
  "subject_id": "Subject001",
  "config_hash": "a1b2c3d4",
  "config_path": "/path/to/config",
  "volume_path": "/path/to/volume.npy",
  "nphoton": 1000000,
  "voxel_size": 0.25,
  "volume_shape": [60, 60, 60],
  "num_tissues": 5,
  "tissue_names": ["skin", "fat", "muscle", "ijv", "cca"],
  "source_position": [30.0, 30.0, 1.0],
  "source_direction": [0.0, 0.0, 1.0],
  "gpu_id": 1
}
```

## LoadedSimulationConfig Object

The returned `LoadedSimulationConfig` object contains:

```python
class LoadedSimulationConfig:
    mcx_config: MCXConfig              # MCX simulation parameters
    hardware_config: HardwareParameterSchema  # Hardware configuration
    optical_config: OpticalSettingSchema      # Optical properties
    volume_data: np.ndarray            # 3D volume array
    angleinvcdf_data: np.ndarray       # Angle distribution array
    config_hash: str                   # Configuration hash
```

### Accessing Configuration Data

```python
output_dir, configs = create_simulation_directories(...)

# MCX parameters
nphoton = configs.mcx_config.nphoton
source_pos = configs.mcx_config.srcpos
detector_pos = configs.mcx_config.detpos

# Hardware parameters
voxel_size = configs.hardware_config.hardware.voxel_size
detector_radius = configs.hardware_config.hardware.detector.fibers[0].radius

# Optical properties
skin_mua_range = configs.optical_config.tissues.skin.mua
tissue_names = configs.optical_config.tissues.get_tissue_names()

# Volume and angle data
volume_shape = configs.volume_data.shape
angle_distribution = configs.angleinvcdf_data

# Configuration hash
hash_value = configs.config_hash
```

## Hash Calculation Details

The hash is calculated using MD5 over the binary content of all files:

```python
def calculate_simulation_hash(simulation_files):
    hasher = hashlib.md5()

    # Files are hashed in consistent order
    files = [
        mcxlab_setting.yaml,
        hardware_parameter.yaml,
        optical_setting.yaml,
        angleinvcdf.csv,
        volume.npy,
    ]

    for file in files:
        with open(file, 'rb') as f:
            hasher.update(f.read())

    return hasher.hexdigest()[:8]  # First 8 characters
```

**Important Notes:**
- Any change to any configuration file will produce a different hash
- Volume changes (even single voxel) will produce a different hash
- Hash collisions are extremely unlikely (1 in 4 billion for 8-char hash)
- Full hash is logged for verification

## Error Handling

The system provides clear error messages for common issues:

### Missing Files

```
FileNotFoundError: File not found: config/mcxlab_setting.yaml
```

**Solution**: Ensure all required files exist in the config directory.

### Invalid Configuration

```
ValidationError: Field 'nphoton' must be positive, got -1
```

**Solution**: Check configuration values against schema requirements.

### Volume Loading Error

```
ValueError: Unsupported angleinvcdf file format: .txt
```

**Solution**: Ensure angleinvcdf is in .csv or .npy format.

### Hash Collision Warning

```
Output directory already exists: outputs/Subject001_a1b2c3d4/
This may indicate the simulation was already run with these exact parameters
```

**This is normal** if you're re-running with the same configuration.

## Example Usage

See [`examples/create_simulation_setup.py`](../examples/create_simulation_setup.py) for a complete example.

### Basic Usage

```python
from pathlib import Path
from ijv_project.mcx_simulation.main import create_simulation_directories

# Set up paths
subject_id = "Julie"
config_path = Path("config/julie/")
volume_path = Path("data/julie/volume.npy")
output_dir = Path("outputs/mcx_simulations/")

# Create simulation setup
output_dir, configs = create_simulation_directories(
    subject_id=subject_id,
    config_path=config_path,
    volume_path=volume_path,
    output_dir=output_dir,
)

print(f"Output directory: {output_dir}")
print(f"Configuration hash: {configs.config_hash}")
print(f"Number of photons: {configs.mcx_config.nphoton:,}")
```

### Running MCX Simulation

```python
import pmcx

# Load configurations
output_dir, configs = create_simulation_directories(...)

# Convert MCX config to pmcx format
mcx_dict = configs.mcx_config.to_pmcx_dict()

# Update with loaded volume
mcx_dict['vol'] = configs.volume_data

# Run simulation
result = pmcx.run(mcx_dict)

# Save results
import numpy as np
np.save(output_dir / "fluence.npy", result['flux'])
```

### Multiple Configurations

```python
# Different configurations get different directories
subjects = ["Julie", "Tom", "Sarah"]

for subject in subjects:
    config_path = Path(f"config/{subject}/")
    volume_path = Path(f"data/{subject}/volume.npy")

    output_dir, configs = create_simulation_directories(
        subject_id=subject,
        config_path=config_path,
        volume_path=volume_path,
    )

    print(f"{subject}: {output_dir} (hash: {configs.config_hash})")
```

## Benefits

1. **Type Safety**: Pydantic validation catches configuration errors early
2. **Reproducibility**: Hash links outputs to exact input configuration
3. **Organization**: Automatic directory structure creation
4. **Caching**: Reuse results for identical configurations
5. **Safety**: Prevents accidental overwrites
6. **Traceability**: Metadata tracks all simulation parameters
7. **Flexibility**: Works with any valid MCX configuration

## Best Practices

1. **Version Control**: Keep configuration files in git
2. **Documentation**: Comment your YAML files
3. **Validation**: Run setup before long simulations
4. **Archiving**: Keep metadata with simulation results
5. **Testing**: Use small volumes for testing configurations

## See Also

- [Configuration Loading Guide](config_loading_guide.md)
- [MCX Configuration Schema](config_schemas.md)
- [MCXLab Documentation](https://github.com/fangq/mcx)
