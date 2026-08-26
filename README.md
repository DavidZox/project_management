# ROS 2 多專案切換部署架構 (Multi-Project Deployment Framework)

本專案提供一套基於 `colcon.mixin` 與 `colcon.meta` 的標準化部署架構，實現**單一工作區（Workspace）切換不同車型／專案**的建置需求。

---

## 核心設計理念

1. **`colcon.mixin` (Packages 篩選)**：控制 CLI 命令，決定目前專案僅需編譯哪些功能套件，未選中的套件會自動忽略。
2. **`colcon.*.meta` (參數注入)**：將專案專屬變數（如 `DEPLOY_PROJECT_NAME`、`ROS_DOMAIN_ID` 與啟動腳本名稱）注入給 `deploy_manager` 套件。
3. **`deploy_manager` (環境與腳本自動化)**：透過 CMake 生成專屬 Environment Hook，當使用者執行 `source install/setup.bash` 時，自動寫入環境變數並執行對應的硬體初始化 Shell 腳本。

---

## 目錄與檔案結構

```text
ros2_ws/
├── colcon.mixin                            # [Mixin] 定義專案對應要編譯的 Packages
├── colcon.amr.meta                         # [Meta]  AMR 專案變數 (Domain ID: 10, Script: amr_init.sh)
├── colcon.agv.meta                         # [Meta]  AGV 專案變數 (Domain ID: 20, Script: agv_init.sh)
└── src/
    └── deploy_manager/                     # 部署管理套件[cite: 5]
        ├── CMakeLists.txt                  # 處理 Meta 參數輸入、生成 Hook 與安裝腳本
        ├── package.xml                     # 套件描述檔[cite: 5]
        ├── env-hooks/
        │   └── project_hook.sh.in          # Environment Hook 範本檔
        └── scripts/
            ├── amr_init.sh                 # AMR 硬體與雷達初始化腳本
            └── agv_init.sh                 # AGV 巡線感測器初始化腳本
```

## 檔案職責說明

| 檔案名稱 | 職責與說明 |
| :--- | :--- |
| **`colcon.mixin`** | 定義 `--mixin AMR_Project` 與 `--mixin AGV_Project`，指定要建置的 Package 清單。 |
| **`colcon.amr.meta`** | 設定 `deploy_manager` 的 CMake 參數：`-DDEPLOY_PROJECT_NAME=AMR_Project`、`-DROS_DOMAIN_ID=10`、`-DTARGET_SCRIPT=amr_init.sh`[cite: 2]。 |
| **`colcon.agv.meta`** | 設定 `deploy_manager` 的 CMake 參數：`-DDEPLOY_PROJECT_NAME=AGV_Project`、`-DROS_DOMAIN_ID=20`、`-DTARGET_SCRIPT=agv_init.sh`[cite: 1]。 |
| **`CMakeLists.txt`** | 接收 Meta 帶入的參數，使用 `configure_file` 注入 `project_hook.sh.in` 並註冊為 ROS 2 載入點[cite: 4]。 |
| **`project_hook.sh.in`** | Shell Hook 範本，當環境被 `source` 時自動設定 `ROS_DOMAIN_ID` 並執行目標腳本。 |

---

## CLI 操作指南

### 1. 切換與建置 AMR 專案 (自主移動機器人)

只會編譯 `pkg_amr_nav` 與 `deploy_manager`：

```bash
# 1. 執行建置 (指定 AMR Mixin 與 AMR Meta)
colcon build --mixin-files colcon.mixin --mixin AMR_Project --metas colcon.amr.meta --cmake-force-configure

# 2. 載入環境變數 (自動觸發 amr_init.sh)
source install/setup.bash

# 3. 驗證環境變數
echo $ROS_DOMAIN_ID
# 預期輸出: 10
```

### 2. 切換與建置 AGV 專案 (無人搬運車)

只會編譯 pkg_agv_line 與 deploy_manager：

```bash
# 1. 清理舊環境
rm -rf build/ install/ log/

# 2. 執行建置 (指定 AGV Mixin 與 AGV Meta)
colcon build --mixin-files colcon.mixin --mixin AGV_Project --metas colcon.agv.meta --cmake-force-configure

# 3. 載入環境變數 (自動觸發 agv_init.sh)
source install/setup.bash

# 4. 驗證環境變數
echo $ROS_DOMAIN_ID
# 預期輸出: 20
```
### 載入環境輸出範例

當執行 source install/setup.bash 時，Terminal 會自動印出目前專案資訊並執行對應初始化動作：

```text
==================================================
[Active Project] Name           : AMR_Project
[Active Project] ROS_DOMAIN_ID  : 10
[Active Project] Running Script : amr_init.sh
--------------------------------------------------
[SH Execution] Initializing AMR hardware & Lidar...
--------------------------------------------------
```
## 前置需求與套件安裝

在開始使用本架構之前，請確保已安裝 ROS 2 環境，並執行以下指令安裝 `colcon-mixin` 擴充套件：

```bash
# 1. 更新 apt 軟體源並安裝 colcon-mixin 套件
sudo apt-get update
sudo apt-get install -y python3-colcon-mixin

# 2. (選擇性) 初始化 colcon-mixin 預設庫
colcon mixin add default [https://raw.githubusercontent.com/colcon/colcon-mixin-repository/master/index.yaml](https://raw.githubusercontent.com/colcon/colcon-mixin-repository/master/index.yaml) 2>/dev/null || true
colcon mixin update