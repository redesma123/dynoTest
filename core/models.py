"""
Domain models and dataclasses for DynoTest & BrakeTest application.
Follows Ubiquitous Language defined in docs/CONTEXT.md.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class TestMode(str, Enum):
    __test__ = False
    DYNO = "DYNO"
    BRAKE = "BRAKE"
    COMBINED = "COMBINED"


class EvaluationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


@dataclass
class Vehicle:
    vin: str
    test_number: str
    license_plate: str = ""
    vehicle_category: str = "Roda 2"
    brand_model: str = ""
    engine_capacity_cc: int = 150
    vehicle_weight_kg: float = 150.0
    created_at: Optional[datetime] = None


@dataclass
class DynoTelemetry:
    """Realtime telemetry packet from Dyno test rig."""
    engine_rpm: int = 0
    dyno_torque_nm: float = 0.0
    speed_kmh: float = 0.0
    power_hp: float = 0.0
    running_time_s: float = 0.0
    is_test_active: bool = False


@dataclass
class BrakeTelemetry:
    """Realtime telemetry packet from Brake & Lux test bench."""
    roller_rpm: int = 0
    braking_force_n: float = 0.0
    braking_time_s: float = 0.0
    lux_intensity: float = 0.0
    running_time_s: float = 0.0
    speed_kmh: float = 0.0
    is_pedal_pressed: bool = False
    is_test_active: bool = False


@dataclass
class DynoResult:
    session_id: int
    max_rpm: float = 0.0
    max_torque_nm: float = 0.0
    max_power_hp: float = 0.0
    max_speed_kmh: float = 0.0
    rpm_at_peak_power: float = 0.0
    rpm_at_peak_torque: float = 0.0
    raw_time_series: List[Dict[str, Any]] = field(default_factory=list)
    id: Optional[int] = None


@dataclass
class BrakeResult:
    session_id: int
    initial_speed_kmh: float = 0.0
    peak_braking_force_n: float = 0.0
    braking_time_s: float = 0.0
    total_running_time_s: float = 0.0
    lux_intensity: float = 0.0
    braking_efficiency_pct: float = 0.0
    lux_pass_status: EvaluationStatus = EvaluationStatus.FAIL
    brake_pass_status: EvaluationStatus = EvaluationStatus.FAIL
    overall_status: EvaluationStatus = EvaluationStatus.FAIL
    raw_time_series: List[Dict[str, Any]] = field(default_factory=list)
    id: Optional[int] = None


@dataclass
class TestSession:
    __test__ = False
    vin: str
    inspector_name: str
    test_mode: TestMode
    notes: str = ""
    tested_at: Optional[datetime] = None
    id: Optional[int] = None
    dyno_result: Optional[DynoResult] = None
    brake_result: Optional[BrakeResult] = None
