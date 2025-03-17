# 如何修改MCX原版code
> [time=Sat, Jan 29, 2022 11:11 PM]
> [name=dicky1031]
> [TOC]

## 1. 初始設定
[原始程式碼連結](https://github.com/fangq/mcx)
我修改的部分從branch-master clone而來
修改資料夾 MCX/src (原版MCX C code都會在這裏面)

## 2. 原始code功能說明
判斷哪個detector偵測到:
mcx_core.cu : finddetector
使用出光光子與detector XYZ距離的平方合，看是否在detector半徑以內

mcx_core.cu : mcx_main_loop
是MC的主要loop
他真的是在每個while loop裡面一個一個voxel移動

random出一個unitless PL後
走一個voxel花的距離要乘上mus才是他花掉的PL

不過他裡面有計算mua衰減的code
mcx_core.cu : line 1255~1259


finddetector會被savedetphoton呼叫到，用來決定要儲存在哪個detector
而savedetphoton會在每次launchnewphoton時被呼叫到，把上一顆光子的資訊存起來
launchnewphoton則會在mcx_main_loop裡面的開始新光子、光子跑出組織外、輪盤玩輸之後被呼叫到
看起來頗合理
因此應該不會有上次懷疑的，detector太大(超出一個voxel)導致收到的光子不對的狀況

mcx_main_loop之中
launchnewphoton在一開始、玩輪盤，或是time window超過、光子從non-zero voxel跑到zero voxel時會被呼叫

launchnewphoton: 結束目前的光子，並且開始新的光子
如果mediaid(the medium index at the voxel at launch)==0且isdet(前一顆光子打到了detector)的話，裡面會呼叫到savedetphoton，才會把偵測到個光子存起來

transmit會在檢查光子是否跑到zero voxel前被呼叫，而transmit會改變方向，所以輸出的光子方向應該是已經跑到外面的方向

## 3. Make mex
### 3.1 編譯mex檔案
mex為matlab執行C語法的執行檔案，所以當修改完原始版C語言的程式碼後，需要再將其編譯成matlab可以執行的mex檔案
具體使用方式: 打開終端機(terminal)
```
cd ~/mcx-master/src
cmake ~/mcx-master/src
make
```
之後如果都沒報錯，編譯好的mex檔案將會在mcx-master/bin裡面

---
### 3.2 如果遇到錯誤的解決方案
#### 3.2.1 GPU環境不相容
```
nvcc fatal   : Value 'sm_30' is not defined for option 'gpu-architecture'
```
如果看到此錯誤(注意錯誤可能為sm_**，**為任意數字代表不同版本)，代表gpu環境編譯時發生不相容的情況，此時請點[此連結](https://arnon.dk/matching-sm-architectures-arch-and-gencode-for-various-nvidia-cards/)查看本機端電腦的gpu規格。

---
ex:假如GPU為RTX2080，則表示此架構為Turing (CUDA 10 and later)適用sm_75版本。
因此需要將~/mcx-master/src這個路徑下的cmakelist.txt做修改。
```
# NVCC Options
set(
    CUDA_NVCC_FLAGS
    ${CUDA_NVCC_FLAGS};
    -g -lineinfo -Xcompiler -Wall -Xcompiler -fopenmp -O3 -arch=sm_30
    -DMCX_TARGET_NAME="fermi  MCX" -DUSE_ATOMIC -use_fast_math
    -DSAVE_DETECTORS -Xcompiler -fPIC
    )
```
將上述程式碼中的 sm_30 修改為 sm_75，
-DMCX_TARGET_NAME="fermi  MCX" --> -DMCX_TARGET_NAME="Turing  MCX"

#### 3.2.2 ZLIB錯誤
```
Could NOT find ZLIB (missing: ZLIB_LIBRARY ZLIB_INCLUDE_DIR)
```
如果看到上述錯誤則代表需安裝ZLIB，執行以下程式碼即可
```
sudo apt-get install zlib1g-dev
```

Config structure 在 mcx_utils.h 259行
mcx_run_simulation 在 mcx_core.cu 2236行 mcxlab.cpp 257行
launchnewphoton 在 mcx_core.cu 1026行

#ifndef#define#endif的用法(整理)
https://huenlil.pixnet.net/blog/post/24339151

```
__device__ inline uint finddetector(MCXpos *p0){
      uint i;
      for(i=gcfg->maxmedia+1;i<gcfg->maxmedia+gcfg->detnum+1;i++){
      	if((gproperty[i].x-p0->x)*(gproperty[i].x-p0->x)+
	   (gproperty[i].y-p0->y)*(gproperty[i].y-p0->y)+
	   (gproperty[i].z-p0->z)*(gproperty[i].z-p0->z) < gproperty[i].w*gproperty[i].w){
	        return i-gcfg->maxmedia;
	   }
      }
      return 0;
}

```

在 core.cu 的2764行 /** Copy param to the constant memory variable gcfg */ 把 cfg的data複製到 gcfg(在GPU上)
```
__host__ ​cudaError_t cudaMemcpyToSymbol ( const void* symbol, const void* src, size_t count, size_t offset = 0, cudaMemcpyKind kind = cudaMemcpyHostToDevice )

Copies data to the given symbol on the device.

Parameters
symbol
- Device symbol address
src
- Source memory address
count
- Size in bytes to copy
offset
- Offset from start of symbol in bytes
kind
- Type of transfer

```



2348行
```
MCXParam param={cfg->steps,minstep,0,0,cfg->tend,R_C0*cfg->unitinmm,
                     (uint)cfg->issave2pt,(uint)cfg->isreflect,(uint)cfg->isrefint,(uint)cfg->issavedet,1.f/cfg->tstep,
		     p0,c0,s0,maxidx,uint4(0,0,0,0),cp0,cp1,uint2(0,0),cfg->minenergy,
                     cfg->sradius*cfg->sradius,minstep*R_C0*cfg->unitinmm,cfg->srctype,
		     cfg->srcparam1,cfg->srcparam2,cfg->voidtime,cfg->maxdetphoton,
		     cfg->medianum-1,cfg->detnum,cfg->polmedianum,cfg->maxgate,0,0,ABS(cfg->sradius+2.f)<EPS /*isatomic*/,
		     (uint)cfg->maxvoidstep,cfg->issaveseed>0,(uint)cfg->issaveref,cfg->isspecular>0,
		     cfg->maxdetphoton*hostdetreclen,cfg->seed,(uint)cfg->outputtype,0,0,cfg->faststep,
		     cfg->debuglevel,cfg->savedetflag,hostdetreclen,partialdata,w0offset,cfg->mediabyte,
		     (uint)cfg->maxjumpdebug,cfg->gscatter,is2d,cfg->replaydet,cfg->srcnum,cfg->nphase,cfg->omega};
```

param initial時沒有宣告bc
之後才宣告bc如下

2677行
```
memcpy(&(param.bc),cfg->bc,12);
```



***
開始修改
在MCX_utils.h的259行 Config{}增加 float detreflect之屬性;

matlab structure to cJson https://github.com/fangq/mcx/tree/master/src/cjson

mcx_loadjson

