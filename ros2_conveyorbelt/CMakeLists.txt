cmake_minimum_required(VERSION 3.10)
project(ros2_conveyorbelt)

# Default to C++17
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(conveyorbelt_msgs REQUIRED)

find_package(gz-sim8 REQUIRED)
find_package(gz-plugin2 REQUIRED)
find_package(gz-math7 REQUIRED)

add_library(ros2gz_conveyorbelt_system SHARED
  src/ros2gz_conveyorbelt_system.cpp
)
target_include_directories(ros2gz_conveyorbelt_system PUBLIC 
  include
  ${gz-sim8_INCLUDE_DIRS}
)
target_link_libraries(ros2gz_conveyorbelt_system
  gz-sim8::gz-sim8
  gz-plugin2::gz-plugin2
  gz-math7::gz-math7
)
ament_target_dependencies(ros2gz_conveyorbelt_system
  rclcpp
  conveyorbelt_msgs
)

install(TARGETS ros2gz_conveyorbelt_system
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)
install(DIRECTORY include/ DESTINATION include)

# Install Python scripts:
install(
  DIRECTORY 
    python
  DESTINATION 
    share/${PROJECT_NAME}
)
install(PROGRAMS
  python/SpawnObject.py
  python/item_spawner.py
  python/item_spawner_template.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()