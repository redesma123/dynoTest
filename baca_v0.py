from pymodbus.client import ModbusTcpClient
import time

PLC_IP = "127.0.0.1"  # Localhost (ing 1 komputer)
PLC_PORT = 502

client = ModbusTcpClient(PLC_IP, port=PLC_PORT)

if not client.connect():
    print(f"[GAGAL] Ora iso nyambung menyang {PLC_IP}:{PLC_PORT}")
    print("Pastikne server_plc_device_a.py wis di-run dhisik minangka Administrator.")
    exit(1)

print(f"[BERHASIL] Nyambung menyang PLC ing {PLC_IP}:{PLC_PORT}. Maca V0...\n")

try:
    while True:
        # Maca Holding Register V0 (address 0)
        response = client.read_holding_registers(address=0, count=1)

        if not response.isError():
            nilai_v0 = response.registers[0]
            print(f"Nilai V0 saat ini = {nilai_v0}")
        else:
            print(f"Gagal maca register: {response}")

        time.sleep(0.5)  # Interval maca saben 0.5 detik

except KeyboardInterrupt:
    print("\nProgram pembaca dihentikan.")
finally:
    client.close()