cmake_minimum_required(VERSION 3.8)
project(deploy_manager)

find_package(ament_cmake REQUIRED)

# 使用 DEPLOY_PROJECT_NAME 避免覆蓋 CMake 內建的 PROJECT_NAME
set(DEPLOY_PROJECT_NAME "Default_Project" CACHE STRING "Deploy Project Name")
set(ROS_DOMAIN_ID "0" CACHE STRING "ROS Domain ID")
set(TARGET_SCRIPT "" CACHE STRING "Target init script")

# 安裝 init 腳本
install(
  PROGRAMS
    scripts/amr_init.sh
    scripts/agv_init.sh
  DESTINATION share/${PROJECT_NAME}/scripts
)

# 配置範本檔
configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/env-hooks/project_hook.sh.in"
  "${CMAKE_CURRENT_BINARY_DIR}/project_hook.sh"
  @ONLY
)

# 註冊 Hook
ament_environment_hooks("${CMAKE_CURRENT_BINARY_DIR}/project_hook.sh")

ament_package()
