"""
Interactive Terminal Test Rig & Simulation CLI for DynoTest & BrakeTest.
Runs the Digital Twin PLC and allows real-time execution of Dyno & Brake test runs.
"""
import sys
import time
from core.models import Vehicle, TestSession, TestMode
from core.physics import DynoPeakTracker, BrakePeakTracker
from database.connection import DatabaseManager
from database.repository import DatabaseRepository
from drivers.modbus_driver import ModbusDriver
from simulator.digital_twin_plc import DigitalTwinPLC

# Ensure UTF-8 output on Windows terminal
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def render_ascii_gauge(label: str, value: float, max_val: float, unit: str, bar_len: int = 15) -> str:
    clamped = max(0.0, min(value, max_val))
    ratio = clamped / max_val if max_val > 0 else 0.0
    filled = int(ratio * bar_len)
    bar = "=" * filled + "-" * (bar_len - filled)
    return f"{label}:[{bar}] {value:>5.1f} {unit}"


def run_dyno_simulation(driver: ModbusDriver, repo: DatabaseRepository, session_id: int):
    print("\n=======================================================")
    print("         MEMULAI SIMULASI UJI DYNO TEST (GAS PULL)       ")
    print("=======================================================")
    print("Memicu trigger Coil M0 (Start Test)...")

    tracker = DynoPeakTracker(session_id=session_id)
    driver.set_start_trigger(True)
    
    start_time = time.time()
    last_print = 0

    try:
        while True:
            telemetry = driver.read_all_telemetry()
            if not telemetry:
                print("[ERROR] Gagal membaca telemetry dari PLC!")
                break

            current_time = time.time() - start_time
            rpm = telemetry["engine_rpm"]
            torque = telemetry["dyno_torque_nm"]
            speed = telemetry["speed_kmh"]

            hp, tq = tracker.update(rpm, torque, speed, current_time)

            # Print every 100ms
            if current_time - last_print >= 0.1:
                last_print = current_time
                sys.stdout.write("\033[K")  # Clear line
                line1 = render_ascii_gauge("RPM", rpm, 12000, "RPM", 20)
                line2 = render_ascii_gauge("TORSI", torque, 25, "Nm", 20)
                line3 = render_ascii_gauge("DAYA", hp, 25, "HP", 20)
                line4 = render_ascii_gauge("SPEED", speed, 140, "km/h", 20)
                
                output = f"\r[T+{current_time:4.1f}s] | {line1} | {line2} | {line3} | {line4}"
                sys.stdout.write(output)
                sys.stdout.flush()

            # Check if simulator finished pull (auto resets M0)
            if not telemetry["is_test_active"] and current_time > 2.0:
                break

            time.sleep(0.05)

    except KeyboardInterrupt:
        driver.set_start_trigger(False)
        print("\n[INFO] Pengujian dihentikan oleh user.")

    print("\n\n---------------- HASIL DYNO TEST ----------------")
    dyno_result = tracker.get_result()
    print(f"Max Power (HP)     : {dyno_result.max_power_hp:.2f} HP  @ {dyno_result.rpm_at_peak_power:.0f} RPM")
    print(f"Max Torque (Nm)    : {dyno_result.max_torque_nm:.2f} Nm  @ {dyno_result.rpm_at_peak_torque:.0f} RPM")
    print(f"Max Engine RPM     : {dyno_result.max_rpm:.0f} RPM")
    print(f"Top Speed          : {dyno_result.max_speed_kmh:.1f} km/jam")
    print(f"Total Data Points  : {len(dyno_result.raw_time_series)} samples")
    
    # Save to DB
    repo.save_dyno_result(dyno_result)
    print("Status: Berhasil disimpan ke database SQLite!")
    print("-------------------------------------------------")


