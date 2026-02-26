# smarthome-robot

Helper library for Smart Home League.

## Install

```bash
pip install smarthome_robot
```

## Usage

```python
from smarthome_robot import RobotU14, RobotU19

# U14
robot = RobotU14(team_name="My Team")
robot.left_motor = 10.0
robot.right_motor = 10.0
val = robot.distance_front_left

# U19
robot = RobotU19(team_name="My Team")
x, y, z = robot.gps
roll, pitch, yaw = robot.imu
```

Value properties: `bumper_left`, `bumper_right`, `distance_front_left`, `distance_front_right`, `distance_left`, `distance_right`, `left_motor`, `right_motor`, `left_encoder`, `right_encoder`, `led_on`, `led_play`, `led_step`. Motors and LEDs have setters. Raw devices: `_left_motor`, `_bumpers`, `_distance_sensors`, etc.
