import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ijv_project.mcx_simulation.mcx_runner import MCXRunner, NaFilterMap
from ijv_project.mcx_simulation.schema import MCXConfig
from ijv_project.mcx_simulation.schema.mcxlab import DetectorPosition, OpticalProperties


# create config fixture
@pytest.fixture
def config() -> MCXConfig:
	vol = np.ones((60, 60, 60), dtype=np.uint8)
	vol[20:40, 30:40, 0:30] = 2  # add a layer with different optical properties
	config = MCXConfig(
		nphoton=1000,
		vol=vol,
		prop=[
			OpticalProperties(mua=0, mus=0, g=1, n=1),
			OpticalProperties(mua=1.005, mus=100, g=0, n=1.37),
			OpticalProperties(mua=2.1, mus=1000, g=0.9, n=1),
		],
		tstart=0,
		tend=1e-9,
		tstep=1e-9,
		srcpos=[30, 30, 1],
		srcdir=[0, 0, 1],
		savedetflag='dspxv',
		issave2pt=False,
		detpos=[
			DetectorPosition(
				x=28,
				y=32,
				z=0,
				radius=1,
			),
			DetectorPosition(
				x=30,
				y=29,
				z=0,
				radius=1,
			),
		],
	)
	return config


@pytest.fixture
def sds_detid_map() -> dict[str, list[int]]:
	return {
		'1.0': [1],
		'2.0': [2],
	}


def test_run_single_simulation(config, temp_test_dir):
	runner = MCXRunner(config, save_dir=temp_test_dir)
	result = runner._single_run()
	print(f'Simulation completed in {result.runtime:.2f}s')


def test_run_multiple_simulations(config, temp_test_dir):
	runner = MCXRunner(config, save_dir=temp_test_dir)
	runner.run(5)
	print('Multiple simulations completed.')


def test_calculate_cwd_ref_cv(config, sds_detid_map, temp_test_dir: Path):
	# create dummy output for multiple iteration test
	root = temp_test_dir / 'mcx_output/test_simulation_multi/cwd_ref'
	root.mkdir(parents=True, exist_ok=True)
	for i in range(1000):
		(root / f'iteration_{i + 1:04d}').mkdir(parents=True, exist_ok=True)
		pd.DataFrame(
			{
				'detid': list(range(1, 127)),
				'cwd_ref': np.random.rand(126),
			}
		).to_csv(
			root / f'iteration_{i + 1:04d}/cwd_ref_detector.csv',
			index=False,
		)
	# Run multiple simulations
	runner = MCXRunner(config, sds_detid_map, save_dir=root)
	t1 = time.time()
	calculate_cwd_ref_cv = runner.calculate_cwd_ref_cv()
	t2 = time.time()
	print(calculate_cwd_ref_cv)
	print(f'Simulation completed in {t2 - t1:.2f}s')


def test_run_multiple_simulations_resume(config, temp_test_dir):
	runner = MCXRunner(config, save_dir=temp_test_dir)
	# First run 3 iterations
	runner.run(3)
	# Now resume and run 2 more iterations
	runner.run(
		5,
	)
	print('Resumed multiple simulations completed.')


def test_run_multiple_simulations_with_cv_threshold(config, sds_detid_map, temp_test_dir):
	runner = MCXRunner(config, sds_detid_map, save_dir=temp_test_dir)
	# Run multiple iterations with CV threshold
	runner.run(
		n_iterations=3,
		# save_dir=temp_test_dir / "mcx_output/test_simulation_cv_threshold",
		cv_threshold=70.0,  # 70% CV threshold
	)
	print('Multiple simulations with CV threshold completed.')


def test_real_config_multiple_simulations(temp_test_dir):
	config = MCXConfig.from_yaml(
		'/home/dicky1031/project/test-claude-code/IJV-Project/src/ijv_project/mcx_simulation/mcx_output/example_subject_1_e4905d1f/ijv_large/train/sim_0000/mcxlab_setting.yaml'
	)
	sds_detid_map = json.load(
		open(
			'/home/dicky1031/project/test-claude-code/IJV-Project/src/ijv_project/mcx_simulation/mcx_output/example_subject_1_e4905d1f/metadata/ijv_sds_detid_map.json'
		)
	)
	config.nphoton = 100000  # reduce photon for test speed
	runner = MCXRunner(config, sds_detid_map, save_dir=temp_test_dir)
	runner.run(
		n_iterations=3,
		cv_threshold=20.0,  # 20% CV threshold
	)
	print('Real config multiple simulations with CV threshold completed.')


def test_real_config_merge_cwd_ref(temp_test_dir):
	# test poisson distribution based merging and CV calculation
	config = MCXConfig.from_yaml(
		'/home/dicky1031/project/test-claude-code/IJV-Project/src/ijv_project/mcx_simulation/mcx_output/example_subject_1_e4905d1f/ijv_large/train/sim_0000/mcxlab_setting.yaml'
	)
	sds_detid_map = json.load(
		open(
			'/home/dicky1031/project/test-claude-code/IJV-Project/src/ijv_project/mcx_simulation/mcx_output/example_subject_1_e4905d1f/metadata/ijv_sds_detid_map.json'
		)
	)
	config.nphoton = 10000000  # reduce photon for test speed
	runner = MCXRunner(config, sds_detid_map, save_dir=temp_test_dir)
	runner.run(
		n_iterations=20,
		# save_dir=temp_test_dir,
		# cv_threshold=30.0,  # 30% CV threshold
	)
	runner.merge_per_n_iterations_cwd_ref(
		per_n_iterations=5,
	)
	runner.calculate_cwd_ref_cv(
		detector_path_pattern='merge/iteration_*/cwd_ref_detector.csv',
		sds_path_pattern='merge/iteration_*/cwd_ref_sds.csv',
	)
	print('Real config merge cwd_ref completed.')


def test_na_filtering_in_mcx_runner(config, sds_detid_map, temp_test_dir):
	na_value: NaFilterMap = {
		'na': 0.5,
		'refraction_index_0': 1.0,
		'refraction_index_1': 1.37,
	}

	runner = MCXRunner(config, sds_detid_map, save_dir=temp_test_dir, na=na_value)
	result = runner._single_run()

	# Check if the detector photon data has been filtered based on NA
	detp = result.det_photon
	if detp is not None and detp['v'] is not None:
		# Calculate the angles for each detected photon
		cz = detp['v'][:, 2]  # z-component of direction
		after_refraction_theta_z = np.arccos(cz)
		sin_theta = (
			np.sin(after_refraction_theta_z)
			* na_value['refraction_index_0']
			/ na_value['refraction_index_1']
		)
		na_values = na_value['refraction_index_1'] * sin_theta  # NA = n * sin(theta)

		# Verify that all detected photons have NA less than or equal to the specified NA value
		assert np.all(na_values <= na_value['na']), (
			'Some detected photons exceed the specified NA value.'
		)

	print('NA filtering in MCXRunner test completed.')
