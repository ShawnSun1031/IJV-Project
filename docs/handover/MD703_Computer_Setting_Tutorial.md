## 1. [Linux] Ubuntu 18.04系統下安裝 Anaconda, follow 這個網站的步驟即可。
https://ithelp.ithome.com.tw/m/articles/10290542
## 2. 一些conda 環境配置指令:
`conda create --name test python=3.8`  創建一個名字為”test” python版本為3.8的虛擬環境
![](https://hackmd.io/_uploads/rkqZh3AJ6.png)
`conda list` 該虛擬環境下所已經安裝的套件(package)
![](https://hackmd.io/_uploads/Bkdji301a.png)
`conda install spyder` 安裝spyder這個套件，輸入`spyder` 打開spyer IDE
![](https://hackmd.io/_uploads/HyGv32AJa.png)
`conda deactivate` 退出此虛擬環境
`conda env list` 顯示現在有的虛擬環境(如圖有base、test這兩個環境)
![](https://hackmd.io/_uploads/S1cP6nCyp.png)
conda remove -n test --all 刪除"test"這個虛擬環境
![](https://hackmd.io/_uploads/HyKCT3Ryp.png)
如上圖此時"test"這個虛擬環境已經刪除。
## 3. cuda安裝，follow nvidia官網，看你是要裝甚麼版本的，此範例安裝版本為cuda11.7，https://developer.nvidia.com/cuda-11-7-0-download-archive?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=18.04&target_type=deb_local
![](https://hackmd.io/_uploads/SkjIkTC1T.png)
在裝的時候他會問你設定mok金鑰，輸入自己設定的密碼後重開機，會進入enroll畫面，選擇MOK記得輸入剛剛設定的密碼。
![](https://hackmd.io/_uploads/S1htZpC1a.png)
若是不幸操作錯誤按到continue boot，電腦直接開機，沒有enroll到的話，直接在terminal輸入 `sudo mokutil --import /var/lib/shim-signed/mok/MOK.der` 即可，詳細問題的發生內容以及解法參照[https://askubuntu.com/questions/1122855/mok-manager-nvidia-driver-issue-after-cuda-install](https://askubuntu.com/questions/1122855/mok-manager-nvidia-driver-issue-after-cuda-install)
當cuda裝好後，使用 `nvidia-smi` 可以查看gpu的情況，若是有出現東西就表示裝成功了。
![](https://hackmd.io/_uploads/H13rM6R16.png)
## 4. 在使用實驗室電腦的時候，除了配置屬於自己的虛擬環境外，最好在空間足夠的硬碟(disk)創建自己的資料夾，把自己的東西固定當放在裡面，不然到時候東一個西一個甚至跟別人的東西混雜在一起會很不方便。所以先選一個空間足夠的硬碟
![](https://hackmd.io/_uploads/Hyr_mpRJ6.png)
![](https://hackmd.io/_uploads/BJcsDaRJ6.png)

## 5. pytorch 安裝
到pytorch官方網站[https://pytorch.org/](https://pytorch.org/)。
選擇相對應的選項(範例使用pip安裝pytorch，並且選擇的是CUDA11.7的版本)
![](https://hackmd.io/_uploads/H12lH7kxa.png)


