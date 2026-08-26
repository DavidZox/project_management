#!/bin/bash

# 1. 自動從 colcon.mixin 抓取所有專案名稱
MIXIN_FILE="colcon.mixin"

if [ ! -f "$MIXIN_FILE" ]; then
    echo "[Error] 找不到 $MIXIN_FILE 檔案！"
    return 1 2>/dev/null || exit 1
fi

# 解析 mixin 檔案中的專案名稱 (讀取 build: 下面縮排的 key)
PROJECTS=($(grep -E '^[[:space:]]{2}[A-Za-z0-9_]+:' "$MIXIN_FILE" | tr -d ' :' ))

if [ ${#PROJECTS[@]} -eq 0 ]; then
    echo "[Error] 未在 $MIXIN_FILE 中找到任何專案！"
    return 1 2>/dev/null || exit 1
fi

# 2. 顯示選單介面
echo "=========================================="
echo "      ROS 2 多專案自動建置部署選單        "
echo "=========================================="
PS3="請選擇要建置的專案數字 (Ctrl+C 取消): "

select SELECTED_PROJECT in "${PROJECTS[@]}"; do
    if [ -n "$SELECTED_PROJECT" ]; then
        break
    else
        echo "無效選項，請重新選擇！"
    fi
done

# 3. 根據選擇自動推導 Meta 檔名 (例如 AMR_Project -> colcon.amr.meta)
META_PREFIX=$(echo "$SELECTED_PROJECT" | cut -d'_' -f1 | tr '[:upper:]' '[:lower:]')
META_FILE="colcon.${META_PREFIX}.meta"

echo "------------------------------------------"
echo "專案: $SELECTED_PROJECT"
echo "Meta: $META_FILE"
echo "------------------------------------------"

# 4. 執行 Colcon Build
colcon build \
  --mixin-files "$MIXIN_FILE" \
  --mixin "$SELECTED_PROJECT" \
  --metas "$META_FILE" \
  --cmake-force-configure

# 5. 建置成功後自動執行 source
if [ $? -eq 0 ]; then
    echo -e "\n[Build Success] 自動載入環境中..."
    source install/setup.bash
else
    echo -e "\n[Build Failed] 建置失敗！"
fi
