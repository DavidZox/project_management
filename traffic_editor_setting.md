# Open-RMF Traffic Editor 獨立使用與架構說明指南

本指南說明如何將 Open-RMF 中的 **Traffic Editor** 作為獨立的 2D 拓撲地圖/路徑繪製工具進行編譯、部署與商業應用，並針對 `.building.yaml` 內部資料格式與比例尺校正機制進行詳細解析。

---

## 1. 軟體簡介與授權條款

* **專案名稱**：`rmf_traffic_editor`
* **開源授權**：**Apache License 2.0**
* **商業應用**：
  * **完全允許商業使用**：可閉源、改寫 UI、嵌入自家產品或專利軟體中。
  * **獨立性**：完全不需運行 Open-RMF 核心系統（Fleet Adapter / Core），可單獨作為離線（Offline）地圖編輯器。
  * **合規要求**：僅需在軟體說明或關於頁面中保留原著作權聲明（OSRF / Apache 2.0）。

---

## 2. 環境安裝與編譯

`traffic_editor` 擁有獨立的 Git 儲存庫，可單獨於 ROS 2 環境中進行 Colcon 編譯。

### 步驟 1：安裝基礎系統依賴
```bash
sudo apt update
sudo apt install -y libyaml-cpp-dev qtbase5-dev libopencv-dev libopencv-videoio-dev libceres-dev
```
---

### 2：複製專案與編譯
```bash
# 建立工作區
mkdir -p ~/traffic_editor_ws/src
cd ~/traffic_editor_ws/src

# 複製 Traffic Editor 原始碼（如缺少 rmf_utils，一併拉取或透過 APT 安裝）
git clone [https://github.com/open-rmf/rmf_traffic_editor.git](https://github.com/open-rmf/rmf_traffic_editor.git)
git clone [https://github.com/open-rmf/rmf_utils.git](https://github.com/open-rmf/rmf_utils.git)

# 自動補齊剩餘 ROS 依賴項
cd ~/traffic_editor_ws
rosdep update
rosdep install --from-paths src --ignore-src -r -y

# 編譯專案
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build
```
*注意（編譯警告）：編譯過程中出現 sprintf 或 dangling-pointer 等 Warning 屬於 GCC/Qt 版本演進警告，只要最後顯示 Summary: X packages finished 即代表成功編譯完成。*

---

### 3. 獨立啟動與使用流程
```bash
cd ~/traffic_editor_ws
source install/setup.bash
traffic-editor
```

---

## 4. 底圖（.pgm / .png）匯入與比例尺校正流程

Traffic Editor 不需要 ROS 導航原本的 `map.yaml` metadata（如 `resolution`、`origin`），其圖資匯入與實體尺寸校正完全由軟體內部完成。

### 操作步驟

*轉換圖片格式（建議）*
由於部分 Qt 環境對 `.pgm` 支援度較差，建議先將底圖轉換為 `.png` 格式：
```bash
sudo apt install imagemagick
convert your_map.pgm your_map.png
```

### 建立樓層與載入底圖
* 在 Traffic Editor 中選擇 `Edit` -> `Building Properties`。
* 點擊 `Add` 新增樓層（如 `L1`，`Elevation` 設為 `0.0`）並點擊 `OK`。
* **關鍵**：在 Levels 列表中**雙擊（Double Click）`L1`** 進入完整的 **Level Properties** 視窗。
* 在 `Drawing filename` 選擇您的 `.png` 底圖檔案。

### 專案存檔（相對路徑約束）
* 點擊 `File` -> `Save As...`，將專案儲存為 `.building.yaml`。
* **必須將 `.building.yaml` 與 `.png` 檔案存放在「同一個資料夾」**，以確保相對路徑解析正確。

### 比例尺校正（Measurement Line）
* 點擊工具列的 `Add Measurement`，在底圖已知長度位置拉出一條尺寸線。
* 切換至 `Select (S)` 模式，點擊該條測量線。
* 在下方 **Properties** 面板的 **`distance`** 欄位輸入真實公尺數（例如 `3.0`）。

### 刷新比例尺（Scale Update）
* 修改 `distance` 後，Qt GUI 可能存在視圖延遲。按下 `Ctrl + S` 儲存後，按 **`Ctrl + O` 重新開啟 YAML** 或**切換樓層**，即可強制觸發頂部 `Scale (meters/pixel)` 重新計算與畫面重畫。

