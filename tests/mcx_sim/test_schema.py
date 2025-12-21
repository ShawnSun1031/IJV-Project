# mypy: ignore-errors
from pathlib import Path

import pandas as pd
from loguru import logger

from ijv_project.mcx_simulation.schema.hardware_parameter import HardwareParameterSchema
from ijv_project.mcx_simulation.schema.mcxlab import create_example_config
from ijv_project.mcx_simulation.schema.optical_setting import OpticalSettingSchema


def test_mcxlab_schema():
    # Test the configuration schema
    try:
        config = create_example_config()
        logger.success("MCXLab configuration schema validation passed!")
        logger.info(f"Configuration created with {config.nphoton} photons")
        logger.info(f"Volume type: {type(config.vol)}")
        if config.prop is not None:
            logger.info(f"Number of media types: {len(config.prop)}")
        logger.info(f"Number of detectors: {len(config.detpos) if config.detpos else 0}")
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")


def test_hardware_schema():
    config_path = Path(__file__).parent / "hardware_parameter.yaml"
    if config_path.exists():
        try:
            config = HardwareParameterSchema.from_yaml(config_path)

            logger.info(f"Voxel size: {config.get_voxel_size()} mm/voxel")

            logger.info("\nSource configuration:")
            src_summary = config.get_source_summary()
            logger.info(f"  Holder size: {src_summary['holder_size']} mm")
            logger.info(f"  Window radius: {src_summary['window_radius']} mm")
            logger.info(f"  LED size: {src_summary['led_size']} mm")
            logger.info(f"  LED to window: {src_summary['led_to_window_distance']} mm")

            logger.info("\nDetector configuration:")
            det_summary = config.get_detector_summary()
            logger.info(f"  Number of fibers: {det_summary['num_fibers']}")
            logger.info(f"  SDS values: {det_summary['sds_values']} mm")
            logger.info(f"  Fiber radii: {det_summary['fiber_radii']} mm")

            # Example unit conversion
            logger.info("\nUnit conversion examples:")
            logger.info(
                f"  10mm = {config.hardware.mm_to_voxels(10):.2f} voxels "
                f"(voxel_size={config.get_voxel_size()}mm)"
            )
            logger.info(
                f"  40 voxels = {config.hardware.voxels_to_mm(40):.2f} mm "
                f"(voxel_size={config.get_voxel_size()}mm)"
            )

        except Exception as e:
            logger.error(f"Failed to load config: {e}")
    else:
        logger.warning(f"Config file not found: {config_path}")


def test_optical_setting_schema():
    config_path = Path(__file__).parent.parent / "config" / "ijv_large_optical_setting.yaml"
    if config_path.exists():
        try:
            config = OpticalSettingSchema.from_yaml(config_path)

            logger.info("Dataset split:")
            logger.info(f"  Val:   {config.dataset.val:.1%}")
            logger.info(f"  Test:  {config.dataset.test:.1%}")

            logger.info("\nOptical property ranges (mua):")
            for tissue, (min_val, max_val) in config.mua_range_summary.items():
                logger.info(f"  {tissue:8s}: [{min_val:.4f}, {max_val:.4f}] 1/mm")

            logger.info("\nOptical property ranges (mus):")
            for tissue, (min_val, max_val) in config.mus_range_summary.items():
                logger.info(f"  {tissue:8s}: [{min_val:.4f}, {max_val:.4f}] 1/mm")

            total_combos = config.total_mua_combinations * config.total_mus_combinations
            logger.info(f"\nTotal combinations: {total_combos}")

            mus_dataset = config.mus_dataset
            mua_dataset = config.mua_dataset
            logger.info(
                f"  Mus train/val/test: {mus_dataset['train'].shape[0]}/"
                f"{mus_dataset['val'].shape[0]}/{mus_dataset['test'].shape[0]}"
            )
            logger.info(
                f"  Mua train/val/test: {mua_dataset['train'].shape[0]}/"
                f"{mua_dataset['val'].shape[0]}/{mua_dataset['test'].shape[0]}"
            )

            # save datasets to CSV for inspection
            output_dir = Path(__file__).parent / "config" / "generated_datasets"
            output_dir.mkdir(parents=True, exist_ok=True)
            pd.DataFrame(
                mus_dataset["train"],
                columns=[f"mus_{tissue_name}" for tissue_name in config.tissues.get_tissue_names()],
            ).to_csv(output_dir / "mus_train.csv", index=False)
            pd.DataFrame(
                mus_dataset["val"],
                columns=[f"mus_{tissue_name}" for tissue_name in config.tissues.get_tissue_names()],
            ).to_csv(output_dir / "mus_val.csv", index=False)
            pd.DataFrame(
                mus_dataset["test"],
                columns=[f"mus_{tissue_name}" for tissue_name in config.tissues.get_tissue_names()],
            ).to_csv(output_dir / "mus_test.csv", index=False)
            pd.DataFrame(
                mua_dataset["train"],
                columns=[f"mua_{tissue_name}" for tissue_name in config.tissues.get_tissue_names()],
            ).to_csv(output_dir / "mua_train.csv", index=False)
            pd.DataFrame(
                mua_dataset["val"],
                columns=[f"mua_{tissue_name}" for tissue_name in config.tissues.get_tissue_names()],
            ).to_csv(output_dir / "mua_val.csv", index=False)
            pd.DataFrame(
                mua_dataset["test"],
                columns=[f"mua_{tissue_name}" for tissue_name in config.tissues.get_tissue_names()],
            ).to_csv(output_dir / "mua_test.csv", index=False)
            logger.success(f"\nGenerated datasets saved to: {output_dir}")

        except Exception as e:
            logger.error(f"Failed to load config: {e}")
    else:
        logger.warning(f"Config file not found: {config_path}")
