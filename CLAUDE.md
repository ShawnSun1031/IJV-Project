# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Internal Jugular Vein (IJV) Project - a research project for non-invasively measuring internal jugular vein oxygen saturation changes using near-infrared spectroscopy. The project combines Monte Carlo photon transport simulation with neural network-based surrogate and prediction models.

**Version**: 0.2.0 (Refactored with modern Python practices)

**Key Technologies:**
- Python 3.13+ with PyTorch for neural networks
- CUDA 11.7+ for GPU-accelerated Monte Carlo simulation
- pmcx (Python MCX) for photon transport simulation - NO BINARY COMPILATION REQUIRED
- Pydantic v2 for type-safe configuration
- loguru for structured logging
- uv for fast package management

## Environment Requirements

**Modern Setup (v0.2+):**
1. Python 3.13+ installed
2. CUDA toolkit 11.7+ installed
3. uv package manager (recommended) or pip
4. No binary compilation required - pmcx handles everything

**Installation:**
```bash
# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .

# With all extras (dev + docs)
uv sync --all-extras
```

## Project Structure (v0.2)

The refactored project uses a modern src-layout:

```
IJV-Project/
├── src/ijv_project/              # Main package
│   ├── __init__.py                # Package init with logging
│   ├── config/                    # Pydantic configuration models
│   │   ├── mcx_config.py          # MCX simulation configuration
│   │   ├── tissue_config.py       # Tissue optical properties
│   │   └── project_config.py      # Project-wide settings
│   ├── mcx_simulation/            # pmcx-based simulation
│   │   ├── runner.py              # MCXRunner class
│   │   └── utils.py               # Analysis utilities
│   ├── models/                    # Neural network models (TODO)
│   ├── ultrasound_processing/     # Image processing (TODO)
│   └── utils/                     # General utilities
├── examples/                      # Example scripts
│   └── basic_mcx_simulation.py
├── tests/                         # Unit tests
├── docs/                          # Documentation
│   ├── migration/                 # Migration guides
│   └── ...
├── legacy/                        # Old code (v0.1)
│   ├── mcx_sim/                   # Original shell-based MCX
│   ├── prediction_model/          # Original models
│   └── surrogate_model/
├── pyproject.toml                 # Modern Python config
└── uv.lock                        # Dependency lock file
```

## Modern Development Workflow

### 1. MCX Simulation (New in v0.2)

**Use pmcx Python library instead of binary MCX:**

```python
from ijv_project.config import MCXConfig, MCXSource
from ijv_project.mcx_simulation import MCXRunner
import numpy as np

# Create configuration with type-safe Pydantic models
source = MCXSource(
    pos=(30.0, 30.0, 0.0),
    dir=(0.0, 0.0, 1.0),
)

config = MCXConfig(
    nphoton=1_000_000,
    vol=volume_array,
    prop=properties_array,
    source=source,
)

# Run simulation
runner = MCXRunner(config)
result = runner.run()

# Or with CV criterion
result = runner.run_with_cv_criterion(
    cv_threshold=2.5,
    repeat_times=10,
)
```

**Key Benefits:**
- ✅ No binary compilation required
- ✅ Type-safe configuration with validation
- ✅ Clean Python API
- ✅ Automatic error handling
- ✅ Structured logging

### 2. Configuration with Pydantic

All configuration is now type-safe using Pydantic models:

```python
from ijv_project.config import SubjectConfig, ProjectConfig

# Validated configuration
subject = SubjectConfig(
    name="Julie",
    ultrasound_date="20231012",  # Auto-validated as YYYYMMDD
    voxel_size=0.25,  # Type-checked as positive float
)

# Project-wide config (loads from .env)
config = ProjectConfig()
data_dir = config.get_subject_data_dir("Julie", "train")
```

### 3. Structured Logging

All modules use loguru for consistent, structured logging:

```python
from loguru import logger

logger.info("Starting simulation")
logger.success("Simulation completed!")
logger.warning("CV threshold not met")
logger.error(f"Failed: {error}")

# Logs automatically saved to logs/ with rotation
```

