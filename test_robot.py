import os
import sys
import subprocess
import xml.etree.ElementTree as ET
import yaml

# find xacro file
xacro_file = os.path.join(os.path.dirname(__file__), 'urdf', 'robot.xacro')
yaml_file = os.path.join(os.path.dirname(__file__), 'config', 'controllers.yaml')

if not os.path.exists(xacro_file):
    print(f"FAIL: File not found: {xacro_file}")
    sys.exit(1)

if not os.path.exists(yaml_file):
    print(f"FAIL: File not found: {yaml_file}")
    sys.exit(1)

# test 1: expand xacro
try:
    proc = subprocess.run(['xacro', xacro_file], capture_output=True, text=True, check=True)
    xml_content = proc.stdout
    print("Xacro expansion successful!")
except Exception as e:
    print(f"FAIL: Xacro processing error: {e}")
    sys.exit(1)

try:
    root = ET.fromstring(xml_content)
except Exception as e:
    print(f"FAIL: XML parse error: {e}")
    sys.exit(1)

# test 2: parse links and joints
links = {link.attrib['name']: link for link in root.findall('link')}
joints = {joint.attrib['name']: joint for joint in root.findall('joint')}

print(f"Total links: {len(links)}")
print(f"Total joints: {len(joints)}")

all_joints_valid = True
for name, j in joints.items():
    jtype = j.attrib.get('type')
    parent = j.find('parent').attrib.get('link') if j.find('parent') is not None else None
    child = j.find('child').attrib.get('link') if j.find('child') is not None else None

    print(f" - Joint: {name} | Type: {jtype} | Parent: {parent} -> Child: {child}")

    if parent not in links or child not in links:
        print(f"   ERROR: Joint {name} links missing: parent={parent}, child={child}")
        all_joints_valid = False

# check subsystem presence
has_base = 'left_wheel_joint' in joints and 'right_wheel_joint' in joints
has_arm = all(f'arm_joint{i}' in joints for i in range(1, 5))
has_gripper = 'left_finger_joint' in joints and 'right_finger_joint' in joints
has_sensors = all(s in links for s in ['lidar_link', 'camera_link', 'imu_link'])

print(f"Subsystems: base={has_base}, arm={has_arm}, gripper={has_gripper}, sensors={has_sensors}")

# test 3: check ros2_control tag
r2c = root.find('ros2_control')
has_ros2_control = r2c is not None
if has_ros2_control:
    r2c_joints = [j.attrib.get('name') for j in r2c.findall('joint')]
    print(f"ros2_control joints registered ({len(r2c_joints)}): {r2c_joints}")

# test 4: load controllers.yaml
try:
    with open(yaml_file, 'r') as f:
        config = yaml.safe_load(f)
    print("Controllers YAML loaded successfully!")
    controllers = list(config.keys())
    print(f"Controllers defined: {controllers}")
    yaml_valid = 'controller_manager' in config
except Exception as e:
    print(f"FAIL: YAML load error: {e}")
    yaml_valid = False

if (all_joints_valid and has_base and has_arm and has_gripper and 
    has_sensors and has_ros2_control and yaml_valid):
    print("PASS: Mobile Manipulator verification passed! Base + Arm + Gripper + Sensors + ros2_control + YAML verified.")
    sys.exit(0)
else:
    print("FAIL: Verification failed!")
    sys.exit(1)
