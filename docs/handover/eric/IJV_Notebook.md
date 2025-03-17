---
tags: Lab
---
# IJV | Notebook

## 2021/11/03
==Debug==
1. 不同 x size 下的 detected photons
    - 較大可能上升也可能下降
    - 一樣的話應該要不變
    - 縮小的話應該要變少
2. 簡單模型下，Grid 與 jdata 的形式去模擬，得到的 "detected photons" 與 "absorbed" 會一樣
3. 以 jdata 去模擬，model size 縮減的趨勢符合預期。
    - 但 mus 過大時，reflectance 會過小

==再確認模型是否有誤==
1. 光源分佈 - 沒問題
2. 模擬擺設位置(對稱性，光源需置於中央) -- debug: unitmm 最大只能 0.5mm

==determine==
1. **Eric large - mus_ub**

==final size test==
1. Eric large - mus_ub (big model)
2. **Eric large - mus_ub (small model)**

==闡釋散射影響==
1. Eric large - mus_ub v.s. Eric large - mus_lb

==for昕原==
1. **Eric small - mus_lb**


## 2021/10/24 - 超音波模型確認
模型
1. ~~scaling 是否正確~~
2. ~~z 方向 → 每一層的格數是否符合預期~~
    ~~- 還行~~
4. ~~x, y → holder 寬度是否符合預期~~
    ~~- source holder 符合~~
    ~~- detector holder 符合~~
5. ~~source, detector 是否有擺在正確位置~~
    ~~- fiber 位置正確~~、**detector 需再確認**
    ~~- source window 位置與大小正確~~，**source 位置本身需再確認**
6. **python 與 matlab 的 xyz 方向**

模擬
1. interior boundary → 反射
2. exterior boundary → 不反射

影像
1. skin, fat 區分
2. 決定要用我的還是昕原的影像

## 2021/10/13
1. copy 一份 mcx.py 去改
2. 改 postprocess.py 中的 detectorNum → 直接 x 3 x 2，但可能需要改，與 reflectance.shape[1]

## 2021/10/12
1. Boundary condition check
    - 改變 musp 運算的基底波長 → 目前暫定 800nm (mcx.py function更動)
    - 將 skin 的 g 改為 0.9
    - specular 不用去改，原本預設就會考慮進去(考慮 specular reflection) ---> 可是如果有考慮進去，initial weight 應該不要是 1 ??
    - 需更新 postprocess 中的 pathlength 取得

## 2021/10/04 - Training
先前學長訓練資料集
1. 子佳
    - **做迴歸以減少模擬時間**
    - 目標波長：700-900 nm
    - 資料筆數：5808(散射) * 3000(吸收) = 17424000 (一千七百多萬筆)
    - 資料劃分：training → 75%、validation → 10%、testing → 15%
2. 是澂
    - 放大 detector radius 以減少模擬時間
    - 資料筆數：48700 (四萬多筆)
    - 資料劃分：training → 98%(47700)、testing → 2%(1000)
3. 我
    - 目前無放大 detector

## 2021/09/01 - 驗證模擬正確性(與是澂比較)
目標：應該是驗證 code 是否正確就行(稜鏡…等等的影響嚴格上不包含在這裡)
前言：是澂的 wmc 有拿去與真正的 mc 做驗證，結果是穩合的。(我想關鍵是 pathlength 的提取，只要層數與單位正確，應該就沒問題)
1. 先確認 mcx_fanqq.mch 的 pathlength 位於哪幾個 column (與 mcx_toast.mch 做比較)，找出來後進行標記
2. 使用 mcxlab 中的 loadmch.m 進行 mch file 的讀取，內部會將 pathlength 的單位從 [grid] 轉成 [mm] (是澂的 load_mch 也有做此步驟)。
    - 補充：load mcx_fanqq.mch 時有轉換單位，但 load mcx_toast.mch 時沒有。(猜測原因是 mcx 版本不同)
4. **假定 mcx_fanqq.mch 模擬出的結果(pathlength與dz)是正確的。**
5. 使用 mcx_fanqq 模擬，output 出兩種資料型態，並比較兩者的下方資訊(相同 seed)：<font color="red">**✓**</font>
    - 以 loadmch.m 讀取 mcx_fanqq.mch 所得出的 pathlength 與 dz
    - 以 jd.load 讀取 mcx_fanqq.jdat 所得出的 pathlength 與 dz
6. 如果上述比較相同，則比較以下兩者(相同 seed)：<font color="red">**✓**</font>
    - 以 mcx_fanqq 模擬得的 mch (pathlength 與 dz)
    - 以 mcx_syu 模擬得的 jdata (pathlength 與 dz)
7. 實際去計算 reflectance，看是澂的算法與我的算法是否一樣：
    比較對象
    - 以 mcx_fanqq 模擬得的 mch
    - 以 mcx_syu 模擬得的 jdata

