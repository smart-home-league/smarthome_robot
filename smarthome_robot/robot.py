"""
Smart Home Robot - base classes for Smart Home League.
"""

import json
import math
from typing import Any, Dict, Tuple

from controller import Robot as BaseRobot


def _require_device(robot: BaseRobot, name: str) -> Any:
    d = robot.getDevice(name)
    if d is None:
        raise ValueError(f"Device '{name}' not found")
    return d


class Robot(BaseRobot):
    """Shared robot with common devices: bumpers, distance sensors, motors, encoders, receiver, LEDs."""

    def __init__(self, team_name: str = "My Team") -> None:
        """Initialize robot and enable all common devices.

        Args:
            team_name: Name sent to supervisor (shown on dashboard).

        Raises:
            ValueError: If any required device is missing from the robot model.
        """
        super().__init__()
        self.team_name = team_name
        self.time_step = int(self.getBasicTimeStep())
        self.setCustomData(json.dumps({"team": team_name}))
        self._init_devices()

    def _init_devices(self) -> None:
        """Enable and configure bumpers, distance sensors, motors, encoders, receiver, and LEDs."""
        ts = self.time_step

        self._bumpers = [_require_device(self, n) for n in ["bumper_left", "bumper_right"]]
        for d in self._bumpers:
            d.enable(ts)

        self._distance_sensors = [
            _require_device(self, n)
            for n in ["cliff_front_left", "cliff_front_right", "cliff_left", "cliff_right"]
        ]
        for d in self._distance_sensors:
            d.enable(ts)

        self._receiver = _require_device(self, "receiver")
        self._receiver.enable(ts)

        self._leds = [_require_device(self, n) for n in ["led_on", "led_play", "led_step"]]

        self._left_motor = _require_device(self, "left wheel motor")
        self._right_motor = _require_device(self, "right wheel motor")
        self._left_motor.setPosition(float("inf"))
        self._right_motor.setPosition(float("inf"))
        self._left_motor.setVelocity(0.0)
        self._right_motor.setVelocity(0.0)

        self._left_encoder = _require_device(self, "left wheel sensor")
        self._right_encoder = _require_device(self, "right wheel sensor")
        self._left_encoder.enable(ts)
        self._right_encoder.enable(ts)


    @property
    def receiver(self) -> Any:
        """Raw receiver device for virtual wall detection."""
        return self._receiver

    @property
    def bumper_left(self) -> float:
        """Left bumper value (non-zero when pressed)."""
        return self._bumpers[0].getValue()

    @property
    def bumper_right(self) -> float:
        """Right bumper value (non-zero when pressed)."""
        return self._bumpers[1].getValue()

    @property
    def distance_front_left(self) -> float:
        """Front-left distance sensor value."""
        return self._distance_sensors[0].getValue()

    @property
    def distance_front_right(self) -> float:
        """Front-right distance sensor value."""
        return self._distance_sensors[1].getValue()

    @property
    def distance_left(self) -> float:
        """Left distance sensor value."""
        return self._distance_sensors[2].getValue()

    @property
    def distance_right(self) -> float:
        """Right distance sensor value."""
        return self._distance_sensors[3].getValue()

    @property
    def left_motor(self) -> float:
        """Left wheel velocity (rad/s)."""
        return self._left_motor.getVelocity()

    @left_motor.setter
    def left_motor(self, value: float) -> None:
        self._left_motor.setVelocity(float(value))

    @property
    def right_motor(self) -> float:
        """Right wheel velocity (rad/s)."""
        return self._right_motor.getVelocity()

    @right_motor.setter
    def right_motor(self, value: float) -> None:
        self._right_motor.setVelocity(float(value))

    @property
    def left_encoder(self) -> float:
        """Left wheel encoder position (rad)."""
        return self._left_encoder.getValue()

    @property
    def right_encoder(self) -> float:
        """Right wheel encoder position (rad)."""
        return self._right_encoder.getValue()

    @property
    def led_on(self) -> bool:
        """Power LED state."""
        return self._leds[0].get()

    @led_on.setter
    def led_on(self, value: bool) -> None:
        self._leds[0].set(bool(value))

    @property
    def led_play(self) -> bool:
        """Play LED state."""
        return self._leds[1].get()

    @led_play.setter
    def led_play(self, value: bool) -> None:
        self._leds[1].set(bool(value))

    @property
    def led_step(self) -> bool:
        """Step LED state."""
        return self._leds[2].get()

    @led_step.setter
    def led_step(self, value: bool) -> None:
        self._leds[2].set(bool(value))


class RobotU14(Robot):
    """U14 robot: adds ground color sensor for floor dust detection."""

    def _init_devices(self) -> None:
        """Enable base devices plus ground color sensor."""
        super()._init_devices()
        ts = self.time_step
        self._color_sensor = _require_device(self, "ground_color_sensor")
        self._color_sensor.enable(ts)

    @property
    def color_sensor(self) -> Tuple[int, int, int]:
        """RGB tuple (r, g, b) of floor ahead. Pixel at rightmost column, center row."""
        img = self._color_sensor.getImage()
        if not img:
            return (0, 0, 0)
        w = self._color_sensor.getWidth()
        h = self._color_sensor.getHeight()
        px, py = w - 1, h // 2
        r = self._color_sensor.imageGetRed(img, w, px, py)
        g = self._color_sensor.imageGetGreen(img, w, px, py)
        b = self._color_sensor.imageGetBlue(img, w, px, py)
        return (r, g, b)
    
    @property
    def rooms(self) -> Dict[int, float]:
        """Room percentage data: {room_id: percentage} for all rooms in the environment."""
        data = json.loads(self.getCustomData())
        return data.get('roomPcts')
    
    @property
    def current_room(self) -> Dict[int, float]:
        """Current room ID."""
        data = json.loads(self.getCustomData())
        return data.get('currentRoom')


class RobotFS(RobotU14):
    """First Step robot: same as U14."""


class RobotU19(Robot):
    """U19 robot: adds GPS and IMU for pose estimation."""

    def _init_devices(self) -> None:
        """Enable base devices plus GPS and IMU."""
        super()._init_devices()
        ts = self.time_step
        self._gps = _require_device(self, "gps")
        self._gps.enable(ts)
        self._imu = _require_device(self, "inertial unit")
        self._imu.enable(ts)

    @property
    def gps(self) -> Tuple[float, float, float]:
        """(x, y, z) in world coordinates (meters)."""
        return self._gps.getValues()

    @property
    def imu(self) -> Tuple[float, float, float]:
        """(roll, pitch, yaw) in radians."""
        return self._imu.getRollPitchYaw()

    @property
    def position(self) -> Tuple[float, float]:
        """(x, y) in world coordinates."""
        x, y, _ = self._gps.getValues()
        return (x, y)

    @property
    def rotation(self) -> float:
        """Yaw in degrees (0-360)."""
        _, _, yaw = self._imu.getRollPitchYaw()
        return (math.degrees(yaw) + 360.0) % 360.0
    
    @property
    def battery(self) -> float:
        """Battery level data."""
        data = json.loads(self.getCustomData())
        return data.get('battery')
