"""
Smart Home Robot - helper library for Smart Home League.
"""
__version__ = "0.1.6"

# Import robot classes lazily; the `controller` dependency (Webots) may not
# be available at install/import time for people who only need metadata.
try:
	from .robot import RobotU14, RobotFS, RobotU19  # type: ignore

	__all__ = ["RobotU14", "RobotFS", "RobotU19"]
except Exception:
	# If the environment doesn't have Webots controller, importing the
	# concrete robot types will fail. Keep import-safe behavior so that
	# callers can still inspect `__version__` and install the package.
	__all__ = []
