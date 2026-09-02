# API Documentation: Modbus PLC & Internal Services

> Last updated: 2026-08-31  
> Protocol: Modbus TCP (Port 502 / Slave Unit ID 1)  
> Internal Interface: Python PyQt6 Signals & Service Contracts

---

## 1. Modbus TCP Register Map (Hardware Contract)

### A. Holding Registers (Read: FC 03 / Write: FC 06)

| Address (Offset) | Register PLC | Tipe Data | Skala | Rentang Nilai | Satuan | Keterangan |
|---|---|---|---|---|---|---|
| `0` | `V0` | `UINT16` | $\times 1$ | 0 – 15,000 | RPM | **RPM Mesin / Dyno Roller** |
| `1` | `V1` | `INT16` | $\times 0.1$ | 0 – 2,000.0 | Nm | **Torsi Dyno** (dibagi 10 untuk nilai riil) |
| `2` | `V2` | `UINT16` | $\times 1$ | 0 – 5,000 | RPM | **RPM Roller Brake Test** |
| `3` | `V3` | `UINT16` | $\times 1$ | 0 – 20,000 | N | **Gaya Pengereman (Braking Force)** |
| `4` | `V4` | `UINT16` | $\times 0.01$ | 0 – 60.00 | Detik | **Braking Time (Waktu Rem)** |
| `5` | `V5` | `UINT16` | $\times 1$ | 0 – 65,535 | Lux | **Intensitas Cahaya Lampu Utama** |
| `6` | `V6` | `UINT16` | $\times 1$ | 0 – 3,600 | Detik | **Running Time Pengujian** |
| `7` | `V7` | `UINT16` | $\times 0.1$ | 0 – 200.0 | km/jam | **Kecepatan Linier Roller** |
| `10` | `V10`| `UINT16` | $\times 1$ | 0 – 100 | Code | **Status Kode PLC** (1=Idle, 2=Running, 9=Error) |

### B. Coils / Discrete Flags (Read: FC 01 / Write: FC 05)

| Address (Offset) | Bit PLC | Tipe Data | Arah | Keterangan |
|---|---|---|---|---|
| `0` | `M0` | `BOOL` | R/W | **Trigger Start Test** (1 = Mulai Sampling / Run, 0 = Stop) |
| `1` | `M1` | `BOOL` | R/W | **Status Sensor Pedal Rem** (1 = Pedal Terinjak, 0 = Lepas) |
| `2` | `M2` | `BOOL` | Write | **Tare / Zero Calibration** (1 = Reset Beban Nol Sensor) |
| `3` | `M3` | `BOOL` | Read | **Interlock / Safety Guard** (1 = Aman, 0 = E-Stop Aktif) |

---

## 2. Internal Service Contracts & Qt Signals

### A. `ModbusWorker` Thread Contract
```python
class ModbusWorker(QThread):
    # Signals terpancar ke UI
    data_received = pyqtSignal(dict)       # Payload dict berisi {v0, v1, v2, v3, v4, v5, v6, v7, m0, m1}
    connection_status = pyqtSignal(bool, str) # (is_connected, status_message)
    error_occurred = pyqtSignal(str)       # Pesan error komunikasi
    
    # Public Methods
    def connect_plc(self, ip: str, port: int) -> bool: ...
    def disconnect_plc(self) -> None: ...
    def set_start_trigger(self, state: bool) -> bool: ...
    def set_tare_sensor(self) -> bool: ...
```

### B. `DatabaseRepository` Contract
```python
class DatabaseRepository:
    def get_vehicle_by_vin_or_test_no(self, query: str) -> Optional[dict]: ...
    def save_vehicle(self, vehicle_data: dict) -> bool: ...
    def create_test_session(self, session_data: dict) -> int: ...
    def save_dyno_result(self, dyno_data: dict) -> bool: ...
    def save_brake_result(self, brake_data: dict) -> bool: ...
    def get_recent_sessions(self, limit: int = 10) -> List[dict]: ...
```

### C. `ExportService` Contract
```python
class ExportService:
    def print_thermal_receipt(self, session_id: int, printer_name: Optional[str] = None) -> bool: ...
    def export_pdf_report(self, session_id: int, output_path: str) -> bool: ...
    def export_excel_report(self, session_id: int, output_path: str) -> bool: ...
```