## Common Development Commands

### Run MCX Simulation (New Method)
```bash
# Run the basic example
python examples/basic_mcx_simulation.py

# Output saved to outputs/
```

### Run Legacy MCX Simulation (Old Method)
```bash
# Still available for backward compatibility
cd legacy/mcx_sim
bash Run_MCX_Sim.sh
```

### Code Quality
```bash
# Lint with ruff
ruff check src/

# Format code
ruff format src/

# Type check
mypy src/ijv_project/

# Run tests
pytest

# Run tests with coverage
pytest --cov=src/ijv_project
```

### Documentation
```bash
# Serve docs locally (with hot reload)
mkdocs serve

# Build static site
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

## Key Architectural Concepts

### Type-Safe Configuration

All configuration uses Pydantic models with automatic validation:

- `MCXConfig`: Complete MCX simulation configuration
- `TissueConfig`: Tissue optical properties and metadata
- `SubjectConfig`: Per-subject configuration
- `ProjectConfig`: Project-wide settings (loads from .env)

**Example validation:**
```python
# This will raise ValidationError:
bad_config = SubjectConfig(
    name="",  # ❌ Empty string not allowed
    ultrasound_date="2023-10-12",  # ❌ Wrong format (needs YYYYMMDD)
    voxel_size=-0.1,  # ❌ Must be positive
)
```

### MCX Simulation Architecture

**New (v0.2):** pmcx Python library
- No binary compilation
- Direct Python API
- Type-safe configuration
- Automatic error handling

**Old (v0.1):** Binary MCX + shell scripts
- Required compilation
- JSON config files
- Subprocess calls
- Manual error parsing

### Tissue Model Structure

The 3D numerical model represents five tissue types:
- **Background** (label 0)
- **Skin** (label 1)
- **Fat** (label 2)
- **Muscle** (label 3)
- **IJV** (label 4) - Internal Jugular Vein (target vessel)
- **CCA** (label 5) - Common Carotid Artery

Each tissue has wavelength-dependent optical properties (μₐ, μₛ, g, n).

### Dual-Channel Measurement System

- **Short channel**: 10mm source-detector separation (reduces superficial tissue)
- **Long channel**: 20mm source-detector separation (captures IJV signal)
- **20 wavelengths**: 700-850nm range

### Neural Network Models

#### Surrogate Model
- **Purpose**: Accelerate MC simulations (~1000x speedup)
- **Architecture**: 10 → 256 → 256 → 128 → 128 → 2
- **Input**: Optical properties (5 tissues × 2 params)
- **Output**: Diffuse reflectance (2 channels)

#### Prediction Model
- **Purpose**: Predict IJV oxygen saturation changes
- **Architecture**: 81 → 256 → 128 → 64 → 32 → 1
- **Input**: Spectral features (modified Beer-Lambert)
- **Output**: ΔStO₂ (oxygen saturation change)
- **Performance**: <1.5% RMSE

## Analysis Utilities

New utility functions in `src/ijv_project/mcx_simulation/utils.py`:

```python
from ijv_project.mcx_simulation import (
    calculate_diffuse_reflectance,
    calculate_mean_pathlength,
    calculate_mean_scattering,
)

# Calculate reflectance
R = calculate_diffuse_reflectance(
    det_photon=result.det_photon,
    detector_area=np.pi * radius**2,
    nphoton=config.nphoton,
)

# Get path lengths by tissue
path_lengths = calculate_mean_pathlength(
    det_photon=result.det_photon,
    tissue_labels=["skin", "fat", "muscle", "ijv", "cca"],
)
```

## Dataset Organization

```
data/  # New unified data directory
├── <subject>/
│   ├── train/
│   │   ├── ijv_large/
│   │   └── ijv_small/
│   ├── test/
│   │   ├── ijv_large/
│   │   └── ijv_small/
│   └── SDS[1|2]/<date>/  # In-vivo raw data
└── phantom_simulated/

models/  # New model directory
├── surrogate/
│   └── <subject>/
└── prediction/
    └── <experiment_name>/
        └── <subject>/

