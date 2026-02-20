import re
import importlib


def test_version_exists():
    pkg = importlib.import_module("smarthome_robot")
    assert hasattr(pkg, "__version__")
    assert isinstance(pkg.__version__, str)
    assert re.match(r"^\d+\.\d+\.\d+", pkg.__version__)


def test_all_is_list():
    pkg = importlib.import_module("smarthome_robot")
    assert hasattr(pkg, "__all__")
    assert isinstance(pkg.__all__, list)
