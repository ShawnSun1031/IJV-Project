# IJV Project: Non-invasive Internal Jugular Vein Oxygen Saturation Measurement

[![Python](https://img.shields.io/badge/python-v3.13+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CUDA](https://img.shields.io/badge/cuda-v11.7+-brightgreen.svg)](https://developer.nvidia.com/cuda-toolkit)
[![uv](https://img.shields.io/badge/uv-package_manager-orange.svg)](https://docs.astral.sh/uv/)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://shawnsun1031.github.io/IJV-Project/)

> **Non-invasive measurement of internal jugular vein oxygen saturation using near-infrared spectroscopy and Monte Carlo photon transport simulation**

---

## 🎯 Overview

The IJV Project aims to quantitatively measure changes in internal jugular vein (IJV) oxygen saturation non-invasively using near-infrared spectroscopy (NIRS). The project combines:

- **Monte Carlo Photon Transport Simulation** using GPU-accelerated pmcx
- **Neural Network Surrogate Models** to accelerate simulations
- **Prediction Models** for oxygen saturation changes
- **3D Tissue Modeling** from ultrasound images
- **In-vivo Validation** with real patient data

### Key Features

✨ **Modern Python Stack** (Python 3.13 + uv package manager)
🚀 **GPU-Accelerated** Monte Carlo simulation via pmcx
🔒 **Type-Safe** configuration with Pydantic v2
📊 **Structured Logging** with loguru
📚 **Comprehensive Documentation** with Material theme
🧪 **Well-Tested** code with pytest

---

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Workflows](#-workflows)
- [Documentation](#-documentation)
- [Migration Guide](#-migration-guide)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🚀 Installation

### Prerequisites

- **Python 3.13+** (required)
- **CUDA Toolkit 11.7+** (for GPU acceleration)
- **NVIDIA GPU** (recommended for MCX simulations)
- **uv Package Manager** (recommended) or pip

### Option 1: Using uv (Recommended)

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/ShawnSun1031/IJV-Project.git
cd IJV-Project

# Install dependencies
uv sync

# Or install with all extras (dev + docs)
uv sync --all-extras
```

### Option 2: Using pip

```bash
# Clone the repository
git clone https://github.com/ShawnSun1031/IJV-Project.git
cd IJV-Project

# Create virtual environment
python3.13 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Or with development tools
pip install -e ".[dev,docs]"
```

### Verify Installation

```python
# Test installation
python -c "import pmcx; print(f'pmcx version: {pmcx.__version__}')"
python -c "from ijv_project import __version__; print(f'IJV Project version: {__version__}')"
```

---

## ⚡ Quick Start

### Run a Basic MCX Simulation

```python
from ijv_project.config import MCXConfig, MCXSource
from ijv_project.mcx_simulation import MCXRunner
import numpy as np

# Create simple volume (3-layer tissue model)
volume = np.ones((60, 60, 60), dtype=np.uint8)
volume[:, :, 0:20] = 1   # Skin
volume[:, :, 20:40] = 2  # Fat
volume[:, :, 40:] = 3    # Muscle

# Define optical properties [mua, mus, g, n]
properties = np.array([
    [0.0, 0.0, 1.0, 1.0],      # Background
    [0.02, 10.0, 0.9, 1.37],   # Skin
    [0.005, 8.0, 0.9, 1.44],   # Fat
    [0.015, 12.0, 0.9, 1.37],  # Muscle
])

# Configure source
source = MCXSource(pos=(30.0, 30.0, 0.0), dir=(0.0, 0.0, 1.0))

# Create MCX configuration
config = MCXConfig(
    nphoton=1_000_000,
    vol=volume,
    prop=properties,
    source=source,
)

# Run simulation
runner = MCXRunner(config)
result = runner.run()

print(f"✅ Simulation completed in {result.runtime:.2f}s")
print(f"📊 Flux shape: {result.flux.shape}")
```

### Run Example Scripts

```bash
# Basic MCX simulation example
python examples/basic_mcx_simulation.py

# Output saved to outputs/ directory
```

---

## 📁 Project Structure

```
IJV-Project/
├── src/ijv_project/              # Main package
│   ├── __init__.py                # Package initialization
│   ├── config/                    # Configuration models
│   │   ├── mcx_config.py          # MCX simulation config
│   │   ├── tissue_config.py       # Tissue properties
│   │   └── project_config.py      # Project settings
│   ├── mcx_simulation/            # Monte Carlo simulation
│   │   ├── runner.py              # Simulation runner
│   │   └── utils.py               # Analysis utilities
│   ├── models/                    # Neural network models
│   ├── ultrasound_processing/     # Image processing
│   └── utils/                     # General utilities
├── examples/                      # Example scripts
│   └── basic_mcx_simulation.py
├── tests/                         # Unit tests
├── docs/                          # Documentation
│   ├── migration/                 # Migration guides
│   ├── mcx_simulation/            # MCX documentation
│   └── ...
├── legacy/                        # Legacy code (v0.1)
│   ├── mcx_sim/                   # Original MCX scripts
│   ├── prediction_model/          # Original models
│   └── surrogate_model/
├── pyproject.toml                 # Project configuration
├── uv.lock                        # Dependency lock
├── CLAUDE.md                      # Claude Code guidance
├── REFACTORING_SUMMARY.md         # Refactoring details
└── README.md                      # This file
```

---

## 🔄 Workflows

### 1. Ultrasound Image Processing

Process ultrasound images to create 3D tissue models:

```python
from ijv_project.ultrasound_processing import process_ultrasound_images

# Process images (coming soon in v0.2.1)
model_3d = process_ultrasound_images(
    subject="Julie",
    date="20231012",
    ijv_type="ijv_large",
)
```

### 2. MCX Simulation

Run Monte Carlo photon transport simulations:

```python
from ijv_project.mcx_simulation import MCXRunner

# With CV stopping criterion
result = runner.run_with_cv_criterion(
    cv_threshold=2.5,
    repeat_times=10,
    save_path="results/simulation.npz",
)
```

### 3. Surrogate Model Training

Train neural networks to accelerate simulations:

```python
# Coming in v0.2.1
from ijv_project.models import train_surrogate_model

model = train_surrogate_model(
    training_data="data/train/",
    model_config=config,
)
```

### 4. Prediction Model

Predict oxygen saturation changes:

```python
# Coming in v0.2.1
from ijv_project.models import PredictionModel

model = PredictionModel.load("models/prediction/best_model.pt")
prediction = model.predict(spectral_features)
```

### 5. In-vivo Experiments

Process and analyze real experimental data:

```python
# Coming in v0.2.1
from ijv_project.in_vivo import process_experiment_data

results = process_experiment_data(
    subject="Julie",
    experiment_date="20231015",
)
```

---

## 📚 Documentation

**Full documentation**: [https://shawnsun1031.github.io/IJV-Project/](https://shawnsun1031.github.io/IJV-Project/)

### Key Documentation Pages

- **[Installation Guide](docs/installation.md)** - Detailed setup instructions
- **[Quick Start](docs/quick_start.md)** - Get started quickly
- **[MCX Simulation](docs/mcx_simulation/overview.md)** - Monte Carlo simulation guide
- **[API Reference](docs/api/)** - Complete API documentation
- **[Migration Guide](docs/migration/v0.1_to_v0.2.md)** - Upgrade from v0.1

### Build Documentation Locally

```bash
# Install docs dependencies
uv sync --extra docs

# Serve documentation (with hot reload)
mkdocs serve

# Open browser to http://127.0.0.1:8000
```

---

## 🔄 Migration Guide

### Upgrading from v0.1 to v0.2

**Key Changes:**
- ✅ **No more binary MCX compilation** - Use `pmcx` Python library
- ✅ **Type-safe configuration** - Pydantic models with validation
- ✅ **Modern logging** - Structured logging with loguru
- ✅ **Python 3.13** - Latest Python features

**Quick Migration Steps:**

```bash
# 1. Update Python
python --version  # Should be 3.13+

# 2. Install new dependencies
uv sync

# 3. Update import statements
# OLD:
from mcx_sim.utils import calculate_R
# NEW:
from ijv_project.mcx_simulation import calculate_diffuse_reflectance

# 4. Update configuration
# OLD: Dictionary-based
config = {"nphoton": 1000000, ...}
# NEW: Pydantic model
config = MCXConfig(nphoton=1000000, ...)
```

**Full Migration Guide**: [docs/migration/v0.1_to_v0.2.md](docs/migration/v0.1_to_v0.2.md)

---

## 🎓 Scientific Background

### Methodology

1. **Dual-Channel NIRS System**
   - Short channel: 10mm source-detector separation
   - Long channel: 20mm source-detector separation
   - 20 wavelengths (700-850nm)

2. **3D Tissue Model**
   - Constructed from ultrasound images
   - 5 tissue types: skin, fat, muscle, IJV, CCA
   - Wavelength-dependent optical properties

3. **Surrogate Model**
   - Neural network acceleration of MC simulation
   - ~1000x speedup vs traditional Monte Carlo
   - Input: Optical properties → Output: Diffuse reflectance

4. **Prediction Model**
   - Input: Spectral features (modified Beer-Lambert)
   - Output: IJV oxygen saturation changes (ΔStO₂)
   - RMSE < 1.5% in simulations

### Performance

- **Simulation**: <1% CV with adaptive stopping
- **Surrogate Model**: >99% correlation with MC
- **Prediction Model**: <1.5% RMSE on test data
- **In-vivo Validation**: Consistent with physiology

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/development/contributing.md) for guidelines.

### Development Setup

```bash
# Install with development tools
uv sync --extra dev

# Run tests
pytest

# Run linter
ruff check src/

# Format code
ruff format src/

# Type check
mypy src/ijv_project/
```

### Code Style

- **Format**: Ruff formatter (line length: 100)
- **Docstrings**: Google style
- **Type Hints**: Required for all functions
- **Testing**: pytest with >80% coverage goal

---

## 📝 Citation

If you use this project in your research, please cite:

```bibtex
@mastersthesis{sun2023ijv,
  author  = {Chin-Hsuan Sun},
  title   = {Non-invasive Measurement of Internal Jugular Vein Oxygen Saturation},
  school  = {National Taiwan University},
  year    = {2023},
  type    = {Master's Thesis},
}
```

---

## 📧 Contact

- **Author**: Chin-Hsuan Sun
- **Email**: dicky10311111@gmail.com
- **GitHub**: [@ShawnSun1031](https://github.com/ShawnSun1031)
- **Website**: [https://shawnsun1031.github.io/](https://shawnsun1031.github.io/)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **MCX Project**: [fangq/mcx](https://github.com/fangq/mcx) - Monte Carlo eXtreme
- **pmcx**: Python bindings for MCX
- **Research Group**: BOSI Lab, National Taiwan University
- **Funding**: [Add funding sources if applicable]

---

## 🗂️ Legacy Documentation

For users of v0.1, legacy documentation is preserved in:
- Original scripts: `legacy/` directory
- Old README: See git history
- Handover docs: `docs/handover/`

---

**Last Updated**: January 2025
**Version**: 0.2.0
**Status**: 🚧 Active Development
