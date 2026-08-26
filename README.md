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
            ├── amr_init.sh                 # AMR 硬體與雷達初始化腳本[cite: 7]
            └── agv_init.sh                 # AGV 巡線感測器初始化腳本[cite: 6]
```