ART( Athlete Analysis of Real Time Sports Events ) Documentation
+ ## 導覽
    + [System documentation 系統文件](#System-documentation-系統文件)
        + [Reuqirements document 需求文件](#Reuqirements-document-需求文件)
        + [User Experience Design documentation 使用者體驗設計文件](#User-Experience-Design-documentation-使用者體驗設計文件)
        + [Software architecture design 軟體架構設計](#Software-architecture-design-軟體架構設計)
        + [Source code 程式原始碼](#Source-code-程式原始碼)
        + [Verification and Testing document 驗證和測試文件](#Verification-and-Testing-document-驗證和測試文件)
        + [API documentation API文件](#API-documentation-API文件)
+ ## System documentation 系統文件
    + 系統版本號: NaN
    + 文件狀態: 持續更新中
        + feature_GUI: 6c934b8
        + develop: 931da5f
        + master: 5185588
    + 文件擁有者: [ambersun1234](https://github.com/ambersun1234)
    + 開發者: [ambersun1234](https://github.com/ambersun1234), [louisme87](https://github.com/louisme87)
    + QA: [ambersun1234](https://github.com/ambersun1234), [louisme87](https://github.com/louisme87)
    + 專案原始碼位置: [AART](https://github.com/ambersun1234/AART)
    + ### Reuqirements document 需求文件
        + #### 系統需求
            |#|安裝名稱|必要性|備註|
            |:--:|:--:|:--:|:--:|
            |1|Ubuntu 16.04|是|作業系統必須為linux based, 建議為Ubuntu|
            |2|[Openpose fe767ala](https://github.com/CMU-Perceptual-Computing-Lab/openpose)|是|為本系統必要之第三方套件|
            |3|[Caffe](https://github.com/CMU-Perceptual-Computing-Lab/caffe)|是|為OpenPose必要之第三方套件|
            |4|Opencv 3.4.3|是|
            |5|wxpython 4.0.4|是|為GUI套件, 透過`sudo pip3 install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-16.04 wxpython`進行安裝|
            |6|numpy 1.15.1|是|程式碼相依套件|
            |7|gstreamer1.0-libav|是|Ubuntu 影音播放套件, 透過`sudo apt install gstreamer1.0-libav`安裝|
            |8|pycodestyle|否|PEP8 coding style檢查工具|
            |9|autopep8|否|自動格式化為PEP8形式之程式碼工具|
        + #### 系統非功能性需求

        |非功能性需求編號|非功能性需求描述|
        |:--:|:--|
        |AART-NF-001 畫面的穩定輸出|程式的優化：我們利用了現今消費級顯示卡中數一數二的顯示卡作為本次專題所需之神經網路加速使用，但神經網路的運算量實在過於龐大，因此當我們輸入 FPS 30 的原始影片並經過神經網路後 FPS 可能就會降至 5 左右，因此我們希望在所有計算都完成後 FPS 僅會再下降 1 以內|
        |AART-NF-002 一目了然|表格化的介面：為了使我們在製作時方便檢視，並使的使用者可以在程式執行時可以加以檢視程式的執行狀況，我們會將：<br>1. 輸入的影片<br>2. 各個人的身體骨架的影片<br>3. 偵測到特殊動作時所需輸出的文字<br>4. 讓使用者可以隨時切換想特別關注的人的背號四項同步顯示於視窗上|
        |AART-NF-003 切換語系所需時間|盡可能地快：讓切換語系功能能在選擇後的 1 秒內執行完畢|
        
        + #### 系統功能性需求

        |系統功能性需求編號|系統功能需求描述|
        |:--:|:--|
        |AART-F-001 偵測投籃姿勢|偵測球員是否為投籃的姿勢，是，則輸出"OOO投出了一球"等文字至視窗上|
        |AART-F-002 偵測運球姿勢|偵測球員是否為運球的姿勢，是，則輸出"OOO正在運球"等文字至視窗上|
        |AART-F-003 偵測上籃姿勢|偵測球員是否為上籃的姿勢，是，則輸出"OOO上籃了"等文字至視窗上|
        |AART-F-004 輸入文字|讓使用者輸入想追蹤的人之背號，一次最多可同時追蹤三個號碼|
        |AART-F-005 鎖定特定人物|追蹤使用者輸入的人，並對此人動作加以判斷|
        |AART-F-006 即時輸出偵測到的動作|將偵測到的各種姿勢即時輸出到視窗中的文字輸出方塊|
        |AART-F-007 語系切換|提供中英語系的切換功能|
        |AART-F-008 影片操作|提供對影片的暫停與繼續進行操作|

    + ### User Experience Design documentation 使用者體驗設計文件
        + #### 系統功能操作使用案例
        + ![](https://i.imgur.com/v6i3ljj.png)

        |使用案例編號|使用案例名稱|
        |:--:|:--:|
        |AART-UC001|使用影片作為本程式之輸入以追蹤特定人物|
        |系統反應動作|使用者操作動作|
        |a. 顯示歡迎畫面||
        ||b. 從左上角點選輸入影片( webcam )，已導入影片|
        |c. 視窗左上角開始播放原始影片(圖一原影片處)||
        ||d. 在右下角區塊輸入想要特別觀看的人的背號|
        |e. 左下角區塊改為指輸出指定的變號||
        
        |使用案例編號|使用案例名稱|
        |:--:|:--:|
        |AART-UC002|使用影片作為本程式之輸入以追蹤所有人|
        |系統反應動作|使用者操作動作|
        |a. 顯示歡迎畫面||
        ||b. 從左上角點選輸入影片( webcam )，已導入影片|
        |c. 視窗左上角開始播放原始影片(圖一原影片處)||
        ||d. 在右下角區塊輸入想要特別觀看的人的背號|
        |e. 左下角區塊改為指輸出指定的變號||
        
        |使用案例編號|使用案例名稱|
        |:--:|:--:|
        |AART-UC003|使用webcam作為本程式之輸入以追蹤特定人物|
        |系統反應動作|使用者操作動作|
        |a. 顯示歡迎畫面||
        ||b. 從左上角點選輸入影片( webcam )，已導入影片|
        |c. 視窗左上角開始播放原始影片(圖一原影片處)||
        
        |使用案例編號|使用案例名稱|
        |:--:|:--:|
        |AART-UC004|使用webcam作為本程式之輸入以追蹤所有人|
        |系統反應動作|使用者操作動作|
        |a. 顯示歡迎畫面||
        ||b. 從左上角點選輸入影片( webcam )，已導入影片|
        |c. 視窗左上角開始播放原始影片(圖一原影片處)||
    + ### Software architecture design 軟體架構設計
    + ### Source code 程式原始碼
        + 詳細程式碼位於 [AART](https://github.com/ambersun1234/AART)
        + 本軟體有如下物件分別位於以下module
            + src/main.py
                + `Frame`
            + src/device/device.py
                + `SelectDeviceDialog`
                + `DeviceCheck`
            + src/input/input.py
                + `InputPanel`
            + src/output/output.py
                + `outputTextPanel`
                + `outputPicPanel`
            + src/media/media.py
                + `previewCamera`
                + `MediaPanel`
                + `StaticText`
    + ### Verification and Testing document 驗證和測試文件
        + integration test on neural network
        + unit test on GUI
        + deploy on travis.ci
    + ### API documentation API文件
        + #### src/fetch.sh
            + 輸入: 無
            + 輸出: 該裝置上所有的video裝置
            + 輸出格式: 裝置ID|裝置ID|裝置ID@裝置名稱|裝置名稱|裝置名稱
                + 回傳值為`純字串`，需要使用python進行基本的字串處理
        + #### class xxxx.xxxx function
            + 輸入:
                + 輸入模式: 0與1
                    + 型態: `integer`
                    + 0: 無特定追蹤人員，全輸出
                    + 1: 有指定特定追蹤人員，輸入最多3名
                + 原始輸入照片
                    + 型態: `numpy ndarray`
                + 追蹤的dict()
                    + 型態: `dict()`, key: `string`, value: `integer` or `string`
                    + e.g. `{"person1": "11(號)"}`
                    + 大小最多為3，最小為0
            + 輸出:
                + 狀態: 0與1
                    + 型態: `integer`
                    + 0: 正常
                    + 1: 出現錯誤
                + 追蹤的照片的dict()
                    + 型態: `dict()`, key: `integer` or `string`, value: `numpy.ndarray`
                    + e.g. `{"11(號)": numpy.ndarray}`
                    + 大小無上限，最小為0
                + 追蹤的人姿勢的dict()
                    + 型態: `dict()`, key: `integer` or `string`, value: `string`
                    + e.g. `{"11(號)": "投球"}`
                    + 大小無上限，最小為0