---

## 5. YAML 資料結構解析與常見踩坑點

Traffic Editor 導出的 `.building.yaml` 將所有物件屬性定義為 **`[數值, 型別代碼]`** 的 Tuple 結構：

```yaml
# 原始 YAML 結構範例：
levels:
  L1:
    drawing:
      filename: your_map.png
    measurements:
      - [0, 2, {distance: [3, 3]}]  # [起點ID, 終點ID, {屬性: [數值, 型別代碼]}]
```

### `distance` 屬性中的型別代碼（Type Tag）說明

C++ 內部源碼（`param.h`）定義了以下數據型別代碼：

* `1` = `STRING` / `INT` (未指定或字串)
* `2` = `INT` (整數)
* `3` = `DOUBLE` / `FLOAT` (雙精度浮點數)
* `4` = `BOOL` (布林值)

#### 常見錯誤問題（比例尺跑掉）：
* **`distance: [3, 1]`**：手動編輯或輸入時被判別為整數或字串型別，導致開啟檔案時 C++ 程式 `as<double>()` 解析失敗，無法正確獲取長度，進而造成 Scale 重置為預設值（比例跑掉）。
* **`distance: [3, 3]`**：型別代碼為 **`3`**，系統能正確將數值轉換為 `double` 浮點數公尺值。

> **解決方案**：在 GUI 中輸入長度時請帶上記號（如 `3.0`），或手動編輯 YAML 時確保 `distance` 後方的型別代碼固定為 **`3`**。

---

## 6.比例尺（Scale）同步運算與 GUI 視圖刷屏機制

### 1. Scale 與 Measurement 欄位屬性解讀

在 Traffic Editor 的 UI 介面中，上方樓層列表與下方屬性面板（Properties）為同步連動關係：

* **Scale（公尺/像素）**：位於上方樓層表格（如 `t_1`），代表該樓層最終套用的繪圖比例尺。
* **`length (m)`**：位於下方 Properties 面板，代表根據當前 Scale 算出該測量線段的物理長度（計算公式：$\text{像素距離} \times \text{當前 Scale}$）。
* **`distance`**：位於下方 Properties 面板，代表使用者定義的真實公尺數（目標長度）。

#### 雙向同步邏輯
* **修改下方 `distance` $\rightarrow$ 連動上方 `Scale`**：
  在下方輸入實際公尺數（例如 `3`）並按下 Enter 後，系統依據以下公式計算新比例尺：
  $$\text{Scale (公尺/像素)} = \frac{\text{下方的 distance (公尺)}}{\text{測量線在圖片上的像素長度 (Pixels)}}$$
* **修改上方 `Scale` $\rightarrow$ 連動下方 `length (m)`**：
  點擊上方樓層右側的 `Edit...` 手動修改 `Scale` 時，下方的 `length (m)` 會隨之縮放改變。

---

### 2. GUI 視圖渲染延遲與重載機制

在 GUI 中修改 `distance` 後，若上方 `Scale` 未即時變更，此為 Qt 視圖監聽未觸發的已知現象（Re-render Delay）。

#### 延遲原因
1. **數據已更新，UI 未重畫**：按下 Enter 時，記憶體數據已完成更新，但 Qt 介面的視圖刷新函式未被觸發。
2. **檔案載入觸發重新計算**：重新載入專案時，Traffic Editor 會執行完整的初始化流程，讀取 `distance` 並調用內部 `recalculate_scale()` 函式，介面上才會顯示最新 `Scale`。

#### 快速刷新技巧（無需重開程式）
* **快捷鍵重新載入**：按下 `Ctrl + S` 儲存後，直接按下 `Ctrl + O` 重新開啟同一個 `.building.yaml` 檔案。
* **切換樓層（Level Switch）**：若專案包含多個樓層，切換至其他 Level 再切換回原樓層，即可強制觸發繪圖參數與 Scale 的重新計算。

---

### 3. 校正驗證方式

修改下方的 `distance` 並按下 Enter 鍵後（或完成快速刷新），檢查上方樓層列表中對應的 `Scale` 數值是否已隨之變動；數值更新即代表比例尺校正完成。