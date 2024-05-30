# robotics_final_project

## Usage:

Start 3 Terminals:

### CoppeliaSim:

`~/apps/CoppeliaSim_Edu_V4_4_0_rev0_Ubuntu22_04/coppeliaSim.sh`

In Coppelia, load the scene "Robomaster_Red_Blue.ttt" and start the simulation.

### ROS:

`cd ~/dev_ws/src/robomaster_ros`

`ros2 launch robomaster_ros s1.launch`

### Controller:

`cd /home/robotics23/dev_ws`

`colcon build`

`source ~/dev_ws/install/setup.bash`

`ros2 launch robotics_final_project final.launch.xml`




