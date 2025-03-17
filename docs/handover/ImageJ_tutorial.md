# ImageJ 教學：分析超音波影像
> [name=dicky1031][time=Fri, Oct 6, 2023 5:57 PM][color=#1aba0e]

## 下載ImageJ
到官網下載相對應的應用程式 https://imagej.nih.gov/ij/download.html  
![](https://hackmd.io/_uploads/rywAc86gp.png) 

打開ImageJ  
![](https://hackmd.io/_uploads/Sy0epIpxp.png)

## 操作步驟
### 匯入超音波影像
File -> Open 
### 找出比例尺
使用straight line把圖上的10mm部分畫出來
![](https://hackmd.io/_uploads/BkIFCUpeT.png)

Analyze --> Set Scale  
![](https://hackmd.io/_uploads/HJjlbPplp.png)  
此時如圖上所示，程式告訴你這段長度等於107.0047個pixels，  
這時把known distance填 10  
unit of length 填 mm  
接著按ok  
![](https://hackmd.io/_uploads/Hy3DWD6gT.png)  

### 量測IJV長短軸
選用直線，在長軸短軸畫出來後，Analyze-->Measure(快捷鍵Ctrl+M)來量測長度  
![](https://hackmd.io/_uploads/rknhWvTxT.png)
![](https://hackmd.io/_uploads/r1GJzw6ep.png)


## 延伸閱讀
1. [ImageJ 教學：分析光譜照片](https://hackmd.io/@yizhewang/BkRtEa0VN#%E5%BB%B6%E4%BC%B8%E9%96%B1%E8%AE%80)


---

###### tags : `ImageJ`