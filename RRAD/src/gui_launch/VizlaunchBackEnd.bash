#!/bin/bash

CATKIN_WORKSPACE="/home/steven/RRAD"

source /opt/ros/kinetic/setup.bash
source $CATKIN_WORKSPACE/devel/setup.bash
gnome-terminal \
  --tab-with-profile=Unnamed -t "roscore" --command="roscore" \
  --tab-with-profile=Unnamed -t "Flask" --command=$CATKIN_WORKSPACE"/src/gui/BackEnd/runFlaskServer.py" \
  --tab-with-profile=Unnamed -t "file_input_service" --command="rosrun rrad_wash_cell file_input_service_final.py" \
  --tab-with-profile=Unnamed -t "path_modifier_server" --command="rosrun rrad_wash_cell ImpingementROS.py" \
  --tab-with-profile=Unnamed -t "path_planning_service_master" --command="rosrun rrad_wash_cell NewVizPlanner.py" \
  --tab-with-profile=Unnamed -t "path_storage_server" --command="rosrun rrad_wash_cell path_storage_server_final.py" \
  --tab-with-profile=Unnamed -t "subpath_builder_service" --command="rosrun rrad_wash_cell NewReworkPlanner.py"&