logs/  # Automatic logging directory
└── ijv_project_<timestamp>.log
```

## Testing

### Unit Tests (New in v0.2)
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/ijv_project --cov-report=html

# Run specific test
pytest tests/test_mcx_simulation.py -v
```

### Legacy Validation
- CV (Coefficient of Variation) analysis in simulations
- RMSE evaluation of models
- Nested k-fold cross-validation
- In-vivo experiment comparison

## Migration from v0.1

If working with old code, see:
- **Migration Guide**: `docs/migration/v0.1_to_v0.2.md`
- **Refactoring Summary**: `REFACTORING_SUMMARY.md`
- **Old Code**: Preserved in `legacy/` directory

**Quick Migration:**
1. Install Python 3.13 and uv
2. Run `uv sync`
3. Update imports from `legacy/` to `src/ijv_project/`
4. Replace dictionary configs with Pydantic models
5. Replace binary MCX calls with pmcx

## Code Style Guidelines

All new code must follow:

1. **Type Hints**: Required for all functions
```python
def calculate_something(x: float, y: int) -> tuple[float, str]:
    """Calculate something with full type hints."""
    ...
```

2. **Google-Style Docstrings**: Required
```python
def function(arg1: str, arg2: int) -> bool:
    """Brief description.

    Longer description if needed.

    Args:
        arg1: Description of arg1.
        arg2: Description of arg2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When something goes wrong.
    """
    ...
```

3. **Pydantic for Config**: Use models, not dictionaries
4. **loguru for Logging**: Use logger, not print()
5. **Ruff for Formatting**: Line length 100, Python 3.13

## Documentation

- **Main Site**: https://shawnsun1031.github.io/IJV-Project/
- **Theme**: Material for MkDocs with dark/light mode
- **Features**: Search, navigation tabs, code highlighting, math support
- **Source**: `docs/` directory
- **Config**: `mkdocs.yml`

## Performance Notes

### pmcx vs Binary MCX

| Aspect | Binary MCX | pmcx |
|--------|------------|------|
| Setup | Compile required | pip/uv install |
| Interface | JSON + subprocess | Python API |
| Type Safety | None | Full validation |
| Error Handling | Parse stderr | Python exceptions |
| GPU Performance | Fast | Equivalent (same kernel) |
| Development | Slow (recompile) | Fast (immediate) |

### Optimization Tips

1. **Use CV Criterion**: Stop when variance is low
2. **Batch Processing**: Run multiple wavelengths in parallel
3. **GPU Selection**: Use `gpu_id` parameter for specific GPU
4. **Adaptive Photons**: Start with fewer photons, increase if needed

## Related Resources

- **MCX Documentation**: https://github.com/fangq/mcx
- **pmcx PyPI**: https://pypi.org/project/pmcx/
- **MCX User Group**: https://groups.google.com/g/mcx-users
- **MCX Cloud Visualization**: https://mcx.space/cloud/#
- **Master Thesis**: NAS:Data/BOSI Lab/Thesis/R10 (for detailed theory)

## Future Development (v0.2.x)

### Planned Features

1. **Complete Model Migration**
   - Migrate neural network models to `src/ijv_project/models/`
   - Add type hints and docstrings
   - Create training pipelines

2. **Ultrasound Processing**
   - Modernize image processing code
   - Add configuration models
   - Improve 3D visualization

3. **Testing & CI/CD**
   - Comprehensive unit tests (>80% coverage)
   - Integration tests
   - GitHub Actions CI/CD

4. **Documentation**
   - Complete API reference
   - Tutorial notebooks
   - Video guides

5. **Performance**
   - Multi-GPU support
   - Distributed training
   - Real-time processing

## Contact & Support

- **Author**: Chin-Hsuan Sun
- **Email**: dicky10311111@gmail.com
- **GitHub**: https://github.com/ShawnSun1031/IJV-Project
- **Issues**: https://github.com/ShawnSun1031/IJV-Project/issues

---

**Last Updated**: January 2025
**Version**: 0.2.0
**Status**: 🚧 Active Development (Core modules refactored, legacy code preserved)
