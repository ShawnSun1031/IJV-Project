from pathlib import Path

import pytest


@pytest.fixture
def temp_test_dir(tmp_path: Path):
    test_dir = tmp_path / "mcx_output/test_simulation"
    test_dir.mkdir(parents=True, exist_ok=True)
    yield test_dir
