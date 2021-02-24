cmake_minimum_required(VERSION 3.17)
project(fps)

set(CMAKE_CXX_STANDARD 14)

set(CMAKE_CXX_COMPILER g++)

add_executable(fps
        src/point_aux.c
        src/point_aux.h
        src/fps.c
        src/fps.h
        src/fps_test.c)


target_link_libraries(fps)