---
tags: IJV
---
# IJV | QEPro 環境安裝
Editor: 許逸翔 (R08)

## 1. 安裝軟體

### 1.1 Labview 與 NI Driver
**簡易流程** ↓
- Copy IJV 外接硬碟(5TB) 的 LabView 資料夾至你的 Windows 筆電中。
    - LabView 資料夾路徑：`/media/md703/Expansion/LabView`
- 確認已有下列 4 個映像檔
    - `NI_Academic_Site_License_Fall_2014_Disk01.iso`
    - `NI_Academic_Site_License_Fall_2014_Disk02.iso`
    - `NI_Academic_Site_License_Fall_2014_Disk03.iso`
    - `NI_Device_Driver.iso`
- 從 [安裝說明](https://drive.google.com/file/d/1t0nvhgb_GGh8mfT5cYSNmKepUR5YhmZD/view?usp=sharing) 的第 2 步開始接著做 (從Disk01.iso 開始按)，同時記下第一步圖片中的授權碼 (serial number)。

### 1.2 安裝 vision aquisition software
**簡易流程** ↓
- 進入網站 ([連結](https://www.ni.com/zh-tw/support/downloads/drivers/download.vision-acquisition-software.html#306474))
- 選擇 Version 17.5
- 下載
    ![](https://i.imgur.com/pnMHJOr.png)
    
### 1.3 安裝 QEPro driver - OmniDriver and SPAM
**簡易流程** ↓
- 進入網站 ([連結](https://www.oceaninsight.com/support/software-downloads/))
- 下載 OmniDriver and SPAM (Windows Version (32-bit)，因 Labview 也是 32-bit。
![](https://i.imgur.com/2hJsf55.png)

## 2. 使用軟體

### 2.1 啟動 labview 控制 QEPro
**方法**：
使用 `QEPROcontrol_version3.vi` 的檔案, 功能可以錄影，可以控制多久拍一張，可以輸出光譜檔案。

**可能存在問題**：打不開 v3 檔案，原因 → 找不到 net40.dll。
**解法**：指定路徑：
C:\Program Files (x86)\Ocean Optics\OmniDriver\OOI_HOME\net40.dll 給軟體。Solver: 林國聖(BOSI R08)


