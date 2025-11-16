#!/bin/bash
git submodule update --init --recursive
source .venv/bin/activate

echo "Building pmcx wheel..."
echo "-----------------------------------"

cd src/third_party/mcx_fanq/pmcx
python3 -m pip wheel .
uv pip install --force-reinstall --no-deps pmcx-*.whl
# git reset --hard HEAD