import os
import subprocess
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node

def generate_launch_description():
    # expand xacro to urdf string
    xacro_path = os.path.join(os.path.dirname(__file__), '..', 'urdf', 'robot.xacro')
    robot_desc = subprocess.check_output(['xacro', xacro_path]).decode('utf-8')

    return LaunchDescription([
        # robot state publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_desc}]
        ),
        # launch gazebo server & client
        ExecuteProcess(
            cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_factory.so'],
            output='screen'
        ),
        # spawn entity in gazebo
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            name='spawn_entity',
            output='screen',
            arguments=['-topic', 'robot_description', '-entity', 'mobile_manipulator']
        )
    ])
