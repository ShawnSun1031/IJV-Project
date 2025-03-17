# MD703 3D繪圖與3D列印教學

###### tags: `實驗室管理`

Editor: 許逸翔(R08)

一般印出實驗室要用到的探頭(probe holder)需要經過 2 個步驟 → **3D 繪圖**與 **3D 列印**。**3D 繪圖**的目的是設計探頭的規格，包含大小、孔洞…等等。**3D 列印**的目的是將繪製好的設計圖印出成型，印出的物品能直接用於相關實驗。

## 3D 繪圖
1. 工具：[Tinkercad](https://www.tinkercad.com/dashboard)
2. 主要使用功能：群組、挖孔、大小調整解析度設定
3. 繪圖後的檔案輸出格式：.stl
4. 相關教學網站：
    - [基本功能介紹](https://sites.google.com/a/jbps.ttct.edu.tw/3d-lie-yin-ke-cheng/09dui-qi-yu-qie-ge)
    - [實用小技巧](https://www.xteach.net/wecourseware/4ed806d2-6690-11e9-864f-0242c0a81002)

## 3D 列印
1. 輸入檔案：吃前述提到的 .stl 檔。
2. 輸出檔案：確認完 3D 列印的參數沒問題後輸出為 .gcode 檔。
3. 3D 列印重要參數 (for black PLA - spyder)
    - 噴頭溫度：220°C
    - 平台溫度：50°C
    - 列印品質：super quality
    - 填充密度：小 holder 可以設為 100%
    - 支撐密度：小 holder 可以設為 100%
    - 支撐填充形態：line
4. 軟體與 3D 列印機使用方法：[子佳文件](https://docs.google.com/document/d/12ADjYwN-y1Bsul9udg6LIXKWmVShLo9nLkZFtRd8rvs/edit?usp=sharing)