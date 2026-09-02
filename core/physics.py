"""
Physics & Calculation Engine for DynoTest & BrakeTest.
Provides deterministic calculations for Power (HP), Brake Efficiency, Peak Tracking, and Evaluation.
"""
from typing import Tuple, Dict, Any, List, Optional
from core.models import EvaluationStatus, DynoResult, BrakeResult


# Constant for Metric Horsepower (PS/HP) calculation: HP = (Torque_Nm * RPM) / 7127
METRIC_HP_CONSTANT = 7127.0
# Gravity acceleration standard (m/s^2)
STANDARD_GRAVITY = 9.80665
# Minimum statutory threshold for brake efficiency (50%)
MIN_BRAKE_EFFICIENCY_PCT = 50.0
# Minimum statutory threshold for headlamp lux intensity (12,000 Lux)
MIN_LUX_INTENSITY = 12000.0


def calculate_power_hp(torque_nm: float, rpm: float, constant: float = METRIC_HP_CONSTANT) -> float:
    """
    Menghitung daya kuda (HP / PS) dari torsi dan RPM.
    Formula: HP = (Torque_Nm * RPM) / constant
    """
    if rpm <= 0 or torque_nm <= 0:
        return 0.0
    hp = (torque_nm * rpm) / constant
    return round(hp, 2)


def calculate_braking_efficiency(total_braking_force_n: float, vehicle_weight_kg: float) -> float:
    """
    Menghitung persentase efisiensi pengereman terhadap bobot kendaraan.
    Formula: Efficiency (%) = (Total Braking Force (N) / (Vehicle Weight (kg) * g)) * 100%
    """
    if vehicle_weight_kg <= 0 or total_braking_force_n <= 0:
        return 0.0
    weight_force_n = vehicle_weight_kg * STANDARD_GRAVITY
    efficiency = (total_braking_force_n / weight_force_n) * 100.0
    return round(efficiency, 2)


def evaluate_brake_pass(efficiency_pct: float, threshold: float = MIN_BRAKE_EFFICIENCY_PCT) -> EvaluationStatus:
    """Menentukan status kelulusan rem berdasarkan ambang batas efisiensi."""
    return EvaluationStatus.PASS if efficiency_pct >= threshold else EvaluationStatus.FAIL


def evaluate_lux_pass(lux_intensity: float, threshold: float = MIN_LUX_INTENSITY) -> EvaluationStatus:
    """Menentukan status kelulusan intensitas lampu (Lux)."""
    return EvaluationStatus.PASS if lux_intensity >= threshold else EvaluationStatus.FAIL


def evaluate_overall_status(brake_status: EvaluationStatus, lux_status: EvaluationStatus) -> EvaluationStatus:
    """Status lulus jika kedua uji rem dan lampu lulus."""
    if brake_status == EvaluationStatus.PASS and lux_status == EvaluationStatus.PASS:
        return EvaluationStatus.PASS
    return EvaluationStatus.FAIL


