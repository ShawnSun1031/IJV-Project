---
tags: Lab
---
# IJV | 目前holder設計圖、活體量測注意事項

## Current holders and molds (tinkercad)
- [連結](https://www.tinkercad.com/things/jXQ2XruECrh-md703-ijv-holders-and-molds/edit?sharecode=6JOvnRu4RYYhRP8T4h7aiLnMmsYloP7zZGMwOsqz-rc)

## Measurement Memo
- Procedure
    - 開啟 LED 光源 (至少 10 分鐘後再開始量測，確保光強是穩定的)
    - 超音波操作
        1. 受測者平躺，頭部朝上，target 為右頸 ijv
        2. 超音波探頭來回移動，找出正確 ijv 位置與 ijv 走勢平緩的區域
        3. 貼上 ijv 平緩處的兩端標記
        4. 看需求，可以記錄一下此受試者的 ijv 影像 (錄影、事後用 imageJ 分析幾何參數)
    - 貼上探頭
        1. 清除超音波導膠，使用酒精清潔皮膚表面(油脂)
        2. 撕除 ok 繃上雙面膠布之背膠
        3. 抓好 source, detector 位置，貼上 ok 繃
        4. 微調 ok 繃，確認 source, detector 置於 ijv 正上方
        5. 確保 prism 和皮膚之間有超音波 gel (for index-match)
    - 確認 labview 曝光時間是否為 0.1 s
    - 確認訊號是否平穩
        1. 上方 window 的整體光譜訊號是否平穩
        2. 左下角的 window 是否有看見 CVP 波形 (全波長平均的倒數)
        3. 右下角的 window 呈現的是 delta_R / R (800nm 處，也是訊號最大值處)
    - 開始依據感興趣之 sds 進行量測
    - 若是血氧調變實驗，可觀察 760 nm 處的波形(如果由平滑變凹陷，可初步視為血氧下降的證據)

- Note
    - 實驗端
        1. for index-match 的 gel 不要太多也不要太少，並注意可能會乾掉的問題，量測過程需注意，若乾掉需添加 gel
        2. 注意量測過程中，超音波導膠不要沾到 ok 繃上之雙面膠布
        3. ok 繃需盡量與皮膚黏貼緊密、平整
        4. ok 繃上雙面膠布之背膠可在 ok 繃黏貼至皮膚前預先撕除，ok 繃黏後會較難撕除
    - 3D 列印端
        1. support (支撐) 的 infill pattern 可選擇 line，infill density 可選擇 100%。大面積的懸空表面會較平整。
        2. detector holder 印完後 fiber 端會較緊，可先確認 fiber 是否能接至 holder 底端
