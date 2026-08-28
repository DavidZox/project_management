# 自動化建置與發行架構發展進程 (Deployment Automation Roadmap)

## 階段目標與進度追蹤

### Phase 1: 基礎自動建置與專案架構 (進行中)
- [x] 完成一鍵式自動建置腳本 (`build.sh`) 與選單互動切換機制 (AMR / AGV Project)
- [x] 完成核心設計理念 `colcon.mixin` (Packages 篩選) 與 `colcon.*.meta` 專案變數注入
- [x] 完成 `deploy_manager` 模組與自動生成 Environment Hook (`project_hook.sh.in`) 實作
- [x] 建立一碼多用 (Single Source of Truth) 與環境解耦 Setup Hook 機制

### Phase 2: CI/CD 自動化測試與 Debian 套件發行 (規劃中)
- [ ] 建立 GitHub Actions 矩陣建置與測試流程 (AMR_Project / AGV_Project 平行編譯)
- [ ] 整合 `colcon test` 與自動化測試結果彙整機制 (`colcon test-result`)
- [ ] 開發 Debian 獨立安裝包 (`.deb`) 發行流程與 bloom/cpack 打包機制
- [ ] 實作現場部署 `dpkg` 自動安裝與環境變數、初始化腳本固化機制

### Phase 3: 容器化與雲端發行 (長遠規劃)
- [ ] 設計 Docker 多機型打包機制 (同 Dockerfile 帶入不同 `build-arg` 參數)
- [ ] 建立 Docker Image 版本控管與私有 Docker Registry 部署推送流程
- [ ] 整合 CI/CD 與容器化雲端部署機制 (DevOps for Robotics)
- [ ] 實現雲端 OTA (Over-The-Air) 韌體/軟體自動更新與版本降級保護機制