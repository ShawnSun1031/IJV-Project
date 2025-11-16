# MCX Configuration Loading Guide

This guide explains how to use the `MCXConfig.from_yaml()` method to load MCX simulation configurations from YAML files.

## Overview

The `from_yaml()` class method provides a convenient way to load complete MCX configurations from YAML files with automatic:
- Type validation
- File path resolution (relative to YAML file)
- Numpy array loading
- Optical properties parsing
- Detector configuration parsing

## Basic Usage

```python
from ijv_project.mcx_simulation.schema.mcxlab import MCXConfig

# Load configuration from YAML file
config = MCXConfig.from_yaml("path/to/config.yaml")

# Use with pmcx
pmcx_dict = config.to_pmcx_dict()
```

## YAML File Format

### Required Fields

```yaml
# Number of photons
nphoton: 1000000

# Volume data (see Volume Configuration section)
vol:
  type: "auto_generate"
  dimensions: [60, 60, 60]

# Optical properties
prop:
  - mua: 0.0
    mus: 0.0
    g: 1.0
    n: 1.0

# Time window
tstart: 0.0
tstep: 5.0e-9
tend: 5.0e-9

# Source configuration
srcpos: [30.0, 30.0, 1.0]
srcdir: [0.0, 0.0, 1.0]
```

## Volume Configuration

The `vol` field supports three configuration types:

### 1. Auto-Generate (Simple Homogeneous Volume)

Creates a uniform volume filled with ones:

```yaml
vol:
  type: "auto_generate"
  dimensions: [60, 60, 60]  # [nx, ny, nz]
```

### 2. Load from File

Loads a volume from a `.npy` file:

```yaml
vol:
  type: "file_path"
  file_path: "data/volume.npy"  # Relative or absolute path
```

**Notes:**
- Relative paths are resolved relative to the YAML file location
- Volume should be a 3D numpy array with dtype uint8
- Values represent tissue type indices

### 3. Explicit Values

Define volume directly in YAML (only for small volumes):

```yaml
vol:
  type: "explicit"
  values:
    - [[1, 1], [1, 1]]
    - [[2, 2], [2, 2]]
```

## Optical Properties Configuration

Optical properties can be specified in two formats:

### Dictionary Format (Recommended)

```yaml
prop:
  - mua: 0.0      # Absorption coefficient (1/mm)
    mus: 0.0      # Scattering coefficient (1/mm)
    g: 1.0        # Anisotropy factor
    n: 1.0        # Refractive index
  - mua: 0.005    # Skin
    mus: 1.0
    g: 0.9
    n: 1.37
  - mua: 0.01     # Fat
    mus: 8.0
    g: 0.85
    n: 1.44
```

### List Format (Compact)

```yaml
prop:
  - [0.0, 0.0, 1.0, 1.0]      # [mua, mus, g, n] - Background
  - [0.005, 1.0, 0.9, 1.37]   # Skin
  - [0.01, 8.0, 0.85, 1.44]   # Fat
```

## Detector Configuration

Detectors can also be specified in two formats:

### Dictionary Format (Recommended)

```yaml
detpos:
  - x: 30.0
    y: 20.0
    z: 1.0
    radius: 1.0
  - x: 30.0
    y: 40.0
    z: 1.0
    radius: 1.0
```

### List Format (Compact)

```yaml
detpos:
  - [30.0, 20.0, 1.0, 1.0]  # [x, y, z, radius]
  - [30.0, 40.0, 1.0, 1.0]
```

## Source Configuration

### Basic Source

```yaml
srcpos: [30.0, 30.0, 1.0]  # [x, y, z]
srcdir: [0.0, 0.0, 1.0]    # [vx, vy, vz]
srctype: "pencil"
```

### Source with Parameters

```yaml
srcpos: [30.0, 30.0, 1.0, 5.0]  # [x, y, z, w0] - with beam waist
srcdir: [0.0, 0.0, 1.0, 10.0]   # [vx, vy, vz, focal_length]
srctype: "gaussian"
srcparam1: [0.0, 0.0, 0.0, 0.0]  # Source-specific parameters
```

### Source from File

```yaml
srcpos:
  file_path: "data/source_positions.npy"
```

## Advanced Configuration

### Launch Angle Distribution

Load from file:

```yaml
angleinvcdf:
  file_path: "data/angle_distribution.npy"
```

### GPU Configuration

```yaml
gpuid: 1              # Single GPU (ID 1)
autopilot: 1          # Auto-configure threads
# gpuid: "1011"       # Multiple GPUs (binary string)
# workload: [0.5, 0.5] # Load distribution
```

### Boundary Conditions

```yaml
bc: "aaaaar"  # 6 characters for 6 faces
# a = absorption
# r = reflection
# m = mirror
# c = cyclic
```

### Output Control

```yaml
savedetflag: "DSPXV"  # Detector data flags
issaveexit: true      # Save exit positions
issaveref: true       # Save reflectance
issave2pt: false      # Don't save volumetric output
outputtype: "flux"    # Output type
```

## Complete Example

See [`examples/load_config_from_yaml.py`](../examples/load_config_from_yaml.py) for a complete working example.

```python
from pathlib import Path
from ijv_project.mcx_simulation.schema.mcxlab import MCXConfig
import pmcx

# Load configuration
config = MCXConfig.from_yaml("config/mcxlab_setting.yaml")

# Convert to pmcx format
pmcx_dict = config.to_pmcx_dict()

# Run simulation
result = pmcx.run(pmcx_dict)
```

## Error Handling

The `from_yaml()` method provides clear error messages:

```python
try:
    config = MCXConfig.from_yaml("config.yaml")
except FileNotFoundError as e:
    print(f"Configuration file not found: {e}")
except ValueError as e:
    print(f"Invalid configuration: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Common Errors

**Missing required fields:**
```
ValidationError: Field required [type=missing, input_value={...}, input_type=dict]
```

**Invalid optical properties:**
```
ValueError: Invalid prop format: [0.1, 0.2, 0.3]  # Must have 4 values
```

**Invalid volume type:**
```
ValueError: Invalid vol type: invalid. Must be 'file_path', 'auto_generate', or 'explicit'
```

**File not found:**
```
FileNotFoundError: YAML configuration file not found: config.yaml
```

## Benefits

1. **Type Safety**: Automatic validation using Pydantic
2. **Clear Errors**: Descriptive error messages for invalid configurations
3. **File Management**: Automatic path resolution for relative paths
4. **Flexible Input**: Support for multiple data formats
5. **Documentation**: Self-documenting with YAML comments
6. **Version Control**: Easy to track configuration changes in git

## Template

A complete YAML template is available at:
[`src/ijv_project/mcx_simulation/config/mcxlab_setting.yaml`](../src/ijv_project/mcx_simulation/config/mcxlab_setting.yaml)

## See Also

- [MCX Configuration Schema](config_schemas.md)
- [MCXLab Documentation](https://github.com/fangq/mcx)
- [pmcx Python Package](https://pypi.org/project/pmcx/)