==待辦==
要把這段改好：
![](https://i.imgur.com/6tYOyCL.png)



==先驗證 jdata 的 reflectance 計算可行再繼續==
1. 比較是澂 loadmch 與我 load jdata **之後**的 code
2. 比較 loadmch 內的內容(是澂-oldmcx、mcxlab、我-newmcx)
3. mcxlab loadmch.m
4. 不一定要比較真正的 reflectance 和經 wmc 的 reflectance。但可以比較 loadmch 後和 jdata 的內容，以及後續計算 reflectance 的 code。(也可以比較,注意 total diffuse reflectance → per voxel ??)
5. 比較 wmc 與 真正 mc 的 weight
6. normalize、specular、skipradius、initial weight
7. 

**模擬環境差異整理：**
1. 2021 與 2018 用相同 seed 跑，結果會不同
2. 2021 跑的 mch 沒辦法用是澂寫的 load_mch 讀取

**測試目的：**
為了比較，需儘量還原當時是澂模擬的環境，也於此會犧牲 seed。

**測試方式：**
還原當時是澂模擬的環境，再與現行的版本比較(改過的 cuda code，不同的硬體，不同的擺設，不同的 output 檔案格式)

**測試流程**
原始模型：僅含 cone source, detector
1. 測現行使用版本 mcx 的正確性(reflectance 數量級也應該 1e-10 左右)
    使用相同 seed
    - 是澂：原始模型
    - 新版：原始模型
2. 測光源影響
    - 是澂：原始模型
    - 新版：原始模型 but 光源改為 LED
3. 測 holder 影響
    - 是澂：原始模型
    - 新版：原始模型 but 光源改為 LED、probe 加上 holder(detector 一樣貼於表面，也因此 detector 的位置需有一層空氣柱)
4. 測稜鏡影響
    - 是澂：原始模型
    - 新版：原始模型 but 光源改為 LED、probe 加上 holder(detector 不貼於表面)、加上稜鏡
**備住：記得是澂的 na 較小 (0.12)

## 2021/08/27
1. 整理目前結果 
    - 最新 reflectance mean & cv
    - cv variation
    - reflection coefficient analysis
    - 回報子佳、是澂 reflectance 的數量級與所需光子數
2. 後續規劃
    - 模擬波長
    - 找最佳模型大小
    - 對稱模擬、多個 sds 同時模擬、detector fiber 直徑放大
    - regression 修正的事物
        1. 大 NA to 小 NA
        2. 半徑
        3. 稜鏡
        4. 延長的稜鏡造成的反射率差異
    - 校正仿體修正的事物(模擬光譜與實驗光譜之間的關係式)
        1. sensor 響應


## 2021/08/19 - 減少模擬時間方法/
- 減少所需光子數
    1. 大數值孔徑 ==(子佳)==
    2. 對稱 detector holder
    3. 增加 detector 面積
- 提升模擬速度
    1. **縮小模型尺吋**(本研究為開放模型，與大腦的封閉模型不同)

## 2021/08/07 - 模擬待辦
- For **sds 確認**
    1. ~~確認 source 為何在皮膚上一層也有吸收(ignore first)~~
    2. ~~完成 pattern 分佈確認 function~~
    3. ~~完成 reflectance 計算 function~~ ==(previous) ↑==
    4. ~~improve the function for making mcxInputForPreview.~~
    5. ~~檢查模擬數量是否為 10 的基數~~
    6. ~~cv.max()、show reflectanceMean~~ ==(8/11) ↑==
    7. run mcx in windows
    8. ~~++github pull++~~
    9. 使用新的 ssd，裝 linux，於 3070 中跑
    10. ~~計算 cv 下降趨勢 (應該光子數有關)~~
    11. 計算 reflectance 時，要以id排序output，一個是刪減時排，一個是合併前排
    12. 如果已有該波長的 mcxInput，就不用再做
    13. check jdata information in MCX google group ([mcx cloud paper](https://www.biorxiv.org/content/10.1101/2021.06.28.450034v1.full.pdf), [jdata specification in github](htt[ps://](https://github.com/fangq/jdata)))
    14. 看子佳是澂之前模擬的數量級、以及原因
        - 子佳
            1. 在做 sds 靈敏度分析時是以 1e11 的光子數模擬
            2. 
        - 是澂
    15. make sure "air" is outside the "Grid"
        - validate by comparing two cases based on same seed.
    16. 畫目前程式的架構圖
    17. reading of mcxInput in two functions of postprocess.py (for wavelength)
    18. add wl id to mcxoutput
    19. make wavelength, detector_na be an input (maybe in config)
- For **sds sensitivity analysis** & **training**
    1. 整理昕原散射、吸收，模擬參數確認
    2. 決定模擬的波長
    3. n, g 詢問老師
    4. 超音波幾何結構擷取 (image → grid)
    5. ==training 前可先找一條平滑的 curve ?==
- For fitting
    1. add tissue composition
    2. 血紅素濃度也需要 fit ?
    3. 整理要 fit 的生理物質(參數種類)
- **Keep doing**
    - **do modularization, add design pattern**
    - **plot structure of the code**

## 2021/07/09 - 模擬架構規劃
[連結](https://hackmd.io/nHbfp0GiS4CgxaC8pL0gdg?both)

## 2021/07/07 - source simulation 驗證 6
兩種比較方式
1. 比較不同角度的直線，看實驗與mcx的趨勢是否相同
    - 實作
        - 選擇角度、半徑長度 → r
        - 將 -r ~ r 分成 n 個等分
        - 取得這 n 個等分所對應到的 (x,y)
        - 取得每一個 (x,y) 所對應的 pixel 的 gray value
        - 畫變化趨勢
    - 例子
        ![](https://i.imgur.com/kIEQBiG.png =40%x) ![](https://i.imgur.com/GjUCEGj.png =40%x) ![](https://i.imgur.com/WJRSGAT.png =40%x)

2. 比較相同 radial distance 的平均 gray value
    - 前提？
        - 中心要抓好？
        - 影像一定要是輻射對稱？==好像也不用!==(雖然光源是矩形，但似乎是距離算遠，所以照射下來的強度分佈像圓形)
    - 實作
        - 選擇徑向距離(radial distance)
        - 將 0~360^o^ 分成 n 等分
        - 取得這 n 個角度所對應到的 (x,y)
        - 取得每一個 (x,y) 所對應的 pixel 的 gray value
        - 計算這 n 個 gray value 的平均 → 得此徑向距離的 gray value
    - 例子
        ![](https://i.imgur.com/wpojBxN.png =40%x) ![](https://i.imgur.com/zXNM25J.png =40%x) ![](https://i.imgur.com/FxX8MqR.png =40%x)





## 2021/07/05 - source simulation 驗證 5
實驗拍攝結果比較(use pillow to read image)
1. 20210607：最弱強度影像 → blue channel 過曝，整體灰階值沒有
2. 20210624：最弱強度影像 → blue channel 過曝，整體灰階值沒有
3. 20210630：led照光的區域均沒有過曝的現象
    - **EX:**
    ![](https://i.imgur.com/6eQrKzA.png =60%x)
    - 找出中心點
    - 畫趨勢線


## 2021/05/26 - source simulation 驗證 4
LED pattern 本身似乎有一點點微右偏，但看不出來，應該 data sheet 提供的資料本身造成，因此這裡忽略。
1. 期望分佈計算
    - 誤差來源
        - 實際上每一個 grid 的 angle_interval 不一樣 (越外圍的 angle_interval 應該會越小，但目前假設一樣) ++**→ 做修正**++
        - 實際上每一個 grid 所需的圓環大小不一樣 (越接近對角線的 grid 所需的圓環應該要越大，但目前假設一樣)
3. mcx 模擬
    - 最外環特別小
5. 實驗

## 2021/05/05 - source simulation 驗證 3
==重新檢查一次 mcx_core.cu, mcx_utils.c==
- mcx_core.cu
        - 新增 radiated window 可以是圓形的狀況
        - angle pattern array 需為 radians
        - **需檢查 code 有無錯誤以及 ifelse 判斷是否有效率。以及 if 內能不能直接放 float。確認 srcparam1, srcparam2 的 float 的順序是 x, y, z, w.。angle array 要有 10001 個嗎？確認光子 p 的起始位置與x, y, z, w**
        - 之前跑錯了!!!!!!! srcparam1.x 應該要放數字，不能放 array !!!
        - 應該要新增一個 src.pattern !!!
        - origin type 與 source 位置的關係
        - 不知為何 p 需要比 0 小一點點才能讓光子在不同的位置發射，例如 -0.0001。
        - 不知道為什麼 sizeof(srcpattern[0]) 一直都是 0.00000 ...QQ
- mcx_utils.c
    - 確認整體 code 的修改是否能 match 子佳的 mcxlab.cpp
    - 確認 code 有無錯誤

## 2021/05/03 - source simulation 驗證 2
==確認驗證需要用的 mua==

測試 mua。.py 檔位於 `Desktop/ijv_2`

1. 撰寫 `determine_validationMUA.py`，內含 step size 的 pdf, cdf, quantile, get_properCoeff ... 等 function。
2. MCX 本身應該是跑 WMC，因此需要用 WMC 的角度去思考。(先根據 mus sampling step size，再用 mua 去計算光子沿著 trajectory 行走時被吸收的能量)
3. **結果：**
    計算出不同的 traveling pathlength 下, 需要多少的 mua 才能讓 99.9% 的 photon weight 被吸收。(99.9% 為可調，traveling pathlength 也是可調)

## 2021/04/26 - source simulation 驗證 1
==確認可跑==
- **`0426`** 
    1. 新增 inverse_cdf 的 script，並製作新的 input_addLED.json，內放 sourcepattern_array 與相關的 srcparam。
    2. 誤以為可跑，不過經測試後其實應該是跑成 default → src_type="pencil"。
- **`0427`**
    1. 初步確認 mcx_utils.c 與 mcx_core.cu 的關連，並於 mcx_utils.c 新增 new source type → "anglepattern"。
    2. 目前應該是可跑，至少跑起來跟 src_type = "pencil" 時不一樣 (detected photons 的數目不同)。
- **`0428`**
    1. [順 mcx code](https://hackmd.io/BvWQe1AjQqC7FLQSFD7qHg)。
    2. 確認 mua 設成 10000，mus 設成 0 的情況下是可跑的，不過還不會 output .mc2 file。
- **`0429`**
    1. 發現 **.jdata** 與 .mch 應該可以算是 equivalent 的，之後可以試著注意 .jdata 的使用，因其容量小(看起來有壓縮)，且使用起來十分方便，就像 json data 一樣! (不會像以往一樣再怎麼試都只會輸出 Detected photon data !)
    2. 成功試著打開 **"輸出 Volumetric data --save2pt"** 的開關，這個開關打開之後，outputtype 設成 energy density 或是 outputformat 設成 .mc2 就會有作用了!
    3. 另外 mcx 指令的 **--savedet, --savedetflag, --saveexit**，有一些設定會互相關連影響，要注意! 這些指令並沒有那麼獨立!
    4. 成功大致地，把 fluence_rate 的 jdata output 讀進 spyder，並利用 plt.imshow() 畫圖，不過僅是大概，畫的到底對不對，還要再確認!
    5. 但今天是有試著把 mcx_input_file 的一些指令關掉，之後可以試著去確認 **mcx_command** 與 **mcx_inputFile內的設定** 之間，哪一個優先權較高!
    6. 發現模擬還是需要 mus，至少要是 1，不然 mcx 不能正常做輸出。(看起來 mcx 是會先跑 wmc，再做 mua 的吸收計算。因為實際上在模擬的測試過程中發現，不管 mua 調多少，在 random seed 設一樣的情況下，detected photons 都會是一樣多)

## 2021/04/26 - source simulation 驗證規劃
### 方法
利用模擬吸收矩陣的方式，強迫光子均會在第一個 grid 以內就被吸收。然後與之前 ++量測得到的++ & ++模擬得到的++ power distribution 做比對(參考 0309, 0312, 0319 的 slide)。


### 流程
1. ==確認可跑==
2. ==確認驗證需要用的 mua==
    - 吸收 → 非常大、散射 → ~~0~~ <font color="red">1</font>。強迫光子幾乎於第一個格點就被吸收。因此需計算路徑長的 pdf，看看光子的路徑長分佈為何。可以設一個 threshold，例如 99.9% 以上的光子的第一個 random walk 都不會超出第 1 個 grid。(看起來需考量到光子的入射角以及 grid 的邊長)
3. ==重新檢查一次 mcx_core.cu, mcx_utils.c==
    - mcx_core.cu
        - 新增 radiated window 可以是圓形的狀況
        - 確認 code 有無錯誤
    - mcx_utils.c
        - 確認整體 code 的修改是否能 match 子佳的 mcxlab.cpp
        - 確認 code 有無錯誤
4. ==重新檢查一次 find LED cdf 的 code==
    - check inverse 的流程是否正確(內插求出 function ... etc)。
    - check code 有無錯誤。
5. ==重新檢查一次 find_power_distribution 的 code==
    - check 會除以 0 的狀況，並排除。
    - check code 有無錯誤。
    - 斜向入射的 $\cos{\theta}$ ？？
6. ==最後 mcx core 驗證==
    - 直接模擬光子於組織表面的吸收矩陣。
        - 此方法等同於用一種近似的方法觀看光子於組織表面的分佈(斜向入射的 $\cos{\theta}$ ？？)
    - 將++吸收矩陣++與先前++實驗量測到的++與++簡單電腦計算得到的++ power distribution on radiated window 作比較。
    - 需確認 source parameter 的單位，mm ?
    - 確認 source 的座標究竟是否能是浮點數，而不需要以 grid 為單位。

## 2021/04/23 - mcx_core.cu 修改（續）
20210730 補充：子佳當初的[修改記錄](https://github.com/kaoben2731/mcx/commit/27862d97fc080c229bf6a25392d0088ac6bb0701)。
1. 載了一個 額外的 package 後(記得是 zlib)，成功 compile 成 mcx bin。
2. kb's comment on meeting
    - fitting 的參數 → 血紅素濃度、epsilon 要可以 fit，因為不同人的血液本質可能不一樣
    - 要考慮到組織表面的收光面積，如果收光面積越大，模擬需要的光子數可能就越多，且空間的資訊會流失。
    - 硬體的材料可考慮要用哪一種。
    - 斜向入射：$\cos{\theta}$ ？？

## 2021/04/21 - mcx_core.cu 修改（續）
1. 為什麼需要
    ```c++
    CUDA_ASSERT(cudaMalloc((void **) &gsrcpattern, sizeof(float)*(int)(cfg->srcparam1.x+1)));
    CUDA_ASSERT(cudaMemcpy(gsrcpattern,cfg->srcpattern,sizeof(float)*(int)(cfg->srcparam1.x+1), cudaMemcpyHostToDevice));
    ```
    - gsrcpattern 是？
    - cfg->srcparam1.x+1 是？
2. Main Flow for launching new photon
    - **zenith angle** → $\theta$ (光子從 LED 射出後與 Z 的夾角, distributed according to the pdf of radiation pattern)
    - **azimuth** → $\phi$ (方位角，平面角，uniform distributed)
    - **Purpose**: Determine whether photon is launched into a legal window. If yes, then update photon position onto the surface being the initial position to start mcx simulation. (但主要的光子方向向量沒有旋轉，這是交給 mcx 內部的 rotatevector() 自行去旋轉的，我們做的只是更新光子的位置到組織表面)
    - **The following flow chart is translated to code** in launchnewphoton() function in mcx_core.cu.
```flow
st=>start: Start
e=>end: End
op1=>operation: Sampling azimuth, zenith angle
op2=>operation: Sampling launch position
uniformly in rectangle area
op3=>operation: Sampling azimuth, zenith angle
op4=>operation: Update photon position
op5=>operation: Sampling launch position
uniformly in circular area
op6=>operation: Sampling azimuth, zenith angle
op7=>operation: Use the legal launching angle
to update stheta, ctheta. And
then formally rotate the 
direction vector of the photon
cond1=>condition: LED panel is
rectangular ?|future
cond2=>condition: Will be launched to
radiated window ?
cond3=>condition: Will be launched to
radiated window ?

st->op1->cond1
cond1(yes)->op2
cond1(no)->op5->cond3
cond3(yes)->op4
cond3(no)->op6->op5
op2->cond2
cond2(yes)->op4->op7->e
cond2(no)->op3->op2
```

3. 待辦
    - 修改好 code
    - 驗證

## 2021/04/09 - mcx_core.cu 修改
- tab `else if(gcfg->srctype==MCX_SRC_ANGLEPATTERN)`
- `float4 srcparam1`、`float4 srcparam2`
    - 確認子佳設定的 `srcparam1.x` 是什麼 (length of angle array ?)
    - 與子佳討論後對 source 參數的想法, 可以==視整個 holder 為 source==, **新增 ↓**
        1. led_x, led_y, led_r
        2. win_x, win_y, win_r, led2win
    - 現行 source 的預定設定參數
        ```python
        srctype: MCX_SRC_ANGLEPATTERN
        srcpattern: sampled angle array
        srcparam1: {length of angle array (default=10000), 
                    led_x, 
                    led_y, 
                    led_r}
        srcparam2: {win_x, 
                    win_y, 
                    win_r, 
                    led2win}
        ```

## 2021/04/08 - mcx_core.cu 閱讀
閱讀記錄請參考 → [內部模擬 / 基本流程 / mcx_core.cu](https://hackmd.io/BvWQe1AjQqC7FLQSFD7qHg?both)

## 2021/03/26 - mcx_core.cu 修改方法規劃
[03/26 meeting slide](https://docs.google.com/presentation/d/1P1vdLg07-VwKTGUq6sBL51jp33TCREjlfhUxrP-lxPM/edit?usp=sharing)

1. sampling 光子發射位置 (coordinate on LED panel)
2. sampling 光子發射角度
3. 運算、判斷光子是否落於 radiated window 內
4. 參數：++光源至組織表面的距離++、++LED panel大小++、++radiated window大小++
5. 光源設置示意圖：
    - 3D
    ![](https://i.imgur.com/AA9LDSZ.png =80%x)
    
    - 2D
    ![](https://i.imgur.com/drEOFYc.png =80%x)
6. ==Kb's comment:== 
    - 需要注意 **radiated window 的參數**，要可以讓其他 project 使用的話，需要可以設定成**圓形、方形**…等等，所以需要**長、寬、半徑**…等等的參數
    - 可以看看其他的 source type 有沒有 sampling 發射位置相關的 code，然後再看如何 copy、借用、修改。
    - filter 實際上應該是比 window 大，所以 raidated window 以實際上 tissue surface 會收到光的面積為主就好。
    - 光在 filter 內的折射和反射對於 detector reflectance 的影響低，所以可以忽略。
    - 之後可以想想 detector 的個數(因應需要的 resolution), 因為光纖的數量與收光半徑大小是可以改變的。


## 2021/03/21 - source 量測與確認
[02/26 meeting slide](https://docs.google.com/presentation/d/1Rl2WWZq0WBaWBayeXv8FsLi9SmVT1LLvl96DrbbImYs/edit?usp=sharing) → 第一次發現會漏光
[03/09 meeting slide](https://docs.google.com/presentation/d/1Z6YO-HptSFnNQ2ZyCe2bMJpBtqxo-tlJoCtDWWL3IPc/edit?usp=sharing) → 第一次請祐祥用相機照，並看 gray value 變化趨勢。另外也試著用顯微鏡觀察 LED 發光情形。另外也試著用電腦模擬 LED 照到 radiated plane 應有的 power 分佈。
[03/12 meeting slide](https://docs.google.com/presentation/d/1ObdHPxEvi4rdOSzwr48NHa8qiQ5AQYZq-o54MIx2f2w/edit?usp=sharing) → source 均勻度量測。
[03/19 meeting slide](https://docs.google.com/presentation/d/18R92Ddgc2owg0txbxbn2D3mGxYD4oW8RslFYC0Yc4Hc/edit?usp=sharing) → source 均勻度量測(續)，並實際嘗試量測 LED 發光面積。


1. 從顯微鏡下看 LED plate 發光的區域面積
2. 直接以 LED 對相機的 sensor 拍攝，上次是有加透鏡(但應不能加)
3. 將 sensor 拍攝得的 profile 與模擬對照
4. 看子佳的 c++ 的 source code of new source case

## 2021/02/01 - source 設定
- 老師文件閱讀
    - 需要知道 die 的 size 嗎？還是就視為點光源？
    - 之前所學習到的 **source type**: uniform, gaussian，…etc，都是指 radiated surface 上 power density 的 pattern 嗎？
- C++ code 閱讀
- MCX readme

## 2021/01/20 - 重新 training ann 規劃（續）
暫時再整理一下流程，之後做時若發現一些細節再補上來。(詳細可參考 [2020/01/08](#20210108---重新-training-ann-規劃)，綜合 kb's comment)

==已完成==
1. transformed (a,b) 的 output。[01/22 meeting slide](https://docs.google.com/presentation/d/1B0IQbGEkFPc4i_vfeHFJAstePMlI4K8QEIQPLwc-_8o/edit?usp=sharing)。
    - ann 的訓練資料產生預計是由在 range 內的隨機 (a,b) 數值，而不是是澂原本使用的"直接 sampling mus"
    - <font color="red">問題：文獻上有 whole blood 的 musp ? 還有一些文獻的整理，目前交給昕原。(整理各組織 mus, mua)</font>
2. source 設定。[01/29 meeting slide](https://docs.google.com/presentation/d/1A8kIjFOpYw6AtN0y0CDpp5_T13hDKV98bnbTVSzOrqQ/edit?usp=sharing)。
    - LED 出光角
        - Typical FWHM Beam Angle (Table from datasheet)![](https://i.imgur.com/gWzMvCH.png)
        - Radiation Pattern Characteristics (Figure from datasheet)![](https://i.imgur.com/90x0fIq.png =50%x)
        - [Datasheet](https://www.lumileds.com/wp-content/uploads/files/DS263-luxeon-ir-onyx-datasheet.pdf)
    - LED 內光源與組織表面的實際距離
    - mcx code 設定
    - omlc gaussian beam example

==待做==
1. 需確認使用的 code template
2. 硬體: 安裝 gpu 3060

==簡易流程==
1. wmc
    - code template: xx
    - 需求: 隨機挑出不同的 (a,b) 進行模擬
3. calculate reflectance
    - code template: xx
5. ann training
    - code template: xx

## 2021/01/08 - 重新 training ann 規劃
[01/08 meeting slide](https://docs.google.com/presentation/d/1zXrJbGi_4mUiyscM3_glYi6kqLfC3-fxMmADk-GvbDY/edit?usp=sharing)

經過一系列的測試後，發現 ann 極有可能需要重新 training。(不過尚不知為何是澂的碩論 error 會如此低)

==**規劃**==
- wmc
    - 光學參數
        - 使用的 (a,b) 需於正常範圍
    - 幾何參數
        - 幾何結講設定 - 2人 (kb與昕原 or kb與我)
    - 系統(硬體)參數 - 確認硬體的設計符合wmc的設定
        - sds 可以多個
            - size 符合實驗
            - 可能不能重複(wmc default 的 code 記得是不能重疊的)
        - source 與組織表面的距離
            - led 的 location 與 orientation (led 發光後是否有 collimator 或是 filter，導致就算 led 與表面緊貼，光還是會經過一段距離才會到組織表面，另外出光角與方向也要考慮，要去查硬體規格!!)
        - prism 與組織表面可以塗一層膠(大腦計劃發現這樣會比較穩定)
        - detector 與組織表面的距離
            - 要查 prism 的規格，看是否反射面有 coating (看反射率會不會受**光的波長**或**入射角**的影響)
        - 確認 wmc 的第 0 層要設為空氣還是 detector、prism
            - 如果量測的環境是有光，那第 0 層也要是貼片(如果有貼片的話，也會造成收到的光產生衰減)
- calculate reflectance
    - 使用的 mua 需於正常範圍
- ann
    - input
        - 5 層組織的 mua, mus, 
        - 各層的 n, g(變為固定)
            - g 需參考文獻，看肌肉、ijv 的 g 值要設定成什麼
            - 或是 g 也能當作未知數去 fitting
        - **幾何形狀**
            - 全部固定
            - 部分不固定
                - ijv, cca 深度(也可以當作未知數)
                - ijv, cca 管徑(也可以當作未知數)
    - output
        - reflectance

==**目的**==
- 先跑一個小規模的模擬，確認 ann 的可用性
- 歸納不同光學參數所對應的特徵，觀察哪些光學參數需要較多的光子數 (還是需要知道 cv → 較可靠，因為 indicator 比較難找)

## 2020/12/25 - 大規模檢測 ann 穩定性（續）
[12/25 meeting slide](https://docs.google.com/presentation/d/1bD6YeTJTEdyBfSyRJzosjVwEBNptsDaUM3SsrARqmX0/edit?usp=sharing)

由於上週僅在跑完 wmc 之後測試一組 mua，所以可以再更進一步地去測試不同組的 mua，例如調整不同的 ijv SO2，然後再去看這些參數之下的光譜，到底是否能跟 ann 所輸出的光譜穩合。

詳細結果列於 12/25 meeting slide。

==待確認：==
- 檢查 code，確認 mc 與 ann 的差異是否根本是 code 寫錯導致的。
- 如果需要重 train，需要再列一份清單，看有哪些細節要確認。

## 2020/12/18 - 大規模檢測 ann 穩定性（續）
[12/18 meeting slide](https://docs.google.com/presentation/d/1AQ8vSngmffd0AuMoksLL2j0v-SQ1Q1FlNS7knkjNkfw/edit?usp=sharing)

整理 12/14 模擬結果。<font color="red">同時在調整身體組成比例時，發現換算後的 mua 難以符合 ann 的 training range</font>。

**解決方法 ↓**
再次調整血紅素濃度，產生 hemoglobin 濃度為 20 g/L 所相應的 mua，同時調整肌肉的含血量，使肌肉的吸收係數也落於 ann training range。(注意：在此比較不顧慮組織物質的組成比例是否落於正常的生理範圍，因為目標**僅**是要看 mc 與 ann 在相同的光學參數之下是否能夠 output 出一樣或幾乎近似的光譜 - ++數值上++與++形狀上++)。

詳細結果列於 12/18 meeting slide。

## 2020/12/14 - 大規模檢測 ann 穩定性（續）
進行 mc 模擬。**跑 5 個 mus 類別 (分別搭配一組隨機產生的 geo)。**
- wl: 680, 690, ..., 810 nm。
- g 需確認一下(已確認)
- parameters.json 修改 (mus, geo)：
    - mus 類別 ↓
        1. 均在範圍內
        2. 均在範圍內
        3. 僅 fat 超出
        4. 僅 muscle 超出
        5. fat, muscle 均超出
    - geo 類別
    與 mus 獨立，隨機產生。<font color="red">(不過可能先限制一下 cca 不應比 ijv 淺)</font>
- config.json 修改
- 光子數 1e9 重複 10 次，以得到穩定 reflectance。(相當於光子數為 1e10 之下的 reflectance、spectrum)

==待確認：==
- a, b 上下界的數值是否正確
- geo 的深淺是否有一些相依性（例如 cca 會比 ijv 淺？）

## 2020/12/03 - 大規模檢測 ann 穩定性
[12/04 meeting slide](https://docs.google.com/presentation/d/1eGaQ5ODXlFutubPIbhcQICtL3fN0kNQ24C35Z6I9EXU/edit?usp=sharing)

~~理想檢測: 取 2 種幾何組織(隨機？)，各自取 3 種散射組合。~~
理想檢測：假設人體的(a, b)是獨立的，然後兩者存在 continuous uniform joint distribution，意即不同人體的組織，落在不同的 (a, b) 數值的機率是相同的(隨機的)。那麼今天就可以隨機取幾個不同的(a, b)組合，並搭配隨機取出的幾何組織，來說他們是隨機抽出的不同的人的組織，接著進行 mc 模擬，看看 mc 模擬的結果，是否與 ann output 的結果一樣。

實作：
- 產生 5 個組織的 mus 與 1 個 tissue_geo，看看數值是否落在範圍(是或否都行，因為都是代表組織的一種可能性，只是 "否" 的話就代表 ann 沒有 cover 到)
- output 這 5 個 mus 背後的 (a,b) 與 tissue_geo 背後的 7 個參數數值(skin_thickness, ijv_depth ...etc) - **做為後續 mcx 運行所根據的檔案**

## 2020/11/27 - 檢查 ann 是否有效（續）
[11/27 meeting slide](https://docs.google.com/presentation/d/1zX-99CdeRMJyNxm4xXmBHJbaVgtDsnziUeQdNkLQfcg/edit#slide=id.gad96658c40_0_0)
- 確認 11/23 結果。(最終詳細結果列於 meeting slide)
    - (1) ann no cover 實驗 → 改採 11/20 的低光子數模擬。
    - (2) ann cover 實驗 → 11/27 重跑一次模擬：調整 fat、muscle 的 a, b，使跑 mc 時的組織 mus 符合 ann 的 training range；並避開 header["photon"] 的問題，使用低光子數進行模擬。(10 億顆重複 100 次，等效於 100 億重複 10 次)

## 2020/11/26 - 檢查 code
- na 複習，與稜鏡的關係？
    - 看起來 light source 距離 tissue surface 15mm 是因為稜鏡的關係。(++哲皓碩論：光源與偵測光纖束的探頭端均搭配邊長 5 mm 的等腰直角三稜鏡++)
    - 衍生問題：++如果 detector 端也有稜鏡++，這樣計算 reflectance 是否也要改變？(與平常不同)
        - →++看起來是沒有QQ++，而且 <font color="red">**detector 在跑 wmc 時還是被設定成緊貼組織表面(z=0)**</font>。
        - <font color="red">而且在跑 reflectance 的計算時，$\theta_{max}$ 的計算還是 detector 的 n 來當分母(理論上應該是要用空氣或組織的 n)。</font>
- 哲皓、胤甫、是澂碩論參考 → ++哲皓碩論：sds = 20mm++
- ann 參數設定是否符合 mcx 的參數設定？ → 確認：有。
    - mua
    - mus <font color="red">(不過什麼時候需要去訓練 high mus)</font>
    - n
    - g
- <font color="red">header 的 photon 存取怪怪的</font>

## 2020/11/25 - 檢查 ann 是否有效（續）
整理問題清單(for是澂)，計算 11/23 模擬之 reflectance 結果。
- [問題清單](https://docs.google.com/document/d/1lphknBw93OAAFuCb2bcFk0j6pH7du_M0QUBcZshjzEU/edit?usp=sharing)
- 11/23 模擬總結
    - (1) header["total_photon"] 數字錯誤，例如應為 100 億，結果只顯示 14 億，如此會導致 reflectance 被高估。因此<font color="red">此次模擬不可用</font>。
    - (2) mus 範圍沒檢查到，fat & muscle 的 mus 跑到 training range 外了，因此需重新 run mc。<font color="red">不過也因此發現 mus 的 training range 好像也有點奇怪。</font>

## 2020/11/23 - 檢查 ann 是否有效（續）
11/20 的光子數偏低，cv 是12.5%，因此仍需提高光子數試試。
做 2 個測試 → (1) ann 沒有 cover 到的 mua 是否與 MC 模擬相同。(2) ann 有 cover 到的 mua 是否與 MC 模擬相同。
- 跑 (1)，100 億顆重複 9 次 (有 1 次已等效於 11/20 跑的)，算 cv， wavelength → 750nm。
- 跑 (2)，100 億顆重複 10 次，算 cv，wavelength  → 680nm。

## 2020/11/20 - 檢查 ann 是否有效
試跑 ijv 模擬。
- 確認模擬前細節
    1. validateANN.json
    2. session_id
    3. type
    4. voxel_size
    5. medium_n
    6. detector_na
    7. coefficients.csv
    8. parameters (mua, mus, n, g checked, geometry checked, boundary checked which is for voxel = 0.1mm)
    9. mcx_input, mcx.py: not sure whether to uncomment set seed) <font color="red">need to quick test</font>
    10. fiber
    11. wavelength (++only 750nm++)
- 先用少量光子跑跑看
    1. 看是否能跑 (測試後：可！)
    2. 看是否隨機 (測試後：可！)
    3. 看看 1 億顆的時間
- 跑 10 億顆，並重複 10 次 ==(ann 沒有 cover 到的 mua)==
    1. 算 CV 值























