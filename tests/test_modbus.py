import time
import pytest
from simulator.digital_twin_plc import DigitalTwinPLC
from drivers.modbus_driver import ModbusDriver


@pytest.fixture(scope="module")
def plc_simulator():
    # Use high port for testing to avoid admin permission requirements
    plc = DigitalTwinPLC(host="127.0.0.1", port=5025)
    plc.start()
    time.sleep(0.3)
    yield plc
    plc.stop()


def test_modbus_telemetry_reading(plc_simulator):
    driver = ModbusDriver(host="127.0.0.1", port=5025)
    assert driver.connect() is True

    telemetry = driver.read_all_telemetry()
    assert telemetry is not None
    assert "engine_rpm" in telemetry
    assert "dyno_torque_nm" in telemetry
    assert "lux_intensity" in telemetry
    assert telemetry["lux_intensity"] > 10000  # Default ~14,500
    assert telemetry["is_safety_ok"] is True

    driver.disconnect()


def test_modbus_coil_control(plc_simulator):
    driver = ModbusDriver(host="127.0.0.1", port=5025)
    assert driver.connect() is True

    # Trigger Start Test
    assert driver.set_start_trigger(True) is True
    time.sleep(0.1)
    telemetry = driver.read_all_telemetry()
    assert telemetry["is_test_active"] is True

    # Stop test
    assert driver.set_start_trigger(False) is True
    time.sleep(0.1)
    telemetry = driver.read_all_telemetry()
    assert telemetry["is_test_active"] is False

    driver.disconnect()