def run_brake_simulation(driver: ModbusDriver, repo: DatabaseRepository, session_id: int, weight_kg: float = 150.0):
    print("\n=======================================================")
    print("    MEMULAI SIMULASI UJI REM & LAMPU (BRAKE TEST)      ")
    print("=======================================================")
    tracker = BrakePeakTracker(session_id=session_id, vehicle_weight_kg=weight_kg)
    
    # Step 1: Putar roller
    driver.set_start_trigger(True)
    driver.set_brake_pedal(False)
    print("Memutar roller hingga kecepatan uji...")
    for _ in range(15):
        telemetry = driver.read_all_telemetry()
        if telemetry:
            tracker.update(
                roller_rpm=telemetry["roller_rpm"],
                braking_force_n=telemetry["braking_force_n"],
                braking_time_s=telemetry["braking_time_s"],
                lux_intensity=telemetry["lux_intensity"],
                running_time_s=0.5,
                speed_kmh=telemetry["speed_kmh"],
                is_pedal_pressed=False
            )
        time.sleep(0.05)

    print("Menginjak pedal rem (Coil M1 = 1)...")
    driver.set_brake_pedal(True)

    start_time = time.time()
    last_print = 0

    try:
        while True:
            telemetry = driver.read_all_telemetry()
            if not telemetry:
                break

            current_time = time.time() - start_time
            tracker.update(
                roller_rpm=telemetry["roller_rpm"],
                braking_force_n=telemetry["braking_force_n"],
                braking_time_s=telemetry["braking_time_s"],
                lux_intensity=telemetry["lux_intensity"],
                running_time_s=current_time,
                speed_kmh=telemetry["speed_kmh"],
                is_pedal_pressed=telemetry["is_pedal_pressed"]
            )

            if current_time - last_print >= 0.1:
                last_print = current_time
                line1 = render_ascii_gauge("GAYA REM", telemetry["braking_force_n"], 2000, "N", 15)
                line2 = render_ascii_gauge("ROLLER", telemetry["roller_rpm"], 3000, "RPM", 15)
                line3 = render_ascii_gauge("SPEED", telemetry["speed_kmh"], 80, "km/h", 15)
                line4 = render_ascii_gauge("LUX", telemetry["lux_intensity"], 20000, "Lux", 15)
                
                output = f"\r[T+{current_time:4.1f}s] | {line1} | {line2} | {line3} | {line4}"
                sys.stdout.write(output)
                sys.stdout.flush()

            # Roller stopped
            if telemetry["roller_rpm"] == 0 and current_time > 1.0:
                break

            time.sleep(0.05)

    except KeyboardInterrupt:
        pass

    driver.set_brake_pedal(False)
    driver.set_start_trigger(False)

    print("\n\n---------------- HASIL BRAKE & LUX TEST ----------------")
    brake_result = tracker.get_result()
    print(f"Kecepatan Awal     : {brake_result.initial_speed_kmh:.1f} km/jam")
    print(f"Gaya Rem Puncak    : {brake_result.peak_braking_force_n:.1f} N")
    print(f"Waktu Pengereman   : {brake_result.braking_time_s:.2f} detik")
    print(f"Efisiensi Rem      : {brake_result.braking_efficiency_pct:.1f}% -> Status Rem: [{brake_result.brake_pass_status.value}]")
    print(f"Intensitas Lampu   : {brake_result.lux_intensity:.0f} Lux -> Status Lux: [{brake_result.lux_pass_status.value}]")
    print(f"Status Keseluruhan : [{brake_result.overall_status.value}]")
    print(f"Total Data Points  : {len(brake_result.raw_time_series)} samples")
    
    # Save to DB
    repo.save_brake_result(brake_result)
    print("Status: Berhasil disimpan ke database SQLite!")
    print("-------------------------------------------------------")


def main():
    print("========================================================")
    print("   DYNOTEST & BRAKETEST - DIGITAL TWIN CONSOLE RUNNER   ")
    print("========================================================")

    # 1. Start Virtual Digital Twin PLC
    plc = DigitalTwinPLC(host="127.0.0.1", port=5020)
    plc.start()
    time.sleep(0.3)

    # 2. Connect Modbus Client
    driver = ModbusDriver(host="127.0.0.1", port=5020)
    if not driver.connect():
        print("[ERROR] Gagal terhubung ke Digital Twin PLC!")
        plc.stop()
        return

    # 3. Init Database
    db_mgr = DatabaseManager()
    repo = DatabaseRepository(db_mgr)

    # 4. Registrasi Sesi Kendaraan Virtual
    dummy_vehicle = Vehicle(
        vin="MH1KF1118PK123456",
        test_number="KIR-2026-08-999",
        license_plate="B 9999 DYN",
        brand_model="Yamaha Aerox 155",
        engine_capacity_cc=155,
        vehicle_weight_kg=125.0
    )
    repo.save_vehicle(dummy_vehicle)

    session = TestSession(
        vin=dummy_vehicle.vin,
        inspector_name="Taufik Hidayat (Operator)",
        test_mode=TestMode.COMBINED,
        notes="Sesi uji simulasi digital twin"
    )
    session_id = repo.create_test_session(session)
    print(f"[DATABASE] Sesi Uji ID #{session_id} berhasil dibuat untuk kendaraan: {dummy_vehicle.brand_model} ({dummy_vehicle.license_plate})")

    # 5. Run Dyno Test
    run_dyno_simulation(driver, repo, session_id)
    time.sleep(1.0)

    # 6. Run Brake & Lux Test
    run_brake_simulation(driver, repo, session_id, weight_kg=dummy_vehicle.vehicle_weight_kg)

    # 7. Cleanup
    driver.disconnect()
    plc.stop()
    print("\n[SELESAI] Simulasi siklus pengujian lengkap berhasil dieksekusi 100%!")


if __name__ == "__main__":
    main()
