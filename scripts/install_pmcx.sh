#!/bin/bash
git submodule update --init --recursive
source .venv/bin/activate

echo "Building pmcx wheel..."
echo "-----------------------------------"

cd src/third_party/mcx_fanq/pmcx
git reset fbe3de0 --hard
uv pip install . --force-reinstall --no-deps
rm -r build pmcx.egg-info