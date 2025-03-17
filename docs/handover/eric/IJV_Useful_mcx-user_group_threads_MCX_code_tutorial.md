---
tags: Lab
---
# IJV | Useful mcx-user group threads 與 MCX Code 整理

## mcx-user group threads
mcx-user link: [here](https://groups.google.com/g/mcx-users).

1. pymcx 開發的始末
    記錄原本是澂開發的慢慢的 outdated，然後有人承接、優化，並形成一個 repo (但現在好像又 outdated 了)
    https://groups.google.com/g/mcx-users/c/Gypz-YvuYZY/m/Ih7m07qAAQAJ
2. Info about issaveref
    https://groups.google.com/g/mcx-users/c/nMZzRXeHmFQ/m/iHtjO5RfBQAJ
3. 2019-08-21 [d9d5238] allow one to overwrite SaveDataMask from command line

## MCX code 說明
1. 要利用 MCX 模擬光子的 random walk，可分為兩大步驟。==1. 外部呼叫:== 利用 python 或 matlab 製作適當的 `simulation input file` (本 project 為 python)，並合成 command，於 cmd 上送入 mcx kernel。==2. 內部模擬:== 可將 `mcx_utils.c` 與 `mcx_core.cu` 視為核心的模擬程式，兩支程式各 include 了數個 .h file 做使用，例如 `mcx_utils.h`、`mcx_const.h`、`mcx_core.h` ... 等。

2. mcx 執行檔 compile 方式：於 `/mcx/src` 中開啟 command line，並 type 上 `make`。

## 內部模擬 (from source code)
### 基本流程
#### `mcx_utils.c`
- **parse `command` from cmd.**
- **變數名稱轉換** → 例如 src_type 的 pencil 轉換成 1，src_type 的 anglepattern 轉換成 16。
- ...etc。

#### `mcx_core.cu`
- **Do main simulation.**
- **Important functions (might be related to our project)**
    - ==Ln 693==: @brief Terminate a photon and launch a new photon according to specified source form
        - `__device__ inline int launchnewphoton()`
        - ==Ln 794==: Attempt to launch a new photon until success
        - ==Ln 1051==: Now a photon is successfully launched, perform necssary initialization for a new trajectory
    - ==Ln 1107==:  @brief The core Monte Carlo photon simulation kernel (!!!Important!!!)
        - This is the core Monte Carlo simulation kernel, please see [Fig. 1 in Fang2009](https://www.osapublishing.org/getImage.cfm?img=LmZ1bGwsb2UtMTctMjItMjAxNzgtZzAwMQ&article=oe-17-22-20178-g001). Everything in the GPU kernels is in grid-unit. To convert back to length, use cfg->unitinmm (scattering/absorption coeff, T, speed etc)
        - `kernel void mcx_main_loop()`
    - ==Ln 1675==: @brief Master host code for the MCX simulation kernel (!!!Important!!!)
        - This function is the master host code for the MCX kernel. It is responsible for initializing all GPU variables, copy data from host to GPU, launch the kernel for simulation, wait for competion, and retrieve the results.
        - `void mcx_run_simulation()`

