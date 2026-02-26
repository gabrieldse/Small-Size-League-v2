import socket

from sender.Robot_sender import FWD, RobotSender

# FWD = 0
BWD = 1


class UdpSender(RobotSender):
    def __init__(self, robot_ip, robot_port):
        super().__init__()
        self.robot_ip = robot_ip
        self.robot_port = robot_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.packet_size = 9

        print(
            f"UdpSender configurado para enviar para {self.robot_ip}:{self.robot_port}"
        )

    def send_command(self, fl_s, fl_d, bl_s, bl_d, fr_s, fr_d, br_s, br_d, kicker):
        packet = self.build_packet(
            fl_s, fl_d, bl_s, bl_d, fr_s, fr_d, br_s, br_d, kicker
        )
        self.send_packet(packet)

    def send_packet(self, packet: bytearray):
        try:
            self.sock.sendto(packet, (self.robot_ip, self.robot_port))
            print(
                f"Pacote enviado para {self.robot_ip}:{self.robot_port}: {packet.hex()}"
            )
        except Exception as e:
            print(
                f"Erro ao enviar pacote UDP para {self.robot_ip}:{self.robot_port}: {e}"
            )


if __name__ == "__main__":
    import time

    ROBOT_TEST_IP = "192.168.0.101"
    ROBOT_TEST_PORT = 8080

    sender_test = UdpSender(ROBOT_TEST_IP, ROBOT_TEST_PORT)
    print(f"\nIniciando teste de envio UDP para {ROBOT_TEST_IP}:{ROBOT_TEST_PORT}")
    print("Verifique a saída serial do seu ESP32 para confirmar o recebimento.")

    try:
        print("\nTeste 1: Mover todas as rodas para frente")
        cmd = sender_test.motor_test([1, 2, 3, 4], FWD)
        sender_test.send_command(*cmd)  # <- aqui desempacota a tupla

        time.sleep(10)
        print("\nDesativando todas as rodas")
        cmd = sender_test.motor_test([1, 2, 3, 4], FWD, speed=0)
        sender_test.send_command(*cmd)
        time.sleep(2)

        print("\nTeste 2: Mover todas as rodas para trás")
        cmd = sender_test.motor_test([1, 2, 3, 4], BWD)
        sender_test.send_command(*cmd)  # <- aqui desempacota a tupla
        time.sleep(10)

        print("\nDesativando todas as rodas")
        cmd = sender_test.motor_test([1, 2, 3, 4], FWD, speed=0)
        sender_test.send_command(*cmd)
        time.sleep(2)
    except KeyboardInterrupt:
        print("\nTeste interrompido pelo usuário.")
    except Exception as e:
        print(f"\nOcorreu um erro durante o teste: {e}")
    finally:
        print("\nTeste do UdpSender concluído.")
