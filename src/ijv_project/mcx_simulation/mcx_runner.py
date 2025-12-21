"""MCX simulation runner using pmcx library.

This module provides the main interface for running Monte Carlo simulations
using the pmcx Python library.
"""

import io
import pickle
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict

import numpy as np
import pandas as pd

from ijv_project import logger
from ijv_project.utils.mcx2preview import mcx2preview_json

try:
	import pmcx  # type: ignore[import-untyped]
	from pmcx.utils import detweight, meanpath, meanscat  # type: ignore[import-untyped]

	from ijv_project.utils.ijv_pmcx import cwdref
except ImportError:
	logger.error('pmcx library not found. Install with: uv add pmcx')
	raise

from ijv_project.mcx_simulation.schema import MCXConfig


class DetectPhoton(TypedDict):
	"""Detected photon data structure."""

	detid: np.ndarray
	srcid: np.ndarray | None
	nscat: np.ndarray | None
	ppath: np.ndarray | None
	mom: np.ndarray | None
	p: np.ndarray | None
	v: np.ndarray | None
	w0: np.ndarray | None
	s: np.ndarray | None
	prop: np.ndarray | None
	unitinmm: float | None
	data: np.ndarray | None


class NaFilterMap(TypedDict):
	"""Numerical aperture filter mapping structure."""

	na: float
	refraction_index_0: float
	refraction_index_1: float


@dataclass
class DetectPhotonResults:
	"""Results from detected photon data analysis."""

	det_photon: DetectPhoton
	det_weight: np.ndarray | None
	mean_path: np.ndarray | None
	mean_scat: np.ndarray | None
	cwd_ref: np.ndarray | None


