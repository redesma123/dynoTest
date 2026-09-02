"""
Modbus TCP Client Driver for Haiwell PLC / Digital Twin Simulator.
Reads registers, converts raw telemetry with proper scaling, and controls coils.
"""
import socket
import struct
import time
from typing import Dict, Any, Optional, Tuple


class ModbusDriver:
    def __init__(self, host: str = "127.0.0.1", port: int = 5020, unit_id: int = 1, timeout: float = 1.0):
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.timeout = timeout
        self.sock: Optional[socket.socket] = None
        self.is_connected = False
        self._tx_id = 0

    def connect(self) -> bool:
        """Establishes TCP connection to PLC."""
        try:
            self.disconnect()
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.host, self.port))
            self.is_connected = True
            return True
        except Exception as e:
            self.is_connected = False
            self.sock = None
            return False

    def disconnect(self):
        """Closes socket safely."""
        self.is_connected = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

    def read_holding_registers(self, start_addr: int = 0, count: int = 11) -> Optional[Tuple[int, ...]]:
        """Reads V-registers (FC 03)."""
        if not self.is_connected and not self.connect():
            return None

        self._tx_id = (self._tx_id + 1) % 65535
        # MBAP (7 bytes) + FC3 PDU (5 bytes)
        # TxID (2B), Proto (2B)=0, Length (2B)=6, UnitID (1B)=1, FC (1B)=3, StartAddr (2B), Count (2B)
        request = struct.pack('>HHHBBHH', self._tx_id, 0, 6, self.unit_id, 3, start_addr, count)

        try:
            self.sock.sendall(request)
            header = self._recv_exact(7)
            if not header or len(header) < 7:
                self.disconnect()
                return None

            rx_tx, rx_proto, rx_len, rx_unit = struct.unpack('>HHHB', header)
            pdu = self._recv_exact(rx_len - 1)
            if not pdu or len(pdu) < 2:
                self.disconnect()
                return None

            fc = pdu[0]
            if fc != 3:  # Modbus Exception
                return None

            byte_count = pdu[1]
            register_values = struct.unpack(f'>{count}H', pdu[2 : 2 + byte_count])
            return register_values
        except Exception:
            self.disconnect()
            return None

    def read_coils(self, start_addr: int = 0, count: int = 4) -> Optional[Tuple[bool, ...]]:
        """Reads M-coils (FC 01)."""
        if not self.is_connected and not self.connect():
            return None

        self._tx_id = (self._tx_id + 1) % 65535
        request = struct.pack('>HHHBBHH', self._tx_id, 0, 6, self.unit_id, 1, start_addr, count)

        try:
            self.sock.sendall(request)
            header = self._recv_exact(7)
            if not header or len(header) < 7:
                self.disconnect()
                return None

            rx_tx, rx_proto, rx_len, rx_unit = struct.unpack('>HHHB', header)
            pdu = self._recv_exact(rx_len - 1)
            if not pdu or len(pdu) < 2:
                self.disconnect()
                return None

            fc = pdu[0]
            if fc != 1:
                return None

            byte_count = pdu[1]
            byte_vals = pdu[2 : 2 + byte_count]
            coils = []
            for i in range(count):
                bit = (byte_vals[i // 8] >> (i % 8)) & 1
                coils.append(bool(bit))
            return tuple(coils)
        except Exception:
            self.disconnect()
            return None

    def write_single_coil(self, addr: int, state: bool) -> bool:
        """Writes single M-coil (FC 05)."""
        if not self.is_connected and not self.connect():
            return False

        self._tx_id = (self._tx_id + 1) % 65535
        val = 0xFF00 if state else 0x0000
        request = struct.pack('>HHHBBHH', self._tx_id, 0, 6, self.unit_id, 5, addr, val)

        try:
            self.sock.sendall(request)
            response = self._recv_exact(12)
            return len(response) == 12
        except Exception:
            self.disconnect()
            return False

    def read_all_telemetry(self) -> Optional[Dict[str, Any]]:
        """
        Reads and maps all registers & coils with real engineering units.
        Returns None on communication failure.
        """
        v_regs = self.read_holding_registers(0, 11)
        coils = self.read_coils(0, 4)

        if v_regs is None or coils is None:
            return None

        # V1 is INT16 (signed torque)
        raw_torque = v_regs[1]
        if raw_torque >= 32768:
            raw_torque -= 65536

        return {
            "engine_rpm": v_regs[0],
            "dyno_torque_nm": round(raw_torque / 10.0, 2),
            "roller_rpm": v_regs[2],
            "braking_force_n": v_regs[3],
            "braking_time_s": round(v_regs[4] / 100.0, 2),
            "lux_intensity": v_regs[5],
            "running_time_s": v_regs[6],
            "speed_kmh": round(v_regs[7] / 10.0, 1),
            "status_code": v_regs[10],
            "is_test_active": coils[0],
            "is_pedal_pressed": coils[1],
            "is_safety_ok": coils[3]
        }

    def set_start_trigger(self, state: bool) -> bool:
        return self.write_single_coil(0, state)

    def set_brake_pedal(self, state: bool) -> bool:
        return self.write_single_coil(1, state)

    def set_tare_sensor(self) -> bool:
        return self.write_single_coil(2, True)

    def _recv_exact(self, num_bytes: int) -> bytes:
        buf = b''
        while len(buf) < num_bytes:
            chunk = self.sock.recv(num_bytes - len(buf))
            if not chunk:
                break
            buf += chunk
        return buf
