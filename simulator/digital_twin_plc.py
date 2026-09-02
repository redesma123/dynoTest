"""
Digital Twin PLC Simulator for DynoTest & BrakeTest.
Simulates realistic vehicle acceleration, dyno torque curves, brake dynamics, and Modbus TCP server.
"""
import math
import random
import socket
import struct
import threading
import time
from typing import Optional


class DigitalTwinPLC:
    def __init__(self, host: str = "127.0.0.1", port: int = 5020):
        self.host = host
        self.port = port
        self.v_registers = [0] * 100
        self.coils = [False] * 100
        
        # Initial status
        self.coils[3] = True  # M3: Safety Interlock OK
        self.v_registers[10] = 1  # V10: Status Code (1 = Idle)
        self.v_registers[5] = 14500  # V5: Lux 14,500

        self.running = False
        self.server_socket: Optional[socket.socket] = None
        self._physics_thread: Optional[threading.Thread] = None
        self._server_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Internal simulation state variables
        self.sim_time = 0.0
        self.dyno_progress = 0.0
        self.sim_mode = "IDLE"  # "DYNO_RUN", "BRAKE_RUN", "IDLE"

    def start(self):
        """Starts both simulation physics thread and Modbus TCP listener."""
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.server_socket.settimeout(0.5)

        self._physics_thread = threading.Thread(target=self._run_physics_loop, daemon=True)
        self._physics_thread.start()

        self._server_thread = threading.Thread(target=self._run_server_loop, daemon=True)
        self._server_thread.start()
        print(f"[DIGITAL TWIN PLC] Server aktif di {self.host}:{self.port}")

    def stop(self):
        """Stops simulator cleanly."""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass

    def trigger_dyno_sweep(self):
        """Programmatic trigger for automated dyno test run."""
        with self._lock:
            self.coils[0] = True  # M0 = Start
            self.coils[1] = False
            self.dyno_progress = 0.0

    def trigger_brake_test(self):
        """Programmatic trigger for automated brake test run."""
        with self._lock:
            self.coils[0] = True
            self.coils[1] = False
            self.v_registers[2] = 2500  # Initial roller RPM
            self.v_registers[7] = 600   # 60.0 km/h

    def press_brake_pedal(self, pressed: bool = True):
        with self._lock:
            self.coils[1] = pressed

    def _run_physics_loop(self):
        dt = 0.05  # 20 Hz simulation physics step
        brake_timer = 0.0
        test_timer = 0.0

        prev_start_test = False
        while self.running:
            with self._lock:
                start_test = self.coils[0]  # M0
                pedal_pressed = self.coils[1]  # M1
                tare_requested = self.coils[2]  # M2

                # Detect rising edge of start_test
                if start_test and not prev_start_test:
                    test_timer = 0.0
                    brake_timer = 0.0
                    self.dyno_progress = 0.0
                    self.v_registers[2] = 2500  # Initial brake roller RPM
                    self.v_registers[7] = 600   # 60.0 km/h initial speed
                prev_start_test = start_test

                if tare_requested:
                    self.v_registers[1] = 0  # Zero torque
                    self.v_registers[3] = 0  # Zero brake force
                    self.coils[2] = False   # Reset tare coil

                if start_test:
                    test_timer += dt
                    self.v_registers[6] = int(test_timer)
                    self.v_registers[10] = 2  # V10 = 2 (Running)

                    if pedal_pressed:
                        # ===== BRAKE TEST SIMULATION =====
                        brake_timer += dt
                        self.v_registers[4] = int(brake_timer * 100)  # V4: Braking time x100
                        
                        # Braking force ramps up to ~1150 N with slight noise
                        target_force = 1150 + random.uniform(-20, 20)
                        current_force = min(target_force, self.v_registers[3] + 180)
                        self.v_registers[3] = int(current_force)

                        # Decelerate roller RPM & speed
                        current_roller_rpm = self.v_registers[2]
                        current_speed = self.v_registers[7]
                        
                        new_roller_rpm = max(0, int(current_roller_rpm - 140))
                        new_speed = max(0, int(current_speed - 35))
                        
                        self.v_registers[2] = new_roller_rpm
                        self.v_registers[7] = new_speed

                        # When stopped, hold values and auto-stop
                        if new_roller_rpm == 0 and new_speed == 0 and brake_timer > 0.5:
                            self.coils[0] = False
                            self.coils[1] = False
                            self.v_registers[10] = 1
                    else:
                        # ===== DYNO ACCELERATION SIMULATION =====
                        brake_timer = 0.0
                        self.v_registers[4] = 0
                        self.v_registers[3] = 0
                        # Keep roller spun up for brake test prep
                        self.v_registers[2] = 2500

                        # Progress along dyno pull curve (0.0 to 1.0)
                        self.dyno_progress += dt * 0.15  # ~6.5 seconds pull
                        if self.dyno_progress >= 1.0:
                            self.dyno_progress = 1.0
                            self.coils[0] = False  # Auto stop at top
                            self.v_registers[10] = 1

                        p = self.dyno_progress
                        # Engine RPM: 1500 -> 10500 RPM
                        sim_rpm = 1500 + int(9000 * (p ** 1.3)) + random.randint(-15, 15)
                        self.v_registers[0] = max(0, min(15000, sim_rpm))

                        # Dyno Torque: Curve peaks around 6500 RPM (p ~ 0.55) at ~18.5 Nm
                        torque_peak = 18.8
                        torque_val = 11.0 + (torque_peak - 11.0) * math.exp(-((p - 0.55) ** 2) / 0.12)
                        torque_val += random.uniform(-0.15, 0.15)
                        self.v_registers[1] = int(torque_val * 10)  # V1: Torque x10

                        # Speed: 0 -> 125 km/h
                        sim_speed = int(1250 * p)  # V7: Speed x10
                        self.v_registers[7] = sim_speed

                else:
                    # IDLE STATE
                    test_timer = 0.0
                    self.v_registers[10] = 1  # Idle
                    # Decay RPM back to idle (1500 RPM)
                    current_rpm = self.v_registers[0]
                    if current_rpm > 1500:
                        self.v_registers[0] = max(1500, int(current_rpm - 300))
                    elif current_rpm < 1500 and current_rpm > 0:
                        self.v_registers[0] = 1500

                    # Zero torque and speed decay
                    if self.v_registers[1] > 0:
                        self.v_registers[1] = max(0, self.v_registers[1] - 20)
                    if self.v_registers[7] > 0:
                        self.v_registers[7] = max(0, self.v_registers[7] - 50)

                # Lux with realistic slight lamp flicker
                self.v_registers[5] = int(14500 + random.randint(-50, 50))

            time.sleep(dt)

    def _run_server_loop(self):
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                client_t = threading.Thread(target=self._handle_client, args=(conn, addr), daemon=True)
                client_t.start()
            except socket.timeout:
                continue
            except Exception:
                break

    def _handle_client(self, conn: socket.socket, addr):
        while self.running:
            try:
                data = conn.recv(260)
                if not data or len(data) < 12:
                    break

                tx_id, proto, length, unit, fc = struct.unpack('>HHHBB', data[:8])

                with self._lock:
                    if fc == 3:  # Read Holding Registers
                        start_addr, count = struct.unpack('>HH', data[8:12])
                        vals = self.v_registers[start_addr : start_addr + count]
                        payload = struct.pack(f'>BBB{count}H', unit, fc, count * 2, *vals)
                        header = struct.pack('>HHH', tx_id, proto, len(payload))
                        conn.sendall(header + payload)

                    elif fc == 1:  # Read Coils
                        start_addr, count = struct.unpack('>HH', data[8:12])
                        byte_count = (count + 7) // 8
                        byte_vals = [0] * byte_count
                        for i in range(count):
                            if self.coils[start_addr + i]:
                                byte_vals[i // 8] |= (1 << (i % 8))
                        payload = struct.pack(f'>BBB{byte_count}B', unit, fc, byte_count, *byte_vals)
                        header = struct.pack('>HHH', tx_id, proto, len(payload))
                        conn.sendall(header + payload)

                    elif fc == 6:  # Write Single Register
                        addr, val = struct.unpack('>HH', data[8:12])
                        self.v_registers[addr] = val
                        conn.sendall(data)

                    elif fc == 5:  # Write Single Coil
                        addr, val = struct.unpack('>HH', data[8:12])
                        self.coils[addr] = (val == 0xFF00)
                        conn.sendall(data)

                    else:
                        payload = struct.pack('>BBB', unit, fc | 0x80, 0x01)
                        header = struct.pack('>HHH', tx_id, proto, len(payload))
                        conn.sendall(header + payload)

            except (ConnectionResetError, ConnectionAbortedError, socket.timeout):
                break
            except Exception:
                break
        conn.close()