@dataclass
class SimulationResult:
	"""Results from MCX simulation.

	Attributes:
	   fluence: a struct array, with a length equals to that of cfg.
	         For each element of fluence,
	         fluence(i).data is a 4D array with
	              dimensions specified by [size(vol) total-time-gates].
	              The content of the array is the normalized fluence at
	              each voxel of each time-gate.

	              when cfg.debuglevel contains 'T', fluence(i).data stores trajectory
	              output, see below
	         fluence(i).dref is a 4D array with the same dimension as fluence(i).data
	              if cfg.issaveref is set to 1, containing only non-zero values in the
	              layer of voxels immediately next to the non-zero voxels in cfg.vol,
	              storing the normalized total diffuse reflectance (summation of the weights
	              of all escaped photon to the background regardless of their direction);
	              it is an empty array [] when if cfg.issaveref is 0.
	         fluence(i).stat is a structure storing additional information, including
	              runtime: total simulation run-time in millisecond
	              nphoton: total simulated photon number
	              energytot: total initial weight/energy of all launched photons
	              energyabs: total absorbed weight/energy of all photons
	              normalizer: normalization factor
	              unitinmm: same as cfg.unitinmm, voxel edge-length in mm

	   detphoton: (optional) a struct array, with a length equals to that of cfg.
	         Starting from v2018, the detphoton contains the below subfields:
	           detphoton.detid: the ID(>0) of the detector that captures the photon
	           detphoton.srcid: the ID(>0) of the source in a multi-source simulation
	           detphoton.nscat: cummulative scattering event counts in each medium
	           detphoton.ppath: cummulative path lengths in each medium (partial pathlength)
	                one need to multiply cfg.unitinmm with ppath to convert it to mm.
	           detphoton.mom: cummulative cos_theta for momentum transfer in each medium
	           detphoton.p or .v: exit position and direction, when cfg.issaveexit=1
	           detphoton.w0: photon initial weight at launch time
	           detphoton.s: exit Stokes parameters for polarized photon
	           detphoton.prop: optical properties, a copy of cfg.prop
	           detphoton.data: a concatenated and transposed array in the order of
	                 [detid nscat ppath mom p v w0]'
	           "data" is the is the only subfield in all mcxlab before 2018

	   vol: (optional) a struct array, each element is a preprocessed volume
	         corresponding to each instance of cfg. Each volume is a 3D int32 array.
	   seeds: (optional), if give, mcxlab returns the seeds, in the form of
	         a byte array (uint8) for each detected photon. The column number
	         of seed equals that of detphoton.
	   trajectory: (optional), if given, mcxlab returns the trajectory data for
	         each simulated photon. The output has 6 rows, the meanings are
	            id:  1:    index of the photon packet
	            pos: 2-4:  x/y/z/ of each trajectory position
	                 5:    current photon packet weight
	          srcid: 6:    source ID (>0) of the photon
	          iquv:  7-10: Stokes IQUV vector (>0) of the photon
	         By default, mcxlab only records the first 1e7 positions along all
	         simulated photons; change cfg.maxjumpdebug to define a different limit.
	"""

	flux: np.ndarray | None = None
	det_photon: DetectPhoton | None = None
	volume: np.ndarray | None = None
	seeds: np.ndarray | None = None
	trajectory: np.ndarray | None = None
	runtime: float = 0.0
	nphoton: int = 0

	def save(self, output_dir: Path, cfg: dict, sds_detid_map: dict | None = None) -> None:
		"""Save simulation results to file.

		Args:
		    output_dir: Path to save results (will use .pkl format).
		"""
		output_dict = {
			'simulation_result': output_dir / 'simulation_result.pkl',
			'cwd_ref_detector': output_dir / 'cwd_ref_detector.csv',
			'cwd_ref_sds': output_dir / 'cwd_ref_sds.csv',
		}

		save_dict: dict[str, Any] = {
			'flux': self.flux,
			'runtime': self.runtime,
			'nphoton': self.nphoton,
		}
		if self.det_photon is not None:
			save_dict['det_photon'] = self.det_photon
		if self.volume is not None:
			save_dict['volume'] = self.volume
		if self.seeds is not None:
			save_dict['seeds'] = self.seeds
		if self.trajectory is not None:
			save_dict['trajectory'] = self.trajectory

		output_dict['simulation_result'].parent.mkdir(parents=True, exist_ok=True)
		with open(output_dict['simulation_result'], 'wb') as f:
			pickle.dump(self, f)

		# detw = detweight(detp=self.det_photon, prop=cfg_dict['prop'] )
		# mean_path = meanpath(detp=self.det_photon, prop=cfg_dict['prop'] )
		# mean_scat = meanscat(detp=self.det_photon, prop=cfg_dict['prop'] )
		cwd_ref = cwdref(detp=self.det_photon, cfg=cfg)
		self.get_cwd_ref_by_detector(cwd_ref=cwd_ref).to_csv(
			output_dict['cwd_ref_detector'], index=False
		)
		if sds_detid_map is not None:
			self.get_cwd_ref_by_sds(cwd_ref=cwd_ref, sds_detid_map=sds_detid_map).to_csv(
				output_dict['cwd_ref_sds'], index=False
			)

		logger.info(f'Saved simulation results to {output_dir}')

	@classmethod
	def load(cls, input_path: Path) -> 'SimulationResult':
		"""Load simulation results from file.

		Args:
		    input_path: Path to load results from.

		Returns:
		    Loaded SimulationResult object.
		"""
		with open(input_path, 'rb') as f:
			data: SimulationResult = pickle.load(f)

		return data

	def __add__(self, other: 'SimulationResult') -> 'SimulationResult':
		"""Combine two SimulationResult objects by summing their flux and detected photons.

		Args:
		    other: Another SimulationResult object to combine with.
		Returns:
		    A new SimulationResult object with combined data.
		"""
		if not isinstance(other, SimulationResult):
			return NotImplemented

		combined_flux = None
		if self.flux is not None and other.flux is not None:
			combined_flux = self.flux + other.flux
		elif self.flux:
			combined_flux = self.flux
		elif other.flux:
			combined_flux = other.flux

		combined_det_photon: DetectPhoton | None = None
		if self.det_photon is not None and other.det_photon is not None:
			# Create a dict first, then cast to DetectPhoton
			temp_dict: dict[str, Any] = {}
			for key in self.det_photon.keys():
				if key in other.det_photon:
					self_val = self.det_photon[key] # type: ignore[literal-required]
					other_val = other.det_photon[key] # type: ignore[literal-required]
					if self_val is not None and other_val is not None:
						if key == 'unitinmm':
							if self_val != other_val:
								raise ValueError(
									'Cannot combine DetectPhoton with different unitinmm values.'
								)
							temp_dict[key] = self_val  # unitinmm should be the same
						else:
							if key == 'data':
								temp_dict[key] = np.hstack((self_val, other_val))
							else:
								temp_dict[key] = np.concatenate((self_val, other_val), axis=0)
					else:
						temp_dict[key] = self_val if self_val is not None else other_val
				else:
					temp_dict[key] = self.det_photon[key] # type: ignore[literal-required]
			for key in other.det_photon.keys():
				if key not in temp_dict:
					temp_dict[key] = other.det_photon[key] # type: ignore[literal-required]
			# Cast to DetectPhoton TypedDict
			combined_det_photon = temp_dict.copy() # type: ignore[assignment]
		elif self.det_photon is not None:
			combined_det_photon = self.det_photon.copy()
		elif other.det_photon is not None:
			combined_det_photon = other.det_photon.copy()

		return SimulationResult(
			flux=combined_flux,
			det_photon=combined_det_photon,
			volume=self.volume,
			seeds=self.seeds,
			trajectory=self.trajectory,
			runtime=self.runtime + other.runtime,
			nphoton=self.nphoton + other.nphoton,
		)

	def get_cwd_ref_by_detector(self, cwd_ref: np.ndarray) -> pd.DataFrame:
		"""Get cwd_ref results by detector.

		Args:
		    cwd_ref: cwd_ref array to save.
		"""

		detid = np.array([f'{i + 1}' for i in range(cwd_ref.shape[0])])
		df = pd.DataFrame({'detid': detid, 'cwd_ref': cwd_ref.flatten()})

		return df

	def get_cwd_ref_by_sds(self, cwd_ref: np.ndarray, sds_detid_map: dict) -> pd.DataFrame:
		"""Get cwd_ref results by sds.

		Args:
		    cwd_ref: cwd_ref array to save.
		"""
		cwd_ref_detector = self.get_cwd_ref_by_detector(cwd_ref).set_index('detid')

		sds_list = []
		for sds, detids in sds_detid_map.items():
			detid_strs = [str(detid) for detid in detids]
			cwd_ref_values = cwd_ref_detector.loc[detid_strs, 'cwd_ref'].values
			cwd_ref_mean = np.mean(cwd_ref_values) # type: ignore[arg-type]
			sds_list.append({'sds': sds, 'cwd_ref': cwd_ref_mean})

		return pd.DataFrame(sds_list)

	@classmethod
	def load_cwd_ref(cls, input_path: Path) -> np.ndarray:
		"""Load cwd_ref results from file.

		Args:
		    input_path: Path to load results from.

		Returns:
		    Loaded cwd_ref array.
		"""
		df = pd.read_csv(input_path)
		return df['cwd_ref'].to_numpy()


