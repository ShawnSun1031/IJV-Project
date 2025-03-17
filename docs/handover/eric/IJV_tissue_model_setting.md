---
tags: Lab
---
# IJV | 組織模型設定 July, 2021 - Revised

## 硬體設定
### i. 光源基本參數與模擬
- 實體圖
    ![](https://i.imgur.com/3r9wjYK.png =30%x)
- 規格
    1. 尺吋
        - Holder
            - 邊長: 28 mm
            - 中央出光孔半徑: 5 mm
    2. 折射率
        - Holder
            材質為 PLA，680-810nm 下的折射率如下圖。資料來源: [Optical Properties of Polylactides](https://link.springer.com/article/10.1007/s10924-006-0001-z)。
            ![](https://i.imgur.com/Xoohesg.png =70%x)
- MCX 之 Illumination pattern 模擬方式
    **以下方之 pattern 進行模擬(上學期間修改 mcx source code 之結果)**
        ![](https://i.imgur.com/zXNM25J.png =50%x)
    ***簡單驗證流程回顧(6月至7月初之進度)***
    1. 目標：mcx 模擬之 pattern 需與實驗拍攝之 pattern 一致 (符合真實情況)
    2. Pattern 比對之結果
        - 方法一：畫一條穿過影像中心點的直線，觀察模擬結果與實驗結果在此一直線上的變化趨勢是否一致。
            **`One of previous results ↓`**
            ![](https://i.imgur.com/TSCTuiY.png)
        - 方法二：觀察模擬結果與實驗結果的 average of gray value over the same radial distance 是否一致。
            **`One of previous results ↓`**
            ![](https://i.imgur.com/Dyt3gJ1.png)
    3. 結論
        在以上的兩個比對方法中，mcx 模擬之 pattern 與實驗拍攝之 pattern 皆具有一定程度之一致性，因此往後將以此 pattern 代表真實情況進行模擬。


### ii. 偵測器基本參數與模擬
- 實體圖
   ![](https://i.imgur.com/tbegJQD.jpg =30%x)
- 規格
    1. 尺吋
        -  Holder
            - 長邊: 14.06 mm
            - 短邊: 12.13 mm
        -  Prism
            - 邊長 5 mm 之等腰直角三角形
    2. 折射率
        - Holder
            材質亦為 PLA，因此折射率與光源之 Holder 相同。
        - Prism
            稜鏡型號為 → [PS909, THORLAB](https://www.thorlabs.com/thorproduct.cfm?partnumber=PS909)，與胤甫、哲皓使用的型號相同。材質為 N-BK7。折射率計算公式(Sellmeier Equation)如下圖。資料來自於[來源](https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=6973&tabname=n-bk7)。
        ![](https://i.imgur.com/7fz6j2E.png)
        上述之公式的 unit of λ 為 μm。而另一個可供參考之折射率資料位於此[網站](https://refractiveindex.info/?shelf=glass&book=BK7&page=SCHOTT) (given by THORLAB Tech Support)。因此，透過 Sellmeier Equation 的計算，我們可得 680-810nm 下的折射率如下圖
        ![](https://i.imgur.com/MgVZXHs.png =80%x)
- 光纖 full acceptance angle 之計算
    - 數值孔徑, NA
        根據老師提供的資料，我們所使用的光纖NA為==0.22==。
        ![](https://i.imgur.com/0cHEja6.png)
    - 計算流程
        光纖的 full acceptance angle 計算公式為 2 x sin^-1^(NA/n_prism)，代入不同波長下的 n_prism，可見下圖的涵蓋範圍。
        ![](https://i.imgur.com/Pkht01B.png =80%x)
- 稜鏡尺吋的適合度驗算
    ![](https://i.imgur.com/K2oewyO.jpg)
- MCX 之模擬方式：
    於 MCX 內，我們以 **`將 Prism 與 PLA 皆視為組織的方式進行模擬`**，避開於 source code 中調整 detector 高度的問題。MCX 之模擬示意圖如下。
    ![](https://i.imgur.com/7WYy5VE.png)
    對照之真實情況示意圖如下。(並未 follow 真正擺設之方向)
            ![](https://i.imgur.com/FHAhQav.png)


### iii. 探頭量測之完整擺設
- 探頭擺設方向：位於 ijv 正上方、與 ijv 平行
- 局部示意圖，聚焦於硬體的擺設，探頭下方僅含一層組織。(利用 MCX 作者近期開發的 [MCX Cloud](http://mcx.space/#cloud) 中的 Preview 功能繪製)
    ![](https://i.imgur.com/gjUMd1A.png =75%x)
    **簡易三視圖 ↓**
    1. 俯視圖
        ![](https://i.imgur.com/o9raar0.png =50%x)
    2. 前視圖
        ![](https://i.imgur.com/hukeURT.png =50%x)
    3. 側視圖
        ![](https://i.imgur.com/6s90P6M.png =50%x)
- 整體示意圖，探頭下方含完整組織。
    ![](https://i.imgur.com/o9R535g.png =75%x)


## 幾何參數設定
1. 昕原
    - Upper neck
        ![](https://i.imgur.com/NtrVnun.png =50%x)
    - Middle neck
        ![](https://i.imgur.com/rLL3hSf.png =50%x)
    - Lower neck
        ![](https://i.imgur.com/lsPvjJU.png =50%x)

3. 逸翔
    - Upper neck
        ![](https://i.imgur.com/bMmEfFT.png =50%x)
    - Middle neck
        ![](https://i.imgur.com/P9VXPCt.png =50%x)
    - Lower neck
        ![](https://i.imgur.com/vavhOqy.png =50%x)


## 光學參數設定
1. Background layer
2. 1st layer
3. 2nd layer

## 相關問題
### 1. MCX 細節參數設定
- Boundary reflect → No
### 2. 模型大小 (長、寬、高)
### 3. detector 可以有 2 個？
### 4. 實驗發現稜鏡影響穩定度
### 5. 靜脈半徑計算 → (長邊+短邊)/2

## 後續
1. 測試模型多大才不會影響 reflectance
2. 測試多個 sds 會不會影響 reflectance、計算反射率差異

