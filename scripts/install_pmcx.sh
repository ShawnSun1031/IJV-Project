#!/bin/bash
source .venv/bin/activate

# git submodule init
# cd src/third_party/mcx_md703
# git checkout add_angel_pattern
# git pull origin add_angel_pattern
# git submodule update --init --recursive

# cd pmcx

cd /home/dicky1031/julie/MD703_edit_MCX_src_v2023/pmcx
python3 -m pip wheel .
uv pip install --force-reinstall --no-deps pmcx-*.whl