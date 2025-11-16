"""IJV Project: Non-invasive IJV oxygen saturation measurement.

This package provides tools for:
- Monte Carlo photon transport simulation using pmcx
- Ultrasound image processing for 3D tissue model construction
- Neural network surrogate and prediction models
- In-vivo experiment data processing
"""

__version__ = "0.2.0"
__author__ = "Chin-Hsuan Sun"
__email__ = "dicky10311111@gmail.com"

import sys

from loguru import logger

LOGGER_LEVEL = "DEBUG"

# Remove default handler
logger.remove()
# Configure default logger
logger.add(
    "logs/ijv_project_{time}.log",
    rotation="500 MB",
    retention="10 days",
    level=LOGGER_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
)
# Add a console handler to stderr with default loguru colorful format
logger.add(sys.stderr, level=LOGGER_LEVEL, colorize=True)

__all__ = ["__version__", "__author__", "__email__", "logger"]