def capture_stdout[T](func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
	"""Capture stdout output of a function call."""
	buffer = io.StringIO()
	original_stdout = sys.stdout
	try:
		sys.stdout = buffer
		resp = func(*args, **kwargs)
	finally:
		sys.stdout = original_stdout

	# capture_output = buffer.getvalue()
	# logger.debug(f"Captured output from {func.__name__}: {capture_output}")
	print('')

	return resp


class MCXRunner:
	"""Runner for MCX photon transport simulations using pmcx.

	This class provides a high-level interface to configure and run
	Monte Carlo simulations using the pmcx library.

	Example:
	    >>> from ijv_project.mcx_simulation import (
	    ...     MCXRunner,
	    ... )
	    >>> from ijv_project.mcx_simulation.schema import (
	    ...     MCXConfig,
	    ... )
	    >>> from ijv_project.mcx_simulation.schema.mcxlab import (
	    ...     OpticalProperties,
	    ...     DetectorPosition,
	    ... )
	    >>> import numpy as np
	    >>> # Create configuration
	    >>> vol = np.ones(
	    ...     (60, 60, 60),
	    ...     dtype=np.uint8,
	    ... )
	    >>> config = MCXConfig(
	    ...     nphoton=1000000,
	    ...     vol=vol,
	    ...     prop=[
	    ...         OpticalProperties(
	    ...             mua=0,
	    ...             mus=0,
	    ...             g=1,
	    ...             n=1,
	    ...         ),
	    ...         OpticalProperties(
	    ...             mua=0.005,
	    ...             mus=1.0,
	    ...             g=0.01,
	    ...             n=1.37,
	    ...         ),
	    ...     ],
	    ...     tstart=0,
	    ...     tend=1e-9,
	    ...     tstep=1e-9,
	    ...     srcpos=[
	    ...         1,
	    ...         1,
	    ...         1,
	    ...     ],
	    ...     srcdir=[
	    ...         0,
	    ...         0,
	    ...         1,
	    ...     ],
	    ...     savedetflag='dspxv',
	    ...     bc='aaaaar',
	    ...     issave2pt=False,
	    ...     detpos=[
	    ...         DetectorPosition(
	    ...             x=1,
	    ...             y=1,
	    ...             z=0,
	    ...             radius=1.0,
	    ...         ),
	    ...         DetectorPosition(
	    ...             x=1,
	    ...             y=1,
	    ...             z=0,
	    ...             radius=1.0,
	    ...         ),
	    ...     ],
	    ... )
	    >>> sds_detid_map = {
	    ...     '1.0': [1],
	    ...     '2.0': [2],
	    ... }
	    >>> # Run simulation
	    >>> runner = MCXRunner(
	    ...     config,
	    ...     sds_detid_map,
	    ... )
	    >>> result = runner._single_run()
	    <BLANKLINE>
	    >>> print(
	    ...     f'Simulation completed in {result.runtime:.2f}s'
	    ... )
	    Simulation completed in 0.00s
	"""

	def __init__(
		self,
		config: MCXConfig,
		sds_detid_map: dict[str, list[int]] | None = None,
		na: NaFilterMap | None = None,
		save_dir: Path = Path('./mcx_output'),
	) -> None:
		"""Initialize MCX runner.

		Args:
		    config: MCX configuration object.
		    sds_detid_map: Mapping of source-detector pairs.
		"""
		self.config = config
		self.cfg_dict = config.to_pmcx_dict()
		self.sds_detid_map = sds_detid_map
		self.na = na
		self.save_dir = save_dir
		self.output = {
			'simulation_result': 'simulation_result.pkl',
			'cwd_ref_detector': 'cwd_ref_detector.csv',
			'cwd_ref_sds': 'cwd_ref_sds.csv',
		}
		logger.info(
			f'Initialized MCXRunner with {config.nphoton} photons, volume shape {config.vol.shape}'
		)

	def _na_filtering(self, result: SimulationResult) -> SimulationResult:
		"""Apply numerical aperture (NA) filtering to detected photons.

		Args:
		    result: SimulationResult object.

		Returns:
		    Filtered SimulationResult object.
		"""
		if self.na is None	:
			return result

		# Implement NA filtering logic here
		detp = result.det_photon
		if detp is None or detp['v'] is None:
			raise ValueError('No detected photon data for NA filtering.')

		cz = detp['v'][:, 2]  # z-component of direction
		after_refraction_theta_z = np.arccos(cz)
		na_angle = np.arcsin(self.na['na'] / self.na['refraction_index_1'])
		before_refraction_theta_z = np.arcsin(
			np.sin(after_refraction_theta_z)
			* self.na['refraction_index_0']
			/ self.na['refraction_index_1']
		)
		valid_indices = np.where(before_refraction_theta_z <= na_angle)[0]

		# Filter detected photons
		filtered_detp: DetectPhoton = {
			'detid': detp['detid'][valid_indices],
			'srcid': detp.get('srcid'),
			'nscat': detp['nscat'][valid_indices]
			if 'nscat' in detp and detp['nscat'] is not None
			else None,
			'ppath': detp['ppath'][valid_indices]
			if 'ppath' in detp and detp['ppath'] is not None
			else None,
			'mom': detp['mom'][valid_indices]
			if 'mom' in detp and detp['mom'] is not None
			else None,
			'p': detp['p'][valid_indices] if 'p' in detp and detp['p'] is not None else None,
			'v': detp['v'][valid_indices] if 'v' in detp and detp['v'] is not None else None,
			'w0': detp['w0'][valid_indices] if 'w0' in detp and detp['w0'] is not None else None,
			's': detp['s'][valid_indices] if 's' in detp and detp['s'] is not None else None,
			'prop': detp.get('prop'),
			'data': detp['data'][:, valid_indices]
			if 'data' in detp and detp['data'] is not None
			else None,
			'unitinmm': detp.get('unitinmm'),
		}
		result.det_photon = filtered_detp

		# This is a placeholder implementation
		logger.info(f'Applying NA filtering with NA={self.na}')
		# Actual filtering code would go here

		return result

	def _single_run(self) -> SimulationResult:
		"""Run Monte Carlo simulation.

		Returns:
		    SimulationResult object containing simulation outputs.

		Raises:
		    RuntimeError: If simulation fails.
		"""
		# logger.info("Starting MCX simulation...")
		# logger.debug(f"Configuration: {self.cfg_dict}")

		try:
			# Run simulation
			output = capture_stdout(pmcx.mcxlab, self.cfg_dict)
			if not isinstance(output, dict):
				raise RuntimeError(
					f'Expected dictionary output from pmcx.mcxlab, got {type(output)}'
				)

			result = self._parse_output(output)
			if self.na is not None:
				result = self._na_filtering(result)
			logger.success(
				f'Simulation completed successfully in {result.runtime:.2f}s. '
				f'Simulated {result.nphoton} photons.'
			)

			return result

		except Exception as e:
			logger.error(f'MCX simulation failed: {e}')
			raise RuntimeError(f'MCX simulation failed: {e}') from e

	def _parse_output(self, output: dict[str, Any]) -> SimulationResult:
		"""Parse pmcx output into SimulationResult.

		    pmcx.mcxlab returns a dictionary with keys:
		    'flux', 'detp', 'vol', 'seeds', 'trajectory', 'stat'

		Args:
		    output: Dictionary output from pmcx.mcxlab().

		Returns:
		    Parsed SimulationResult object.
		"""

		flux = output.get('flux', output.get('fluence'))
		if flux is None:
			logger.warning('No flux/fluence data found in simulation output')

		runtime = 0.0
		nphoton = self.config.nphoton

		# Extract runtime from stat if available
		if 'stat' in output:
			stat = output['stat']
			if isinstance(stat, dict):
				runtime = stat.get('runtime', 0.0)
				nphoton = stat.get('nphoton', nphoton)

		if 'detp' in output:
			detp = DetectPhoton(**output['detp']) # type: ignore[typeddict-item]

			if detp.get('detid') is None:
				raise ValueError(
					"No detid in detected photon data, you should set cfg.savedetflag='d' to get detid."
				)
		else:
			detp = None

		return SimulationResult(
			flux=flux,
			det_photon=detp,
			volume=output.get('vol'),
			seeds=output.get('seeds'),
			trajectory=output.get('trajectory'),
			runtime=runtime,
			nphoton=nphoton,
		)

	def calculate_cwd_ref_cv(
		self,
		detector_path_pattern: str = 'iteration_*/cwd_ref_detector.csv',
		sds_path_pattern: str = 'iteration_*/cwd_ref_sds.csv',
	) -> tuple[pd.DataFrame, pd.DataFrame]:
		"""Calculate coefficient of variation (CV) for cwd_ref results."""

		def _calculate_cv(
			cwd_ref_data: list[pd.DataFrame],
			key: str,
		) -> pd.DataFrame:
			# Calculate coefficient of variation (CV) for each detector
			# Based on poisson distribution, we can predict the CV if we used all the iterations results
			# predicted CV = CV / sqrt(n_iterations)
			if len(cwd_ref_data) == 0:
				return pd.DataFrame()

			cwd_ref_std = pd.concat(cwd_ref_data).groupby([key])['cwd_ref'].std()
			cwd_ref_mean = pd.concat(cwd_ref_data).groupby([key])['cwd_ref'].mean()
			cwd_ref_cv = (cwd_ref_std / cwd_ref_mean * 100).reset_index()
			cwd_ref_predicted_cv = cwd_ref_cv.copy()
			cwd_ref_predicted_cv['cwd_ref_cv_percent'] = cwd_ref_cv['cwd_ref'] / np.sqrt(
				len(cwd_ref_data)
			)
			cwd_ref_predicted_cv.columns = pd.Index([
				key,
				'cwd_ref_cv_percent',
				'cwd_ref_predicted_cv_percent',
			])

			# pd.set_option(
			#     "display.float_format",
			#     lambda x: "%.5f" % x,  # noqa: UP031
			# )  # Adjust precision as needed
			# logger.debug(f"\n{cwd_ref_predicted_cv}")

			return cwd_ref_predicted_cv

		cwd_ref_detector = []
		number_iterations = 0
		for csv_file in self.save_dir.glob(detector_path_pattern):
			df = pd.read_csv(csv_file)
			df['iteration'] = number_iterations
			cwd_ref_detector.append(df)
			number_iterations += 1

		logger.debug(f'Calculating detector CV from {number_iterations} iterations')
		cwd_ref_detector_cv = _calculate_cv(cwd_ref_detector, key='detid')
		logger.debug(f'\n{cwd_ref_detector_cv}')

		cwd_ref_sds = []
		number_iterations = 0
		for csv_file in self.save_dir.glob(sds_path_pattern):
			df = pd.read_csv(csv_file)
			df['iteration'] = number_iterations
			cwd_ref_sds.append(df)
			number_iterations += 1

		logger.info(f'Calculating SDS CV from {number_iterations} iterations')
		cwd_ref_sds_cv = _calculate_cv(cwd_ref_sds, key='sds')
		logger.info(f'\n{cwd_ref_sds_cv}')

		return cwd_ref_detector_cv, cwd_ref_sds_cv

	def create_mcx_preview(self) -> None:
		"""Create MCX preview visualization.

		Note:
		    This function is a placeholder and should be implemented
		    to provide visualization of the MCX configuration.
		"""
		logger.info('Creating MCX preview visualization...')
		mcx2preview_json(self.cfg_dict, self.save_dir / 'mcx_preview')

	def merge_per_n_iterations_cwd_ref(
		self,
		per_n_iterations: int,
	) -> None:
		"""Merge cwd_ref results from multiple iterations into a single summary.

		Args:
		    per_n_iterations: Number of iterations to merge.
		    output_path: Path to save merged summary CSV.

		Returns:
		    pd.DataFrame: Merged summary DataFrame.
		"""
		all_simulation_result_files = sorted(
			self.save_dir.glob('iteration_*/simulation_result.pkl'),
			key=lambda x: int(x.parent.name.split('_')[1]),
		)
		iteration_groups = [
			all_simulation_result_files[i : i + per_n_iterations]
			for i in range(0, len(all_simulation_result_files), per_n_iterations)
		]

		for group in iteration_groups:
			result = SimulationResult()
			start_iter = int(group[0].parent.name.split('_')[1])
			end_iter = int(group[-1].parent.name.split('_')[1])
			for pkl_file in group:
				if pkl_file.exists():
					result += SimulationResult.load(pkl_file)

			result.save(
				self.save_dir / 'merge' / f'iteration_{start_iter:04d}_to_{end_iter:04d}',
				cfg=self.cfg_dict,
				sds_detid_map=self.sds_detid_map,
			)

	def run(
		self,
		n_iterations: int,
		prop: np.ndarray | None = None,
		cv_threshold: float | None = None,
	) -> None:
		"""Run multiple simulation iterations.

		This is used for White Monte Carlo where we run with mua=0
		and then post-process with real mua values.

		Args:
		    n_iterations: Number of iterations for the simulation,
		        if `cv_threshold` is specified cv calculation will perform each `n_iterations`.
		    prop: Optional list of OpticalProperties to update before each run.
		        If provided, should match the length of config.prop.

		Returns:
		    List of SimulationResult objects.

		Note:
		    For proper CV calculation with WMC, use the wmc module:
		    from ijv_project.mcx_simulation.wmc import run_wmc_with_cv_criterion
		"""
		logger.info(f'Running {n_iterations} simulation iterations')

		while True:
			# Get starting iteration based on existing files
			existing_iterations = list(self.save_dir.glob('iteration_*/simulation_result.pkl'))
			if existing_iterations:
				existing_indices = [int(f.parent.name.split('_')[1]) for f in existing_iterations]
				start_iteration = max(existing_indices) + 1
				logger.info(
					f'Found {len(existing_iterations)} existing iterations, '
					f'resuming from iteration {start_iteration}'
				)
			else:
				start_iteration = 1

			# Run iterations
			for curr_iteration, _ in enumerate(range(n_iterations), start=start_iteration):
				logger.info(f'Iteration {curr_iteration}/{n_iterations + start_iteration - 1}')

				result = self._single_run()
				if result.det_photon is None:
					raise ValueError('No detected photon data to save summary.')
				assert self.config.detpos is not None, 'Detector positions not defined in config.'
				assert np.unique(result.det_photon['detid']).size == len(self.config.detpos), (
					'Number of unique detid in detected photon data does not match number of detectors.'
				)

				# Update prop if provided
				if prop:
					self.cfg_dict['prop'] = prop
				result.save(
					self.save_dir / f'iteration_{curr_iteration:04d}',
					cfg=self.cfg_dict,
					sds_detid_map=self.sds_detid_map,
				)
			logger.success(f'Completed {n_iterations + start_iteration - 1} iterations')

			det_cwd_ref_cv_df, sds_cwd_ref_cv_df = self.calculate_cwd_ref_cv()
			det_cwd_ref_cv_df.to_csv(self.save_dir / 'det_cwd_ref_cv_summary.csv', index=False)
			sds_cwd_ref_cv_df.to_csv(self.save_dir / 'sds_cwd_ref_cv_summary.csv', index=False)
			# Calculate CV if threshold is provided
			if cv_threshold is not None:
				if sds_cwd_ref_cv_df['cwd_ref_predicted_cv_percent'].max() > cv_threshold:
					logger.info(
						f'Max predicted CV {sds_cwd_ref_cv_df["cwd_ref_predicted_cv_percent"].max():.2f}% '
						f'above threshold {cv_threshold}%, continuing iterations.'
					)
					continue
				else:
					logger.success(
						f'Max predicted CV {sds_cwd_ref_cv_df["cwd_ref_predicted_cv_percent"].max():.2f}% '
						f'below threshold {cv_threshold}%, stopping iterations.'
					)
					break
			else:
				break
