import os
from plantuml import PlantUML

def generate_puml_output(width=350, rank_sep=100):
    # 1. 建立連線
    server = PlantUML(url='http://www.plantuml.com/plantuml/img/')

    # 2. 定義 PlantUML 語法 (使用 f-string 控制比例)
    puml_syntax = """
@startuml
' --- 比例與樣式精準控制 ---
skinparam RectangleWidthMax 300
skinparam ranksep 60
skinparam shadowing false
skinparam defaultFontName "Microsoft JhengHei"

title 1. 診斷系統基礎架構與分散式 Library 架構 (Diagnostics Architecture)

rectangle N1 #E1D5E7 [
  1. 功能節點層 (Functional Nodes Layer)
  各功能 Node (Sensor / Motion / Nav)
  引入對應的 Diagnostic Helper Lib (C++/Python)
]

rectangle N2 #D1E5F0 [
  2. 診斷傳輸層 (Diagnostics Transport)
  透過 diagnostic_updater API 發布
  原始診斷訊息至 /diagnostics (DiagnosticArray)
]

rectangle N3 #F5F5F5 [
  3. 診斷彙整與分層中心 (Aggregation Center)
  diagnostic_aggregator 讀取 diagnostics_matchers.yaml
  完成 Level 1~3 系統分層並發布至 /diagnostics_agg
]

rectangle N4 #DAE8FE [
  4. 監控與高階決策層 (Monitoring & Decision)
  System Health Monitor 進行跨 Node 交叉診斷
  根據故障等級觸發降級或硬體保護
]

' --- 邏輯流向 ---
N1 -down-> N2 : 非同步 Callback 觸發發布
N2 -down-> N3 : 原始診斷資料匯流
N3 -down-> N4 : 訂閱分層後的狀態資訊

' --- 交互機制 ---
N4 .[#e74c3c,bold]left.> N1 : "降級/重試指令 (Task Agent) 或 硬體急停 (Safety PLC)"

note right of N1
  **非同步觸發機制：**
  功能負責人於主程序 Include 模組
  自行決定診斷門檻與觸發時機
  最小化對業務邏輯的干擾
end note

note right of N3
  **YAML 分層架構：**
  依據 Level 1~3 劃分
  如 /Hardware/Sensors
  及 /Control/Motors
end note

note bottom of N4
  **分級處置機制：**
  - rqt_robot_monitor 開發者視覺化
  - 輕微故障：Task Agent 任務重試/降級
  - 嚴重故障：Safety PLC 硬體急停 (E-Stop)
end note
@enduml
"""
    file_base = "診斷機制框架圖"

    # --- 輸出 A: .puml 語法檔 ---
    try:
        with open(f"{file_base}.puml", "w", encoding="utf-8") as f:
            f.write(puml_syntax.strip())
        print(f"✅ 語法檔儲存成功：{os.path.abspath(file_base + '.puml')}")
    except Exception as e:
        print(f"❌ 語法檔儲存失敗: {e}")

    # --- 輸出 B: .png 圖片檔 ---
    try:
        # 直接傳送字串渲染，避開 Windows 編碼報錯
        raw_image_data = server.processes(puml_syntax)
        with open(f"{file_base}.png", 'wb') as f:
            f.write(raw_image_data)
        print(f"✅ 圖片檔轉檔成功：{os.path.abspath(file_base + '.png')}")
    except Exception as e:
        print(f"❌ 圖片轉檔失敗 (請檢查網路): {e}")

if __name__ == "__main__":
    # 這裡你可以精準調整比例：
    # width: 調整方塊寬度
    # rank_sep: 調整垂直間距
    generate_puml_output(width=450, rank_sep=50)