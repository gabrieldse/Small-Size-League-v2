import time
import serial

FWD = 0
BWD = 1
tx_port = "/tmp/ttyV0"

class RadioSender():
    def __init__(self, robot_id=3, port="/dev/ttyACM2", baudrate=115200):
        self.robot_id = robot_id
        self.packet_size = 10
        self.serial = serial.Serial(port, baudrate, timeout=1)

    def build_packet(self, m1, m1_dir, m2, m2_dir, m3, m3_dir, m4, m4_dir, kicker):
        
        # Headers
        packet = bytearray([0xAA, 0x55])
        tail = 0xFF
        packet.append(self.robot_id)
        
        # Validate motor speeds and directions
        m1 = max(0, min(255, int(m1)))
        m1_dir = 1 if m1_dir else 0
        m2 = max(0, min(255, int(m2)))
        m2_dir = 1 if m2_dir else 0
        m3 = max(0, min(255, int(m3)))
        m3_dir = 1 if m3_dir else 0
        m4 = max(0, min(255, int(m4)))
        m4_dir = 1 if m4_dir else 0
        kicker = 1 if kicker else 0

        data = [m1, m1_dir, m2, m2_dir, m3, m3_dir, m4, m4_dir, kicker]
        for value in data:
            packet.append(value)
    
        # Calculate checksum
        checksum = sum(data) % 256
        packet.append(checksum)
        packet.append(tail)
        return packet

    def send_command(self, m1, m1_dir, m2, m2_dir, m3, m3_dir, m4, m4_dir, kicker):
        packet = self.build_packet(m1, m1_dir, m2, m2_dir, m3, m3_dir, m4, m4_dir, kicker)
        print(list(packet))
        self.send_packet(packet)

    def send_packet(self, packet: bytearray):
        self.serial.write(packet)
        self.serial.flush()

    def motor_test(self, motors, direction=FWD, speed=250, kicker=False):
        """
        Returns a command tuple for a single motor or multiple motors.
        
        motor: str ("fl", "fr", "bl", "br") ou int (1=fl,2=fr,3=bl,4=br)
        direction: 0=forward, 1=backward
        speed: motor speed 0-255
        kicker: True/False
        """
        cmd = [0,0,0,0,0,0,0,0,kicker]
        motor_map = {
            "fl": (0,1), 1: (0,1),
            "fr": (2,3), 3: (2,3),
            "bl": (4,5), 2: (4,5),
            "br": (6,7), 4: (6,7)
        }
        if not isinstance(motors, list):
            motors = [motors]
        for m in motors:
            if m not in motor_map:
                raise ValueError(f"Invalid motor: {m}")
            idx_speed, idx_dir = motor_map[m]
            cmd[idx_speed] = speed
            cmd[idx_dir] = direction
        return tuple(cmd)
    
    def stop_all_motors(self):
        self.send_command(0,0,0,0,0,0,0,0,False)

if __name__ == "__main__":
    sender = RadioSender()
    robot_id = 3
    sender = RadioSender(robot_id=robot_id)

    # Comandos individuais (m1 = FL, m2 = FR, m3 = BL, m4 = BR)
    m1 = [200, 0, 0, 0, 0, 0, 0, 0, False]  # FL
    m2 = [0, 0, 200, 0, 0, 0, 0, 0, False]  # FR
    m3 = [0, 0, 0, 0, 200, 0, 0, 0, False]  # BL
    m4 = [0, 0, 0, 0, 0, 0, 200, 0, False]  # BR

    # Comando para todos os motores juntos
    all_motors = [250, FWD, 250, FWD, 250, FWD, 250, FWD, False]
    backwards = [250, BWD, 250, BWD, 250, BWD, 250, BWD, False]
    frontwards = [250, FWD, 250, FWD, 250, FWD, 250, FWD,False]
    r_rotation = [250, BWD, 250, FWD, 250, BWD, 250, FWD, True] 
    l_rotation = [250, FWD, 250, BWD, 250, FWD, 250, BWD, True]
    chutar = [0, 0, 0, 0, 0, 0, 0, 0, True]
    # Intervalo entre comandos (em segundos)
    delay = 2.0

    print("Iniciando teste contínuo dos motores... (Ctrl+C para parar)")
    try:
        while True:
            sender.send_command(*l_rotation)

    except KeyboardInterrupt:
        print("\nTeste interrompido pelo usuário.")
    except Exception as e:
        print(f"\nOcorreu um erro durante o teste: {e}")
        
