import os
import subprocess
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    xacro_path = os.path.join(pkg_dir, 'urdf', 'robot.xacro')
    rviz_config = os.path.join(pkg_dir, 'config', 'rviz.rviz')
    rviz_args = ['-d', rviz_config] if os.path.exists(rviz_config) else []

    robot_desc = subprocess.check_output(['xacro', xacro_path]).decode('utf-8')

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_desc}]
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen'
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=rviz_args
        )
    ])
