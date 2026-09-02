import pytest
from core.physics import (
    calculate_power_hp,
    calculate_braking_efficiency,
    evaluate_brake_pass,
    evaluate_lux_pass,
    evaluate_overall_status,
    DynoPeakTracker,
    BrakePeakTracker,
    METRIC_HP_CONSTANT
)
from core.models import EvaluationStatus


def test_calculate_power_hp():
    # 18.0 Nm at 7000 RPM: (18.0 * 7000) / 7127 = 17.68 HP
    hp = calculate_power_hp(18.0, 7000)
    assert hp == round((18.0 * 7000) / 7127.0, 2)
    assert hp > 0

    # 0 RPM or 0 Torque
    assert calculate_power_hp(0, 7000) == 0.0
    assert calculate_power_hp(18.0, 0) == 0.0


def test_calculate_braking_efficiency():
    # 150 kg vehicle with 1100 N braking force:
    # 1100 / (150 * 9.80665) * 100 = 74.78%
    eff = calculate_braking_efficiency(1100.0, 150.0)
    assert eff == 74.78
    assert eff > 50.0  # Pass standard


def test_evaluations():
    assert evaluate_brake_pass(55.0) == EvaluationStatus.PASS
    assert evaluate_brake_pass(49.9) == EvaluationStatus.FAIL

    assert evaluate_lux_pass(14500) == EvaluationStatus.PASS
    assert evaluate_lux_pass(11999) == EvaluationStatus.FAIL

    assert evaluate_overall_status(EvaluationStatus.PASS, EvaluationStatus.PASS) == EvaluationStatus.PASS
    assert evaluate_overall_status(EvaluationStatus.PASS, EvaluationStatus.FAIL) == EvaluationStatus.FAIL


def test_dyno_peak_tracker():
    tracker = DynoPeakTracker(session_id=1)
    
    # Simulate a rising and falling curve
    tracker.update(rpm=2000, torque_nm=12.0, speed_kmh=25.0, running_time_s=1.0)
    tracker.update(rpm=6500, torque_nm=18.5, speed_kmh=75.0, running_time_s=3.0)  # Peak torque & HP
    tracker.update(rpm=9000, torque_nm=14.0, speed_kmh=110.0, running_time_s=5.0) # Peak RPM & Speed

    res = tracker.get_result()
    assert res.session_id == 1
    assert res.max_rpm == 9000.0
    assert res.max_speed_kmh == 110.0
    assert res.max_torque_nm == 18.5
    assert res.rpm_at_peak_torque == 6500.0
    assert len(res.raw_time_series) == 3


def test_brake_peak_tracker():
    tracker = BrakePeakTracker(session_id=1, vehicle_weight_kg=150.0)
    
    # Step 1: Spinning up roller to 50 km/h
    tracker.update(roller_rpm=2000, braking_force_n=0.0, braking_time_s=0.0,
                   lux_intensity=15000, running_time_s=1.0, speed_kmh=50.0, is_pedal_pressed=False)
    
    # Step 2: Pedal pressed
    tracker.update(roller_rpm=1000, braking_force_n=1200.0, braking_time_s=0.8,
                   lux_intensity=15000, running_time_s=2.0, speed_kmh=25.0, is_pedal_pressed=True)
    
    # Step 3: Stopped
    tracker.update(roller_rpm=0, braking_force_n=1200.0, braking_time_s=1.4,
                   lux_intensity=15000, running_time_s=3.0, speed_kmh=0.0, is_pedal_pressed=True)

    res = tracker.get_result()
    assert res.session_id == 1
    assert res.initial_speed_kmh == 50.0
    assert res.peak_braking_force_n == 1200.0
    assert res.braking_time_s == 1.4
    assert res.lux_intensity == 15000.0
    assert res.brake_pass_status == EvaluationStatus.PASS
    assert res.lux_pass_status == EvaluationStatus.PASS
    assert res.overall_status == EvaluationStatus.PASS
