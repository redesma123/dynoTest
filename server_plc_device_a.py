import socket
import struct
import threading
import time

# Alokasi register internal PLC Haiwell:
# V-Registers (Holding Registers) 0 - 99
v_registers = [0] * 100
# M-Bits / Y-Bits (Coils) 0 - 99
coils = [False] * 100

def simulasi_ladder_ctu():
    """Simulasi ladder CTU: Increment V0 setiap 1 detik"""
    v0 = 0
    while True:
        time.sleep(1)
        v0 = (v0 + 1) % 10000
        v_registers[0] = v0
        print(f"[PLC SIMULATOR DEVICE A] Nilai V0 diupdate ke -> {v0}")

def handle_client(conn, addr):
    while True:
        try:
            # Baca Header Modbus TCP (MBAP Header = 6 byte) + PDU
            data = conn.recv(260)
            if not data or len(data) < 12:
                break
            
            # Format MBAP Header: TransactionID (2B), ProtocolID (2B), Length (2B), UnitID (1B), FC (1B)
            tx_id, proto, length, unit, fc = struct.unpack('>HHHBB', data[:8])
            
            if fc == 3:  # Read Holding Registers (V-Registers)
                start_addr, count = struct.unpack('>HH', data[8:12])
                vals = v_registers[start_addr : start_addr + count]
                payload = struct.pack(f'>BBB{count}H', unit, fc, count * 2, *vals)
                header = struct.pack('>HHH', tx_id, proto, len(payload))
                conn.sendall(header + payload)

            elif fc == 1:  # Read Coils (M/Y Bits)
                start_addr, count = struct.unpack('>HH', data[8:12])
                # pack bits into bytes
                byte_count = (count + 7) // 8
                byte_vals = [0] * byte_count
                for i in range(count):
                    if coils[start_addr + i]:
                        byte_vals[i // 8] |= (1 << (i % 8))
                payload = struct.pack(f'>BBB{byte_count}B', unit, fc, byte_count, *byte_vals)
                header = struct.pack('>HHH', tx_id, proto, len(payload))
                conn.sendall(header + payload)

            elif fc == 6:  # Write Single Register
                addr, val = struct.unpack('>HH', data[8:12])
                v_registers[addr] = val
                conn.sendall(data)  # Echo response

            elif fc == 5:  # Write Single Coil
                addr, val = struct.unpack('>HH', data[8:12])
                coils[addr] = (val == 0xFF00)
                conn.sendall(data)  # Echo response

            else:
                # Modbus Exception: Illegal Function
                payload = struct.pack('>BBB', unit, fc | 0x80, 0x01)
                header = struct.pack('>HHH', tx_id, proto, len(payload))
                conn.sendall(header + payload)

        except ConnectionResetError:
            break
        except Exception as e:
            break
    conn.close()

def main():
    HOST = '0.0.0.0'
    PORT = 502

    # Jalankan background counter CTU
    t_sim = threading.Thread(target=simulasi_ladder_ctu, daemon=True)
    t_sim.start()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((HOST, PORT))
    except PermissionError:
        print("\n[ERROR] Port 502 butuh Administrator. Jalankan CMD / Terminal sebagai Administrator.")
        return
    except OSError as e:
        print(f"\n[ERROR] Gagal bind port 502: {e}")
        return

    server.listen(10)
    print("==================================================")
    print(f"  SIMULATOR PLC MODBUS TCP AKTIF DI PORT {PORT}    ")
    print("  Status: RUNNING (Menunggu koneksi client...)    ")
    print("==================================================")

    try:
        while True:
            conn, addr = server.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            client_thread.start()
    except KeyboardInterrupt:
        print("\n[INFO] Simulator PLC dihentikan.")
    finally:
        server.close()

if __name__ == '__main__':
    main()