class DynoPeakTracker:
    """
    Real-time peak detector and telemetry accumulator for Dyno test runs.
    """
    def __init__(self, session_id: int):
        self.session_id = session_id
        self.max_rpm: float = 0.0
        self.max_torque_nm: float = 0.0
        self.max_power_hp: float = 0.0
        self.max_speed_kmh: float = 0.0
        self.rpm_at_peak_power: float = 0.0
        self.rpm_at_peak_torque: float = 0.0
        self.time_series: List[Dict[str, Any]] = []

    def update(self, rpm: int, torque_nm: float, speed_kmh: float, running_time_s: float) -> Tuple[float, float]:
        """
        Process new sample point.
        Returns: (current_power_hp, current_torque_nm)
        """
        power_hp = calculate_power_hp(torque_nm, rpm)

        if rpm > self.max_rpm:
            self.max_rpm = float(rpm)

        if speed_kmh > self.max_speed_kmh:
            self.max_speed_kmh = float(speed_kmh)

        if torque_nm > self.max_torque_nm:
            self.max_torque_nm = float(torque_nm)
            self.rpm_at_peak_torque = float(rpm)

        if power_hp > self.max_power_hp:
            self.max_power_hp = float(power_hp)
            self.rpm_at_peak_power = float(rpm)

        self.time_series.append({
            "t": round(running_time_s, 2),
            "rpm": rpm,
            "torque": round(torque_nm, 2),
            "power": power_hp,
            "speed": round(speed_kmh, 1)
        })

        return power_hp, torque_nm

    def get_result(self) -> DynoResult:
        return DynoResult(
            session_id=self.session_id,
            max_rpm=self.max_rpm,
            max_torque_nm=self.max_torque_nm,
            max_power_hp=self.max_power_hp,
            max_speed_kmh=self.max_speed_kmh,
            rpm_at_peak_power=self.rpm_at_peak_power,
            rpm_at_peak_torque=self.rpm_at_peak_torque,
            raw_time_series=self.time_series
        )


class BrakePeakTracker:
    """
    Real-time peak detector and telemetry accumulator for Brake & Lux test runs.
    """
    def __init__(self, session_id: int, vehicle_weight_kg: float):
        self.session_id = session_id
        self.vehicle_weight_kg = vehicle_weight_kg
        self.initial_speed_kmh: float = 0.0
        self.peak_braking_force_n: float = 0.0
        self.max_braking_time_s: float = 0.0
        self.max_running_time_s: float = 0.0
        self.latest_lux_intensity: float = 0.0
        self.time_series: List[Dict[str, Any]] = []
        self._initial_speed_recorded = False

    def update(
        self,
        roller_rpm: int,
        braking_force_n: float,
        braking_time_s: float,
        lux_intensity: float,
        running_time_s: float,
        speed_kmh: float,
        is_pedal_pressed: bool
    ):
        if not self._initial_speed_recorded and speed_kmh > 0 and not is_pedal_pressed:
            self.initial_speed_kmh = max(self.initial_speed_kmh, speed_kmh)

        if is_pedal_pressed:
            self._initial_speed_recorded = True

        if braking_force_n > self.peak_braking_force_n:
            self.peak_braking_force_n = float(braking_force_n)

        if braking_time_s > self.max_braking_time_s:
            self.max_braking_time_s = float(braking_time_s)

        if running_time_s > self.max_running_time_s:
            self.max_running_time_s = float(running_time_s)

        if lux_intensity > 0:
            self.latest_lux_intensity = float(lux_intensity)

        self.time_series.append({
            "t": round(running_time_s, 2),
            "roller_rpm": roller_rpm,
            "force_n": round(braking_force_n, 1),
            "brake_t": round(braking_time_s, 2),
            "lux": round(lux_intensity, 0),
            "speed": round(speed_kmh, 1),
            "pedal": is_pedal_pressed
        })

    def get_result(self) -> BrakeResult:
        efficiency = calculate_braking_efficiency(self.peak_braking_force_n, self.vehicle_weight_kg)
        brake_pass = evaluate_brake_pass(efficiency)
        lux_pass = evaluate_lux_pass(self.latest_lux_intensity)
        overall = evaluate_overall_status(brake_pass, lux_pass)

        return BrakeResult(
            session_id=self.session_id,
            initial_speed_kmh=round(self.initial_speed_kmh, 1),
            peak_braking_force_n=round(self.peak_braking_force_n, 1),
            braking_time_s=round(self.max_braking_time_s, 2),
            total_running_time_s=round(self.max_running_time_s, 2),
            lux_intensity=round(self.latest_lux_intensity, 1),
            braking_efficiency_pct=efficiency,
            lux_pass_status=lux_pass,
            brake_pass_status=brake_pass,
            overall_status=overall,
            raw_time_series=self.time_series
        )
